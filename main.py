import discord
from discord.ext import tasks
from decouple import config
from utils.yt_download import YoutubeDownloader
from utils.web_search import Search


class Bot(discord.Client):
    __yt = YoutubeDownloader()
    __web_search = Search()
    __canal_original = None
    __canal_de_voz = None
    __player = None
    __paused = False
    __music_list = []

    @staticmethod
    def __remove_caracteres(name: str):
        m_name = name
        if ':' in m_name:
            m_name = m_name.replace(':', ' -')

        if '"' in m_name:
            m_name = m_name.replace('"', "'")

        if '/' in m_name:
            m_name = m_name.replace('/', '_')

        if '|' in m_name:
            m_name = m_name.replace('|', '_')

        if ' *' in m_name:
            m_name = m_name.replace(' *', ' _')

        if '*' in m_name:
            m_name = m_name.replace('*', '')

        return m_name

    @tasks.loop(seconds=3)
    async def __music_player(self):
        if self.__player:
            if self.__music_list:
                if not self.__player.is_playing() and not self.__paused:
                    actual_music = self.__remove_caracteres(self.__music_list.pop(0))
                    self.__player.play(discord.FFmpegPCMAudio(f'music_cache/{actual_music}.webm'))
                    await self.__canal_original.send(f'Reproduzindo {actual_music}!')

    async def on_ready(self):
        print('Os serviços do bot iniciaram com sucesso!\n')
        self.__music_player.start()

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
            self.__canal_original = msg.channel
            music_search = msg.content[6:]
            if music_search == '' or music_search == ' ':
                await self.__canal_original.send('Insira um nome válido!')
                return

            try:
                self.__canal_de_voz = msg.author.voice.channel
                await self.__canal_original.send('Procurando sua música...')

                link = self.__yt.search(music_search)
                title = self.__yt.download(link)
                if title:
                    self.__music_list.append(title)

                    if not self.__player:
                        self.__player = await self.__canal_de_voz.connect()

                    elif not self.__player.is_connected():
                        await self.__player.move_to(self.__canal_de_voz)

                    if self.__player.is_playing():
                        await self.__canal_original.send(f'{title} foi adicionado na fila!')

                else:
                    await self.__canal_original.send('Houve um erro ao fazer o download da música')

            except AttributeError:
                await self.__canal_original.send('Entre em um canal de áudio!')

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
            self.__canal_original = msg.channel
            pesquisa = msg.content[8:]
            if pesquisa == '' or pesquisa == ' ':
                await self.__canal_original.send('Pesquisa inválida')

            else:
                result = self.__web_search.search(pesquisa)
                if result != '':
                    await self.__canal_original.send(result)

                else:
                    await self.__canal_original.send('Houve um erro ao fazer a pesquisa')


if __name__ == '__main__':
    bot = Bot()
    bot.run(config('TOKEN'))
