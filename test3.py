import os
import sys
import time
import subprocess


def extract_mp3(mp4_path):
    base, _ = os.path.splitext(mp4_path)
    mp3_path = f'{base}.mp3'
    cmd = ['ffmpeg', '-y', '-i', mp4_path, '-q:a', '0', '-map', 'a', mp3_path]
    subprocess.run(cmd, check=True)
    return mp3_path


def main():
    if len(sys.argv) < 2:
        print('Usage: python test3.py <input.mp4>')
        sys.exit(1)
    mp4_path = sys.argv[1]
    print('test3: start')
    time.sleep(10)
    print(f'test3: extracting audio from {mp4_path}')
    mp3_out = extract_mp3(mp4_path)
    print(f'test3: done → {mp3_out}')


if __name__ == '__main__':
    main()
