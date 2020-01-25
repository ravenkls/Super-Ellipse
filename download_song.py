import sys
import subprocess
import os

url = sys.argv[1]
name = sys.argv[2]

subprocess.run(f'youtube-dl {url} --format m4a --output temp.m4a')
subprocess.run(f'ffmpeg -i temp.m4a assets/music/{name}.wav')
os.remove('temp.m4a')