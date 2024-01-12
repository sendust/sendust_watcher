title sendust watcher --> watch and transcode NDS
:begin
python watch_transcode.py --watchfolder \\10.10.108.32\share\jin\income --movefolder \\10.10.108.32\share\jin\working --finishfolder \\10.10.108.32\share\jin\output --donefolder \\10.10.108.32\share\jin\done --errorfolder \\10.10.108.32\share\jin\error
timeout /t 5
goto begin

pause

