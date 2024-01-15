# ffmpeg parameter processor by sendust
# ahk -> python code conversion 
# 2024/1/8
# 

import subprocess, json, os



class param_processor:
    binary = "ffprobe.exe"
    binary2 = "mediainfo.exe"
    result = ""
    param_video = {}
    param_audio = {}
    generator_video = '-f lavfi -i testsrc=size=1920x1080:r=30000/1001'
    generator_audio = '-f lavfi -i sine=f=1000'
    mediainfo = ''
    
    
    def __init__(self):
        self.param_video["default"] = '-filter_complex "[0:v]scale=1920x1080:force_original_aspect_ratio=decrease[vs];[vs]pad=w=1920:h=1080:x=(ow-iw)/2:y=(oh-ih)/2:color=black[vs];[vs]fps=fps=60000/1001[vfps];[vfps]tinterlace=4'
    
        self.param_video["interlace_2997_1920"] = '-filter_complex "[0:v]null'
        self.param_video["interlace_5994_1920"] = '-filter_complex "[0:v]null'
        self.param_video["interlace_2997_1440"] = '-filter_complex "[0:v]scale=1920x1080:interl=1'
        self.param_video["interlace"] = '-filter_complex "[0:v]yadif=mode=send_field:parity=-1:deint=0[vdeint];[vdeint]scale=1920x1080[vsize];[vsize]fps=fps=60000/1001[vfps];[vfps]tinterlace=4'
        self.param_video["picture"] = '-filter_complex "[0:v]scale=1920x1080:force_original_aspect_ratio=decrease[vs];[vs]pad=w=1920:h=1080:x=(ow-iw)/2:y=(oh-ih)/2:color=black[vhd];[vhd]loop=loop=-1:size=1:start=0'
        self.param_video["only_audio"] = '-filter_complex "drawbox=color=black@0.4:y=80:width=iw:height=120:t=fill[vbox];[vbox]drawtext=text="SBS INGEST/AUDIO Playing":fontcolor=white:fontsize=100:x=200:y=100'

        self.param_audio["default"] = ';[0:a]anull"'
        self.param_audio["noaudio"] = '"'
        self.param_audio["1 channels-1"] = ';[0:a]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c0|c2=c0|c3=c0|c4=c0|c5=c0|c6=c0|c7=c0[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["1 channels-2"] = ';amerge=inputs=2[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c0|c3=c1|c4=c0|c5=c1|c6=c0|c7=c1[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["1 channels-4"] = ';amerge=inputs=4[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c0|c5=c1|c6=c2|c7=c3[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["1 channels-8"] = ';amerge=inputs=8[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'            #MXF format
        self.param_audio["1 channels-16"] = ';amerge=inputs=16[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["1 channels-32"] = self.param_audio["1 channels-16"]

        self.param_audio["2 channels-1"] = ';[0:a]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c0|c3=c1|c4=c0|c5=c1|c6=c0|c7=c1[apan];[apan]channelsplit=channel_layout=7.1"'            # Most ordinary media format
        self.param_audio["2 channels-2"] = ';amerge=inputs=2[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c0|c5=c1|c6=c2|c7=c3[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["2 channels-3"] = ';amerge=inputs=3[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c0|c7=c1[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["2 channels-4"] = ';amerge=inputs=4[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["2 channels-5"] = ';amerge=inputs=4[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["2 channels-8"] = ';amerge=inputs=8[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["2 channels-16"] = ';amerge=inputs=16[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'

        self.param_audio["4 channels-1"] = ';[0:a]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["4 channels-2"] = ';amerge=inputs=2[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["5 channels-1"] = ';[0:a]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["6 channels-1"] = ';[0:a]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'                  #MTS camera
        self.param_audio["6 channels-2"] = ';amerge=iputs=2[am];[am]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c7[apan];[apan]channelsplit=channel_layout=7.1"'                  # DVD AC3
        self.param_audio["7 channels-1"] = ';[0:a]aresample=48000[are];[are]pan=7.1|c0=c0|c1=c1|c2=c2|c3=c3|c4=c4|c5=c5|c6=c6|c7=c6|[apan];[apan]channelsplit=channel_layout=7.1"'
        self.param_audio["8 channels-1"] = ';[0:a]aresample=48000[are];[are]channelsplit=channel_layout=7.1"'        # SBS SD DAS Archived format  (Use Decklink 8 channel pure mapping)
        self.param_audio["16 channels-1"] = self.param_audio["8 channels-1"]        # Use Decklink 16 channel pure mapping
        self.param_audio["32 channels-1"] = self.param_audio["8 channels-1"]


    
    def get_filter(self):
        try:
            print(f'video type is {self.mediainfo["videotype"]}')
            print(f'audio type is {self.mediainfo["audiotype"]}')            
            print(f'video filter is {self.param_video[self.mediainfo["videotype"]]}')
            print(f'audio filter is {self.param_audio[self.mediainfo["audiotype"]]}')
            filter = self.param_video[self.mediainfo["videotype"]] + self.param_audio[self.mediainfo["audiotype"]] 
        except Exception as e:
            print(e)
            filter = self.param_video["default"] + self.param_audio["default"]
            print("Error get filter..")
            
        return filter


    def analysis_ffprobe(self, infile):
        p = subprocess.run(f'{self.binary} -show_streams "{infile}" -of json', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #p = subprocess.run(f'{self.binary} -show_format "{infile}"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.result = p.stdout.decode()
        #print(self.result)
        result = json.loads(self.result)
        data = result["streams"]
        print(data)
        print(f'stream count is {len(data)}')
        for each_stream in data:
            if "codec_type" in each_stream:
                print(each_stream["codec_type"])

    def analysis(self, infile):     # New, with Mediainfo CLI
        p = subprocess.run(f'{self.binary2}  --Output=JSON  "{infile}"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.result = p.stdout.decode()
        js = json.loads(self.result)
        #print(js)
        #print("*" * 80)
        type = ""
        mediainfo = {}
        general = {}
        general["VideoCount"] = '0'
        general["AudioCount"] = '0'
        general["ImageCount"] = '0'
        
        image = []
        video = []
        audio = []
        index_video = -1
        index_audio = -1
        index_image = -1
        
        for each_tag in js["media"]["track"]:
            for each in each_tag:
                #print(f'{each}  --> {each_tag[each]}')
                if (each == "@type"):   # type : one of them (General, Video, Audio)
                    type = each_tag[each]
                    
                    if type == "Video":
                        index_video += 1
                        video.append({})
                    if type == "Audio":
                        index_audio += 1
                        audio.append({})
                    if type == "Image":
                        index_image += 1
                        image.append({})
           
                if type == "General":
                    general[each] = each_tag[each] 
                        
                if type == "Video":
                    video[index_video][each] = each_tag[each] 
                
                if type == "Audio":
                    audio[index_audio][each] = each_tag[each] 
                if type == "Image":
                    image[index_image][each] = each_tag[each] 
        
        mediainfo["general"] = general
        mediainfo["video"] = video
        mediainfo["audio"] = audio
        mediainfo["image"] = image
        
        score_image = int(general["ImageCount"])
        score_audio = int(general["AudioCount"])
        score_video = int(general["VideoCount"])
        
        mediatype = "nothing"
        videotype = "default"
        audiotype = "noaudio"
        
        if score_image:
            mediatype = "image"
        if score_audio:
            mediatype = "audio"
        if score_video:
            mediatype = "video"
        if (score_audio * score_video):
            mediatype = "videoaudio"
            

        if ((mediatype == "audio") or (mediatype == "videoaudio")):
            audiotype = mediainfo["audio"][0]["Channels"] + " channels-" + mediainfo["general"]["AudioCount"]

        if ((mediatype == "video") or (mediatype == "videoaudio")):
            try:
                stype = video[0]["ScanType"]
            except:
                stype = ''
            if (stype == "Interlaced"):
                videotype = "interlace"

        
        mediainfo["mediatype"] = mediatype
        mediainfo["videotype"] = videotype
        mediainfo["audiotype"] = audiotype
        
        self.mediainfo = mediainfo
        return mediainfo

    def get_duration(self):
        eachline = self.result.split("\n")
        duration = 0
        for line in eachline:
            if line.startswith("duration="):
                duration = line[9:]
        return float(duration)

    
if __name__ == "__main__":
    param = param_processor()

    #info = param.analysis("E:/코멘타리시스템_영상자료/2014소치/저지연비디오스트리밍_ibc 내부.MP4")
    #info =param.analysis("//jungbi2/여러가지/JINSINWOO/temp/test.png")
    
    import glob
    l = glob.glob("Z:/capture/working/*")
    for each in l:
        print(each)
        if os.path.isdir(each):
            continue
        info = param.analysis(each)
        print(info["mediatype"])
        print(info["general"])
        print(info["video"])
        print(info["audio"])
        print(info["image"])
        print(info["audiotype"])
        print(info["videotype"])
        print(param.get_filter())