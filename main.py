import discord
import os
from discord.ext import tasks
from decouple import config
from utils.yt_download import YoutubeDownloader
from utils.web_search import Search
from utils.cache_clean import CacheClean


class Bot(discord.Client, Search, YoutubeDownloader):
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

        super().__init__(download_folder=path)
        self.__cache_manager = CacheClean(path)

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

        return name

    @tasks.loop(seconds=3)
    async def __music_player(self):
        if self.__player:
            if self.__music_list:
                if not self.__player.is_playing() and not self.__paused:
                    actual_music = self.remove_caracteres(self.__music_list.pop(0))
                    self.__player.play(discord.FFmpegPCMAudio(f'music_cache/{actual_music}.webm'))
                    await self.__original_channel.send(f'Reproduzindo {actual_music}!')

    @tasks.loop(seconds=5)
    async def __cache_clean(self):
        if self.__cache_manager.cache_size() > 10:
            if not self.__player:
                self.__cache_manager.cache_clean()

            else:
                if not self.__player.is_playing() and not self.__paused:
                    self.__cache_manager.cache_clean()

    async def on_ready(self):
        print('Os serviços do bot iniciaram com sucesso!\n')
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

        elif msg.content.startswith('!play'):
            self.__original_channel = msg.channel
            music_search = msg.content[6:]
            if music_search == '' or music_search == ' ':
                await self.__original_channel.send('Insira um nome válido!')
                return

            try:
                self.__voice_channel = msg.author.voice.channel
                await self.__original_channel.send('Procurando sua música...')

                link = self.yt_search(music_search)
                title = self.download(link)
                if title:
                    self.__music_list.append(title)

                    if not self.__player:
                        self.__player = await self.__voice_channel.connect()

                    elif not self.__player.is_connected():
                        await self.__player.move_to(self.__voice_channel)

                    if self.__player.is_playing():
                        await self.__original_channel.send(f'{title} foi adicionado na fila!')

                else:
                    await self.__original_channel.send('Houve um erro ao fazer o download da música')

            except AttributeError:
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

        elif msg.content == '!continue':
            if self.__player:
                if self.__player.is_paused():
                    self.__player.resume()
                    self.__paused = False

        elif msg.content == '!skip':
            if self.__player:
                if self.__player.is_playing():
                    self.__player.stop()

        elif msg.content == '!disconnect':
            if self.__player:
                if self.__player.is_connected() and (self.__player.is_playing() or self.__player.is_paused()):
                    self.__player.stop()
                    self.__music_list = []
                    await self.__player.disconnect()
                    self.__paused = False

                else:
                    self.__music_list = []
                    await self.__player.disconnect()
                    self.__paused = False

        elif msg.content.startswith('!search'):
            self.__original_channel = msg.channel
            pesquisa = msg.content[8:]
            if pesquisa == '' or pesquisa == ' ':
                await self.__original_channel.send('Pesquisa inválida')

            else:
                result = self.search(pesquisa)
                if result != '':
                    await self.__original_channel.send(result)

                else:
                    await self.__original_channel.send('Houve um erro ao fazer a pesquisa')


if __name__ == '__main__':
    bot = Bot()
    bot.run(config('TOKEN'))
