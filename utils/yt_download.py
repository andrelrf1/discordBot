from __future__ import unicode_literals
import subprocess
import youtube_dl
import json


class YoutubeDownloader:
    __ydl_opts = None

    def __init__(self, download_folder: str):
        self.ydl_opts = {
            # 'format': 'bestaudio/best',
            'format': 'worstaudio/worst',
            'quiet': True,
            'download_archive': f'{download_folder}/downloads.txt',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s'
        }

    @property
    def ydl_opts(self):
        return self.__ydl_opts

    @ydl_opts.setter
    def ydl_opts(self, opts: dict):
        if not isinstance(opts, dict):
            raise TypeError('É necessário um dict com parâmetros válidos')

        self.__ydl_opts = opts

    def download(self, url: str):
        with youtube_dl.YoutubeDL(self.__ydl_opts) as ydl:
            try:
                data = ydl.extract_info(url)
                return data['title']

            except youtube_dl.utils.DownloadError:
                try:
                    ydl.cache.remove()
                    data = ydl.extract_info(url)
                    return data['title']

                except youtube_dl.utils.DownloadError:
                    return False

    @staticmethod
    def yt_search(text: str):
        video_json = ''
        command = ['youtube-dl', '-j', f'ytsearch: {text}']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True).stdout.split()
        for i in result:
            video_json = video_json + i

        video_json = json.loads(video_json)
        return video_json['webpage_url']


if __name__ == '__main__':  # main para teste
    yt = YoutubeDownloader()
    coisa = yt.yt_search('TR/ST Slow Burn')
    print(coisa)
    down = yt.download(coisa)
    print(down)
