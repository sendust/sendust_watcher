#  Watch and transcode XDCAM50 MXF with 8ch audio
#  Collaborate with SBS sendAnywhere, SBS NDS
#  Code managed by sendust..
#
#  2023/1/15    Introduce Queue. worker 1, 2
#  


from sendustlogger import updatelog
from sendustparser import argparser
import os, time, glob, queue, threading
from param_processor import param_processor
import subprocess, shutil
import xml.etree.ElementTree as ET

class timer:
    def __init__(self, period_in_sec):
        self.interval = period_in_sec
        self.tm_start = time.time()
    
    def run(self):
        if (time.time() - self.tm_start) > self.interval:
            self.tm_start = time.time()
            return True
        else:
            return False
    
    def reset(self):
        self.tm_start = time.time()


class encoder:
    binary = "ffmpeg.exe"
    metadata = ''
    
    def __init__(self, infile):
        self.infile = infile
    
    def set_mediainfo(self, mediainfo):
        self.mediainfo = mediainfo
        
    def set_target(self, target):
        self.target = target
    
    def set_filter(self, filter):
        self.filter = filter
    
    def set_meta(self, metadata):
        self.metadata = metadata
    
    
    def run(self, str_run, duration = 60):
        updatelog(str_run, True)
        p = subprocess.run(str_run, stderr=subprocess.STDOUT, timeout=float(duration))
        #result = p.stdout.decode()
        ret = p.returncode
        updatelog(f'Encoder finished with return code {ret}', True)
    
    def image(self):
        duration = 10
        str_ffmpeg = f'ffmpeg -i "{self.infile}" -f lavfi -i sine=r=48000 {self.filter};[1:a]pan=7.1|c0=c0|c1=c0|c2=c0|c3=c0|c4=c0|c5=c0|c6=c0|c7=c0[apan];[apan]channelsplit=channel_layout=7.1" -t {duration} -pix_fmt yuv422p -c:v mpeg2video  -profile:v 0 -level:v 2 -b:v 50000k -maxrate 50000k -minrate 50000k -bufsize 17825792 -mpv_flags strict_gop -flags +ildct+ilme+cgop -top 1 -g 15 -bf 2 -color_primaries 1 -color_trc 1 -colorspace 1 -sc_threshold 1000000000 -c:a pcm_s24le -y "{self.target}"'        
        self.run(str_ffmpeg, duration)
        threading.Thread(target=finish_job, args=[self], name="FINISHING").start()
        
    def audio(self):
        duration = self.mediainfo["general"]["Duration"]
        str_ffmpeg = f'ffmpeg -i "{self.infile}"  -f lavfi -i smptehdbars=size=1920x1080:rate=60000/1001 -filter_complex "[1:v]drawbox=color=black@0.4:y=80:width=iw:height=120:t=fill[vbox];[vbox]drawtext=text=SBS_Anywhere_audio_ingest:fontcolor=white:fontsize=100:x=200:y=100{self.filter} -t {duration} -pix_fmt yuv422p -c:v mpeg2video  -profile:v 0 -level:v 2 -b:v 50000k -maxrate 50000k -minrate 50000k -bufsize 17825792 -mpv_flags strict_gop -flags +ildct+ilme+cgop -top 1 -g 15 -bf 2 -color_primaries 1 -color_trc 1 -colorspace 1 -sc_threshold 1000000000 -c:a pcm_s24le -y "{self.target}"'
        self.run(str_ffmpeg, duration)
        threading.Thread(target=finish_job, args=[self], name="FINISHING").start()
        
    def video(self):
        duration =  self.mediainfo["general"]["Duration"]
        str_ffmpeg = f'ffmpeg -i "{self.infile}"  -f lavfi -i sine=r=48000 {self.filter};[1:a]pan=7.1|c0=c0|c1=c0|c2=c0|c3=c0|c4=c0|c5=c0|c6=c0|c7=c0[apan];[apan]channelsplit=channel_layout=7.1" -t {duration} -pix_fmt yuv422p -c:v mpeg2video  -profile:v 0 -level:v 2 -b:v 50000k -maxrate 50000k -minrate 50000k -bufsize 17825792 -mpv_flags strict_gop -flags +ildct+ilme+cgop -top 1 -g 15 -bf 2 -color_primaries 1 -color_trc 1 -colorspace 1 -sc_threshold 1000000000 -c:a pcm_s24le -y "{self.target}"'
        self.run(str_ffmpeg, duration)
        threading.Thread(target=finish_job, args=[self], name="FINISHING").start()
    
    def videoaudio(self):
        duration = self.mediainfo["general"]["Duration"]
        str_ffmpeg = f'ffmpeg -i "{self.infile}" {self.filter} -t {duration} -c:v mpeg2video  -profile:v 0 -level:v 2 -b:v 50000k -maxrate 50000k -minrate 50000k -bufsize 17825792 -mpv_flags strict_gop -flags +ildct+ilme+cgop -top 1 -g 15 -bf 2 -color_primaries 1 -color_trc 1 -colorspace 1 -sc_threshold 1000000000 -c:a pcm_s24le -y "{self.target}"'
        self.run(str_ffmpeg, duration)
        threading.Thread(target=finish_job, args=[self], name="FINISHING").start()

