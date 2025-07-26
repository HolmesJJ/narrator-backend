import os
import sys
import time
import shutil
import subprocess


def extract_mp3(mp4_path):
    dir_path = os.path.dirname(mp4_path)
    mp3_path = os.path.join(dir_path, 'output.mp3')
    cmd = [
        'ffmpeg', '-y',
        '-i', mp4_path,
        '-q:a', '0',
        '-map', '0:a:0',
        '-vn',
        '-acodec', 'libmp3lame',
        mp3_path
    ]
    subprocess.run(cmd, check=True)
    return mp3_path


def copy_mp4(mp4_path):
    dir_path = os.path.dirname(mp4_path)
    dst_path = os.path.join(dir_path, 'output.mp4')
    shutil.copyfile(mp4_path, dst_path)
    return dst_path


def main():
    if len(sys.argv) < 2:
        print('Usage: python test3.py <input.mp4>')
        sys.exit(1)
    mp4_path = sys.argv[1]
    print('test3: start')
    time.sleep(30)
    copied_mp4 = copy_mp4(mp4_path)
    print(f'test3: copied video → {copied_mp4}')
    print(f'test3: extracting audio from {mp4_path}')
    mp3_out = extract_mp3(mp4_path)
    print(f'test3: done → {mp3_out}')


if __name__ == '__main__':
    main()
