import argparse, textwrap


def argparser():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''\
            SBS watch and transcode by sendust  (2024, Media IT)

               Example)  python watch_transcode.py --watchfolder "d:\download" --movefolder "e:\working" --finishfolder "e:\output"
                         
                         For Full help ----
                         python watchfolder.py --help
                '''))

    parser.add_argument("--watchfolder", required=True, type=str, default="c:/temp", help="path for watch folder")
    parser.add_argument("--movefolder", required=True, type=str, default="c:/temp/working", help="transcoder working path")
    parser.add_argument("--finishfolder", required=True, type=str, default="c:/temp/output", help="transcoder target path")
    parser.add_argument("--donefolder", required=True, type=str, default="c:/temp/done", help="path for finished source files")
    parser.add_argument("--errorfolder", required=True, type=str, default="c:/temp/error", help="path for error files")
    parser.add_argument("--timeout", required=False, type=int, default=1800, help="Maximum encoder time(default = 30min)")
    return parser.parse_args()