class watchdog:
    def __init__(self, expected_thread_list):
        self.expected_thread_list = expected_thread_list
        self.tmr = ''
   
    def start(self):
        self.tmr = threading.Timer(60, self.start)
        self.tmr.name = "watchdog"
        self.tmr.start()
        updatelog("Watchdog is running ...", True)

        self.list_thread_name = [x.name for x in threading.enumerate()]
        updatelog(self.list_thread_name, True)

        for each in self.expected_thread_list:
            if each not in self.list_thread_name:
                updatelog("Watchdog detect abnormal thread... try to terminate script...", True)
                updatelog(self.list_thread_name, True)
                do_gracefully_finish()
                exit()

    def stop(self):
        updatelog("Finish watchdog timer...", True)
        self.tmr.cancel()


def do_gracefully_finish():
    global wg, loop_main, loop_encoder
    loop_main = False
    loop_encoder = False
    wg.stop()


def display_time(sec):
    second = int(sec)
    ms = str((sec - second) * 100)
    ms = ms[:2]
    w = second // 604800
    second -= w * 604800
    d = second // 86400
    second -= d * 86400
    h = second // 3600
    second -= h * 3600
    m = second // 60
    second -= m * 60
    second = str(second) + "." + ms
    return f'{w}w {d}d {h}h {m}m {second}s'


def get_age(path):
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
    #print(f'{path} of property atime mtime ctime = {atime} {mtime} {ctime}')
    return time.time() - mtime


def smart_move_backup(origin, target): # Check target existence and rename origin while move
    (head, tail) = os.path.split(origin)      # Get file name only
    target_full = os.path.join(target, tail)
    while os.path.isfile(target_full):
        (head, tail) = os.path.split(target_full)
        (filename, extension) = os.path.splitext(tail)
        filename = filename + "_"
        filename_full = filename + extension
        target_full = os.path.join(target, filename_full)
    
    updatelog(f'Try to move file... {origin}', True)
    try:    
        os.replace(origin, target_full)
    except Exception as e:
        updatelog(f'Fail to move file..  {origin}', True)
        updatelog(e, True)


def smart_move(origin, target): # Check target existence and rename origin while move
    (head, tail) = os.path.split(origin)      # Get file name only
    (name_only, extension) = os.path.splitext(tail)
    tag_time = str(time.time()).split('.')
    tag_time[1] = tag_time[1] + '00000000'
    tag_new = '_' + tag_time[0][-4:] + '(' + tag_time[1][:4] + ')'
    taget_nameonly = name_only + tag_new + extension
    updatelog(f'Try to move file... {origin}  ==> {target}', True)
    try:    
        #os.replace(origin, os.path.join(target, taget_nameonly))
        shutil.move(origin, os.path.join(target, taget_nameonly))
        return os.path.join(target, taget_nameonly)
    except Exception as e:
        updatelog(f'Fail to move file..  {origin}', True)
        updatelog(e, True)
        return f'Fail to smart_move {origin}'

def safe_move(origin,target):
    (head, tail) = os.path.split(origin)
    updatelog(f'Try to move file... {origin}  ==> {target}', True)
    try:
        #os.replace(origin, os.path.join(target, tail))
        shutil.move(origin, os.path.join(target, tail))
    except Exception as e:
        print(e)

