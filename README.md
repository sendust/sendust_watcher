"# sendust_watcher" 

## transcode media file into XDCAM50 MXF
### image -> 10 second MXF
### audio -> colorbar + audio MXF
### video -> video + tone audio MXF
### video/audio -> video/audio MXF



How to use
```
python watch_transcode.py  --watchfolder d:\media\income --movefolder d:\media\working --finishfolder d:\media\output --donefolder d:\media\done --errorfolder d:\media\error
```

or edit `start_watch.bat` and run it