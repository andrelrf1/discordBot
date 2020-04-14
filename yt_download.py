from __future__ import unicode_literals
import subprocess
import youtube_dl
import json


def download_yt(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'download_archive': 'downloads.txt',
        'outtmpl': './music_cache/%(title)s.%(ext)s'
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        #     'preferredquality': '128',  # 128, 192
        # }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(url)
        return data['title']


def search(text: str):
    video_json = ''
    command = ['youtube-dl', '-j', f'ytsearch: {text}']
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True).stdout.split()
    for i in result:
        video_json = video_json + i

    video_json = json.loads(video_json)
    return video_json['webpage_url']


if __name__ == '__main__':  # main para teste
    coisa = search('Estamos todos bebados matanza')
    print(coisa)
    down = download_yt(coisa)
    print(down)
