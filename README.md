# VideoCompression
Python script for easy bulk video compression with neat output using ffmpeg

# Usage

```
> python compress_video.py  --help
usage: compress_video.py [-h] -f FOLDER [-d DEBUG] [-r RECURSIVE]
                         [-ffmpeg FFMPEG_BIN_PATH] [-c CRF] [-vcodec VCODEC]

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        Folder of videos
  -d DEBUG, --debug DEBUG
                        Display some debug information
  -r RECURSIVE, --recursive RECURSIVE
                        Recursively load videos
  -ffmpeg FFMPEG_BIN_PATH, --ffmpeg_bin_path FFMPEG_BIN_PATH
                        Path containing ffmpeg binaries
  -c CRF, --crf CRF     crf value for ffmpeg
  -vcodec VCODEC, --vcodec VCODEC
                        vcodec value for ffmpeg
```               
