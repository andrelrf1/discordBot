import os
from discord import Client, FFmpegPCMAudio
from discord.ext import tasks
from decouple import config
from utils.yt_download import YoutubeDownloader
from utils.cache_clean import CacheClean


class Bot(Client, YoutubeDownloader, CacheClean):
    __original_channel = None
    __voice_channel = None
    __player = None
    __paused = False
    __music_list = []

    def __init__(self, music_cache_path: str = ''):
        if music_cache_path != '':
            path = music_cache_path + '/music_cache' if music_cache_path[-1] != '/' else 'music_cache'
            if not os.path.isdir(music_cache_path + '/music_cache' if music_cache_path[-1] != '/' else 'music_cache'):
                os.mkdir(music_cache_path + '/music_cache' if music_cache_path[-1] != '/' else 'music_cache')

        else:
            path = './music_cache'
            if not os.path.isdir('music_cache'):
                os.mkdir('music_cache')

        Client.__init__(self)
        YoutubeDownloader.__init__(self, path)
        CacheClean.__init__(self, path)

    @staticmethod
    def remove_caracteres(name: str):
        if ':' in name:
            name = name.replace(':', ' -')

        if '"' in name:
            name = name.replace('"', "'")

        if '/' in name:
            name = name.replace('/', '_')

        if '|' in name:
            name = name.replace('|', '_')

        if ' *' in name:
            name = name.replace(' *', ' _')

        if '*' in name:
            name = name.replace('*', '')

        if '?' in name:
            name = name.replace('?', '')

        return name

    @tasks.loop(seconds=3)
    async def __music_player(self):
        if self.__player:
            if self.__music_list:
                if not self.__player.is_playing() and not self.__paused:
                    actual_music = self.remove_caracteres(self.__music_list.pop(0))
                    if os.path.exists(f'.\\music_cache\\{actual_music}.m4a'):
                        self.__player.play(FFmpegPCMAudio(f'.\\music_cache\\{actual_music}.m4a'))

                    else:
                        self.__player.play(FFmpegPCMAudio(f'.\\music_cache\\{actual_music}.webm'))

                    await self.__original_channel.send(f'Reproduzindo {actual_music}!')

    @tasks.loop(minutes=3)
    async def __cache_clean(self):
        if self.cache_size() > 15:
            if not self.__player:
                self.cache_clean()

            else:
                if not self.__player.is_playing() and not self.__paused:
                    self.cache_clean()

    async def on_ready(self):
        print('O bot iniciou corretamente!\n')
        self.__music_player.start()
        self.__cache_clean.start()

    async def on_message(self, msg):
        if msg.author == self.user:  # ignora as mensagens do próprio bot
            return

        elif msg.content == '!ping':
            await msg.channel.send('Pong!')

        elif msg.content == '!changelog':
            with open('./bot_messages/changelog.txt', 'r', encoding='utf-8') as changelog:
                await msg.channel.send(changelog.read())

        elif msg.content == '!help':
            with open('./bot_messages/help.txt', 'r', encoding='utf-8') as help_msg:
                await msg.channel.send(help_msg.read())

        elif (msg.content.startswith('!play') and msg.content.split(' ')[0] == '!play') or (
                msg.content.startswith('!p') and msg.content.split(' ')[0] == '!p'):
            self.__original_channel = msg.channel
            music_search = msg.content[6:] if msg.content.split(' ')[0] == '!play' else msg.content[3:]
            if music_search == '' or music_search == ' ':
                await self.__original_channel.send('Insira um nome válido!')
                return

            try:
                self.__voice_channel = msg.author.voice.channel
                await self.__original_channel.send('Procurando música...')

                link = self.yt_search(music_search)
                title = self.download(link)
                if title:
                    self.__music_list.append(title)

                    if not self.__player:
                        self.__player = await self.__voice_channel.connect()

                    if self.__player.is_playing():
                        await self.__original_channel.send(f'{title} foi adicionado na fila!')

                else:
                    await self.__original_channel.send('Houve um erro ao fazer o download da música')

            except AttributeError as err:
                print(err)
                await self.__original_channel.send('Entre em um canal de áudio!')

        elif msg.content == '!stop':
            if self.__player:
                if self.__player.is_playing():
                    self.__player.stop()
                    self.__music_list = []

        elif msg.content == '!pause':
            if self.__player:
                if self.__player.is_playing():
                    self.__player.pause()
                    self.__paused = True

        elif msg.content == '!continue' or msg.content == '!resume':
            if self.__player:
                if self.__player.is_paused():
                    self.__player.resume()
                    self.__paused = False

        elif msg.content == '!skip':
            if self.__player:
                if self.__player.is_playing():
                    self.__player.stop()

        elif msg.content == '!next' or msg.content == '!queue':
            if len(self.__music_list) > 0:
                future = 'Na fila:\n\n'
                for music in self.__music_list:
                    future = future + f'{self.__music_list.index(music) + 1} - {music}\n'

                await msg.channel.send(future)

            else:
                await msg.channel.send('Não há músicas na fila')


if __name__ == '__main__':
    bot = Bot()
    bot.run(config('TOKEN'))
