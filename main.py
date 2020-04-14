import discord
from discord.ext import tasks
from decouple import config
from yt_download import download_yt, search

client = discord.Client()
canal_original = None
canal_de_voz = None
player = None
music_list = []
paused = False
changelog = '''
Notas de versão:

1.1.4:
- Suporte a mais caracteres especiais nos nomes das músicas;
- Otimização no tempo de espera para reprodução de música;
- Adição da sessão de ajuda (!help);
- Adição da sessão changelog (!changelog).

1.3.4:
- Suporte a lista de reprodução continua adicionado;
- Suporte a pular reprodução adicionado (!skip);
- Suporte a desconectar bot adicionado (!disconnect);
- Os bugs encontrados foram eliminados.

1.4.4:
- Atualização de segurança do Token do Discord.

'''
help_msg = '''
Comandos disponíveis:

!play <nome da música> - pesquisa e reproduz o áudio;
!stop - para a reprodução;
!pause - pausa a reprodução;
!continue - continua a reprodução pausada;
!skip - pula para o próximo áudio;
!disconnect - desconecta o bot;
!changelog - notas de versão;
!ping - Pong!
'''


def remove_caracteres(name: str):
    m_name = name
    if ':' in m_name:
        m_name = m_name.replace(':', ' -')

    if '"' in m_name:
        m_name = m_name.replace('"', "'")

    if '/' in m_name:
        m_name = m_name.replace('/', '_')

    if '|' in m_name:
        m_name = m_name.replace('|', '_')

    return m_name


@tasks.loop(seconds=3)
async def music_player():
    if player:
        if music_list:
            if not player.is_playing() and not paused:
                actual_music = remove_caracteres(music_list.pop(0))
                player.play(discord.FFmpegPCMAudio(f'music_cache/{actual_music}.webm'),
                            after=lambda e: print(f'Música concluída.\n'))
                await canal_original.send(f'Reproduzindo {actual_music}!')


@client.event
async def on_ready():
    print('O bot foi iniciado!\n')
    music_player.start()


@client.event
async def on_message(msg):
    global player, music_list, canal_original, canal_de_voz, paused
    if msg.author == client.user:  # ignora as mensagens do próprio bot
        return

    elif msg.content == '!ping':
        await msg.channel.send('Pong!')

    elif msg.content == '!changelog':
        await msg.channel.send(changelog)

    elif msg.content == '!help':
        await msg.channel.send(help_msg)

    elif msg.content.startswith('!play'):
        canal_original = msg.channel
        music_search = msg.content[6:]
        if music_search == '' or music_search == ' ':
            await canal_original.send('Insira um nome válido!')
            return

        try:
            canal_de_voz = msg.author.voice.channel
            await canal_original.send('Procurando sua música...')

            link = search(music_search)
            title = download_yt(link)
            music_list.append(title)

            if not player:
                player = await canal_de_voz.connect()

            elif not player.is_connected():
                await player.move_to(canal_de_voz)

            if player.is_playing():
                await canal_original.send(f'{title} foi adicionado na fila!')

        except AttributeError:
            await canal_original.send('Entre em um canal de áudio!')

    elif msg.content == '!stop':
        if player:
            if player.is_playing():
                player.stop()
                music_list = []

    elif msg.content == '!pause':
        if player:
            if player.is_playing():
                player.pause()
                paused = True

    elif msg.content == '!continue':
        if player:
            if player.is_paused():
                player.resume()
                paused = False

    elif msg.content == '!skip':
        if player:
            if player.is_playing():
                player.stop()

    elif msg.content == '!disconnect':
        if player:
            if player.is_connected() and (player.is_playing() or player.is_paused()):
                player.stop()
                music_list = []
                await player.disconnect()
                paused = False

            else:
                music_list = []
                await player.disconnect()
                paused = False


if __name__ == '__main__':
    client.run(config('TOKEN'))