def get_filelist(path):
    pattern = os.path.join(path, "*")
    #print("Glob pattern is  " + pattern)
    flist = glob.glob(pattern)
    for each in flist:
        if os.path.isdir(each):
            flist.remove(each)
    return flist


def get_mxffilename(source, outputpath):
    (head, tail) = os.path.split(source)
    name, extension = os.path.splitext(tail)
    return os.path.join(outputpath, name + ".mxf")
    
def get_xmlfilename(source, outputpath):
    (head, tail) = os.path.split(source)
    name, extension = os.path.splitext(tail)
    return os.path.join(outputpath, name + ".xml")


def get_proxyfilename(source, outputpath):
    (head, tail) = os.path.split(source)
    name, extension = os.path.splitext(tail)
    outputpath = os.path.join(outputpath, name)
    
    try:
        os.mkdir(outputpath)
    except Exception as e:
        updatelog(e, True)
    
    return os.path.join(outputpath, name + ".mp4")


def get_catafilename(source, outputpath):
    (head, tail) = os.path.split(source)
    name, extension = os.path.splitext(tail)
    outputpath = os.path.join(outputpath, name)
    filename_cata = os.path.join(outputpath, f'{name}_%08d.jpg')
    filename_cata1 = os.path.join(outputpath, f'{name}_00000000.jpg')

    #try:
    #    os.mkdir(outputpath)
    #except Exception as e:
    #    updatelog(e, True)
    
    return filename_cata, filename_cata1



