import os
import ffmpy
import glob
import time
import datetime
import atexit
from tqdm import tqdm
import subprocess
import argparse

import platform

from colorama import init, Fore, Style
init(autoreset=True)


class VideoCompression:

    def __init__(self, **kwargs):
        atexit.register(self.onexit)

        prop_defaults = {
            "debug": False,
            "recursive": True,
            "ffmpeg_bin_path": r"C:\ffmpeg\bin",  # dont think there is a default for windows, dont even know if this one works
            "crf": 30,
            "vcodec": "libx264"  # Was faster than x265 on my machine
        }
        
       
        if platform.system() == "Linux":
            prop_defaults["ffmpeg_bin_path"] = "/usr/bin/"

        print("===============OPTIONS===============")
        for (prop, default) in prop_defaults.items():
            value = kwargs.get(prop, default) if kwargs.get(prop) != None else default
            print(f"{prop}: {value}")
            setattr(self, prop, value)
        print("===============OPTIONS===============\n\n")
        
        
        #if platform.system() == "Linux":
            #prop_defaults["ffmpeg_bin_path"] = "/usr/bin/"

        self.g_t1 = time.time()
        self.start_size = 0
        self.compressed_directories = []
        self.videos_compressed = 0
        self.current_output_file = ""

    def compress_video(self, input_name, output_name):
        inp = {input_name: None}
        outp = {output_name: f'-vcodec {self.vcodec} -crf {self.crf}'}

        options = ["-loglevel quiet", "-stats"] if not self.debug else []

        ff = ffmpy.FFmpeg(inputs=inp, outputs=outp, executable=os.path.join(self.ffmpeg_bin_path, "ffmpeg"), global_options=options)

        self.printDebug(f"> Running Command: {ff.cmd}")
        ff.run()

        print(Fore.GREEN + Style.BRIGHT+'[!] Finished compressing Video [!]')
   
    def printDebug(self, text):
        if self.debug:
            print(text)

    def convert_seconds(self, seconds):
        dt = datetime.timedelta(seconds=seconds)
        return str(dt)

    def onexit(self):
        print("--------------------------------------------------------------")
        print(f"Total time elapsed: {self.convert_seconds(time.time()-self.g_t1)}")
        print(f"Total videos compressed: {Style.BRIGHT + Fore.CYAN }{self.videos_compressed}")

        if self.current_output_file != "":
            try:
                os.remove(self.current_output_file)
                print(Fore.RED + f"> Removed unfinished filed: {self.current_output_file}")
            except FileNotFoundError:
                print(Fore.RED + f"Someting went wrong while removing {self.current_output_file}. Please remove the file manually")

        # division by 0 bad
        if self.start_size != 0:
            start_size_mb = self.start_size / 1000000
            end_size = sum([self.size_of_dir(dir) for dir in self.compressed_directories])
            end_size_mb = end_size / 1000000

            total_compression_rate = (end_size / self.start_size) * 100
            print(f"Reduced to: {Style.BRIGHT + Fore.CYAN}{total_compression_rate:.2f}%{Style.RESET_ALL} of original size | "
                  f"[{start_size_mb}mb => {end_size_mb}mb]")

        print("Exit")
        print("--------------------------------------------------------------")

    def load_files(self, rootdir):
        return [filename for filename in glob.iglob(rootdir + '**/**', recursive=self.recursive) if os.path.splitext(filename)[1] == ".mp4" and "compressed" not in filename]

    def get_video_length(self, filename):
        if platform.system() == "Linux":
            ffprobe_path = os.path.join(self.ffmpeg_bin_path, "ffprobe")
        else:
             ffprobe_path = os.path.join(self.ffmpeg_bin_path, "ffprobe.exe")
        
        cmds = [ffprobe_path, "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", filename]
        result = subprocess.run(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return float(result.stdout)

    def size_of_dir(self, rootdir):
        return sum([os.stat(filename).st_size for filename in [filename for filename in glob.iglob(rootdir + '**/**', recursive=self.recursive) if os.path.splitext(filename)[1] == ".mp4"]])

    def compress_dir(self, rootdir):
        self.start_size += self.size_of_dir(rootdir)
        self.compressed_directories.append(rootdir)

        files = self.load_files(rootdir)
        print(f"> Loaded {Style.BRIGHT + Fore.CYAN }'{len(files)}' {Style.RESET_ALL}video files in {Style.BRIGHT + Fore.CYAN }{rootdir}")

        bar = tqdm(total=len(files))

        for i, filename in enumerate(files):
            file_type = os.path.splitext(filename)[1]
            output_name = filename.split(file_type)[0] + "_compressed" + file_type

            if file_type != ".mp4" or os.path.exists(output_name) or "compressed" in filename:
                continue

            file_size = os.path.getsize(filename)
            file_size_mb = (file_size/1000000)

            print("\n--------------------------------------------------------------")
            print(f"> Compressing Video: ({i+1}/{len(filename)}) {Style.BRIGHT + Fore.CYAN + filename} "
                  f"{Style.RESET_ALL}: {file_size_mb}mb : {self.convert_seconds(self.get_video_length(filename))}")
            self.current_output_file = output_name

            t1 = time.time()
            self.compress_video(filename, output_name)
            print("--------------------------------------------------------------")

            self.current_output_file = "" #so it doesnt get deleted

            t2 = time.time()

            print(f"Time elapsed: {self.convert_seconds(t2-t1)}")

            compressed_size = os.path.getsize(output_name)
            compressed_size_mb = compressed_size/1000000
            compression_rate = (compressed_size / file_size) * 100

            print(f"Compression: {Style.BRIGHT + Fore.CYAN }{compression_rate:.2f}% {Style.RESET_ALL}: {compressed_size_mb}mb")
            os.remove(filename)
            print(Fore.GREEN + f"> Removed big ass file: {filename}")

            print("--------------------------------------------------------------\n")

            self.videos_compressed+=1

            bar.update(1)



def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'yep'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'nope'):
        return False
    else:
        return False

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--folder", required=True,
                    help="Folder of videos")

    ap.add_argument("-d", "--debug", default=False, type=str2bool,
                    help="Display some debug information")

    ap.add_argument("-r", "--recursive", default=True, type=str2bool,
                    help="Recursively load videos")

    ap.add_argument("-ffmpeg","--ffmpeg_bin_path", type=str,
                    help="Path containing ffmpeg binaries")

    ap.add_argument("-c", "--crf", default=30, type=int,
                    help="crf value for ffmpeg")

    ap.add_argument("-vcodec", "--vcodec", default="libx264", type=str,
                    help="vcodec value for ffmpeg")

    args = vars(ap.parse_args())
    print(args)
    vc = VideoCompression(**args)
    vc.compress_dir(args["folder"])