def get_imagemagickmeta(source):
    binary = os.path.join(os.getcwd(), 'imagemagick\\identify.exe')
    p=subprocess.run(f'{binary} -verbose "{source}"', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    result = ''
    for eachline in p.stdout.split(b"\n"):
        try:
            linedecode = eachline.strip().decode('cp949')
        except Exception as e:
            updatelog(e, True)
            try:
                linedecode = eachline.strip().decode('utf8')
            except Exception as e:
                updatelog(e, True)
                try:
                    linedecode = eachline.strip().decode('ascii')
                except Exception as e:
                    linedecode = ''
                    updatelog(e, True)
        result += linedecode + "\n"    
    #updatelog(result, True)
    return result

def get_exiftoolmeta(source):
    binary = os.path.join(os.getcwd(), 'exiftool\\exiftool.exe')
    p=subprocess.run(f'{binary} -charset UTF8 -t "{source}"', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    result = ''
    for eachline in p.stdout.split(b"\n"):
        try:
            linedecode = eachline.strip().decode('cp949')
        except Exception as e:
            updatelog(e, True)
            try:
                linedecode = eachline.strip().decode('utf8')
            except Exception as e:
                updatelog(e, True)
                try:
                    linedecode = eachline.strip().decode('ascii')
                except Exception as e:
                    linedecode = ''
                    updatelog(e, True)
        result += linedecode + "\n"    

    return result

    

def finish_job(this):
    global args
    f = this.infile
    size = 0
    filename_mxf = get_mxffilename(f, args.finishfolder)
    filename_xml = get_xmlfilename(f, args.finishfolder)
    filename_proxy = get_proxyfilename(f, args.finishfolder)
    filename_cata, filename_cata1 = get_catafilename(f, args.finishfolder)

    
    updatelog(f'proxy file path is {filename_proxy}', True)
    updatelog(f'catalog file path is {filename_cata}', True)
    
    
    try:
        file_stats = os.stat(filename_mxf)
        size = file_stats.st_size
    except Exception as e:
        updatelog(f'Error processing file... {filename_mxf}')
    
    updatelog(f'File size is {size}')
    
    
           
    root = ET.Element("SBS_MAM_Job_List")
    job = ET.SubElement(root, "SBS_MAM_Job")

    ET.SubElement(job, "Job_Creation_Time").text = str(int(time.time()))
    ET.SubElement(job, "Job_Type").text = "71"
    
    ET.SubElement(job, "Job_Src_ID").text = "reserved.."
    ET.SubElement(job, "Job_Src_Path_HR_Abs").text = filename_mxf
    ET.SubElement(job, "Job_Src_Path_LR_Abs").text = filename_proxy
    ET.SubElement(job, "Job_Src_Path_CAT_Abs").text = filename_cata1

    
    len_target = len(args.finishfolder)
    ET.SubElement(job, "Job_Src_Path_HR").text = filename_mxf[len_target:]
    ET.SubElement(job, "Job_Src_Path_LR").text = filename_proxy[len_target:]
    ET.SubElement(job, "Job_Src_Path_CAT").text = filename_cata1[len_target:]

    #ET.SubElement(job, "Job_Src_Path_AUDIO").text = this.outputfiles["aud"][len_target:]
    
    ET.SubElement(job, "Job_Dest_Path").text = '//nds/storage/sendanywhere'
    ET.SubElement(job, "Job_Dest_Filename").text = '//nds/storage/sendanywhere'

    ET.SubElement(job, "Job_OBJ_CATEGORY_ID").text = "reserved...."
    ET.SubElement(job, "Job_OBJ_CATEGORY_DESC").text = "reserved...."


    appdata = ET.SubElement(job, "Job_Src_App_Data")
    meta = ET.SubElement(appdata, 'Metadata')
    meta.tail = None


    for l in this.metadata.split('\n'):
        br = ET.SubElement(meta, 'br')
        br.tail = l.strip()

    len_watch = len(args.movefolder)
    ET.SubElement(appdata, "OBJ_Origin_Abs").text = f
    ET.SubElement(appdata, "OBJ_Origin").text = f[len_watch:]
    
    duration = "10"
    try:
        duration = str(this.mediainfo["general"]["Duration"])
    except:
        updatelog(f'cannot find duration information... set default value..', True)
    ET.SubElement(appdata, "OBJ_Duration").text = duration

    tree = ET.ElementTree(root)
    #ET.indent(tree, '  ')

    
    cmd_proxy = f'{this.binary} -i "{filename_mxf}" -r ntsc -pix_fmt yuv420p -filter_complex [0:v]yadif=0:-1:0[deint];[deint]scale=720:400;amerge=inputs=2 -c:v h264 -preset:v fast -movflags +faststart -g 15 -b:v 2000k -y -c:a aac -b:a 128k  "{filename_proxy}" -nostats'
    cmd_catalog = f'{this.binary} -i "{filename_mxf}" -vf yadif,select=\'isnan(prev_selected_t)+gte(t-prev_selected_t\,10)+gt(scene\,0.2)\',scale=720x400 -vsync 0  -frame_pts 1  -enc_time_base 1/29.97  -y "{filename_cata}" -nostats'
    
 
  
    if (size > 0):
        safe_move(f, args.donefolder)
        updatelog(f'proxy cmd is {cmd_proxy}\n-------  catalog cmd is {cmd_catalog}', True)
        p1 = subprocess.run(cmd_proxy, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=float(duration))
        p2 = subprocess.run(cmd_catalog, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=float(duration))
        updatelog(f'proxy, catalog encoder finished with return value {p1.returncode}  {p2.returncode}')
        updatelog(f'Try to write xml file... {filename_xml}')
        try:
            tree.write(filename_xml, encoding='utf-8', xml_declaration=True)
        except Exception as e:
            updatelog(e, True)
    else:
        safe_move(f, args.errorfolder)

def do_encode():
    global tmr2, loop_second, args
    while loop_second:
        if tmr2.run():
            worklist = get_filelist(args.movefolder)
            for each in worklist:
                updatelog(f'Found new file .. start analysis{each}', True)
                media = param_processor()
                enc = encoder(each)
                enc.set_target(get_mxffilename(each, args.finishfolder))
                enc.set_mediainfo(media.analysis(each)) # Analysis first !!
                enc.set_filter(media.get_filter())  # get filter_complex string
                
                if (media.mediainfo["mediatype"] == "nothing"):
                    updatelog("file is not media type..", True)
                    safe_move(each, args.errorfolder)

                elif (media.mediainfo["mediatype"] == "image"):
                    updatelog("Processing image file...", True)
                    enc.set_filter(media.param_video["picture"])
                    enc.set_meta(get_imagemagickmeta(each))
                    enc.image()

                    
                elif (media.mediainfo["mediatype"] == "audio"):
                    updatelog("Processing audio file...", True)
                    enc.set_filter(media.param_audio[media.mediainfo["audiotype"]])
                    enc.set_meta(get_exiftoolmeta(each))
                    enc.audio()

                    
                elif (media.mediainfo["mediatype"] == "video"):
                    updatelog("Processing video file...", True)
                    enc.set_filter(media.param_video[media.mediainfo["videotype"]])
                    enc.set_meta(get_exiftoolmeta(each))
                    enc.video()

                    
                elif (media.mediainfo["mediatype"] == "videoaudio"):
                    updatelog("Processing video/audio file...", True)
                    enc.set_meta(get_exiftoolmeta(each))
                    enc.videoaudio()
                    
        time.sleep(0.2)
        




def do_encode_new():
    global tmr1, tmr2, loop_encoder, args, queue
    print("Start encoder loop............................")
    while loop_encoder:
        try:
            file_inqueue = ''
            #updatelog("Get from queue...", True)
            file_inqueue = queue.get(timeout=1)
            tmr1.reset()
            #updatelog(f'get file name is {file_inqueue}', True)
        except Exception as e:
            pass

        if not file_inqueue:
            continue
        
        updatelog(f'There new file in queue... {file_inqueue}')
        if os.path.isfile(file_inqueue):
            newfile = smart_move(file_inqueue, args.movefolder)
            updatelog(f'smart move file.. {file_inqueue} ==> {newfile}', True)
            media = param_processor()
            enc = encoder(newfile)
            enc.set_target(get_mxffilename(newfile, args.finishfolder))
            enc.set_mediainfo(media.analysis(newfile)) # Analysis first !!
            enc.set_filter(media.get_filter())  # get filter_complex string
            
            if (media.mediainfo["mediatype"] == "nothing"):
                updatelog("file is not media type..", True)
                safe_move(newfile, args.errorfolder)

            elif (media.mediainfo["mediatype"] == "image"):
                updatelog("Processing image file...", True)
                enc.set_filter(media.param_video["picture"])
                enc.set_meta(get_exiftoolmeta(newfile))
                enc.image()

                
            elif (media.mediainfo["mediatype"] == "audio"):
                updatelog("Processing audio file...", True)
                enc.set_filter(media.param_audio[media.mediainfo["audiotype"]])
                enc.set_meta(get_exiftoolmeta(newfile))
                enc.audio()

                
            elif (media.mediainfo["mediatype"] == "video"):
                updatelog("Processing video file...", True)
                enc.set_filter(media.param_video[media.mediainfo["videotype"]])
                enc.set_meta(get_exiftoolmeta(newfile))
                enc.video()

                
            elif (media.mediainfo["mediatype"] == "videoaudio"):
                updatelog("Processing video/audio file...", True)
                enc.set_meta(get_exiftoolmeta(newfile))
                enc.videoaudio()


updatelog("start application..", True)
args = argparser()
tm_start = time.time()
for k in [args.watchfolder, args.movefolder, args.finishfolder, args.donefolder, args.errorfolder]:
    updatelog(f'check folder {k}', True)
    if not os.path.exists(k):
        updatelog(f'{k} +++ Path not exist !! ERROR !!', True)
        exit()
    else:
        updatelog(f'{k} +++ Path exist !! OK', True)


queue = queue.Queue()
tmr1 = timer(2)
tmr2 = timer(2)
loop_main = True
loop_encoder = True

w1 = threading.Thread(target=do_encode_new, name="encoder1")
w2 = threading.Thread(target=do_encode_new, name="encoder2")
w1.start()
w2.start()

wg = watchdog(["MainThread", "encoder1", "encoder2", "watchdog"])  # Expected thread names...
#wg = watchdog(["MainThread"])  # Expected thread names...
wg.start()


try:
    while loop_main:
        if tmr1.run():
            try:
                for each in get_filelist(args.watchfolder):
                    age = get_age(each)
                    if (age > 10):
                        if each not in list(queue.queue):
                            queue.put(each)
                            updatelog(f'Put new file in queue {each}', True)
                            updatelog(f'queue length = {queue.qsize()}', True)
                    else:
                        print(f'Under aged file... {each}')
            except Exception as e:
                updatelog(e, True)
        print(f'{display_time(time.time() - tm_start)}/Th= {wg.list_thread_name} Qn= {queue.qsize()}', end="\r")
        time.sleep(0.2)

except KeyboardInterrupt:
    do_gracefully_finish()
    
    