import asyncio
import discord
import random
import youtube_dl
from discord.ext import commands, tasks
from random import choice

# id server teste: 759608170229530654
# id server among: 702832904585085021


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='-')
status = ['Trabalhando!', 'Tocando música!', 'Moderando']
queue = []


@client.event
async def on_ready():
    change_status.start()
    print(f'{client.user} is online')


@tasks.loop(seconds=40)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


@client.event
async def on_member_join(member):
    for channel in member.guild.channels:
        if str(channel) == 'geral':
            await channel.send(f'Bem vindo ao servidor {member.mention}!!!!!')


@client.event
async def on_member_remove(member):
    for channel in member.guild.channels:
        if str(channel) == 'geral':
            await channel.send(f'Uma pena que {member.mention} nos deixou...')


@client.command(name='count', help='-count para mostrar o numero de usuários no servidor')
async def count(ctx):
    member_count = len(ctx.guild.members)
    await ctx.send(f'Esse servidor tem {member_count} membros')


@client.command(name='clear', help='-clear [numero de linhas] para remover linhas')
async def clear(ctx, linhas=5):
    await ctx.channel.purge(limit=linhas)
    await ctx.send(f'Ok, removi {linhas} mensagens')


@client.command(name='kick', help='-kick [@dousuario] para kickar um usuário')
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} foi kickado, {reason}')


@client.command(name='ban', help='-ban [@dousuario] para banir um usuário')
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member} foi banido, {reason}')


@client.command(name='unban', help='-unban [@dousuario] para desbanir um usuário')
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} foi desbanido')
            return


@client.command(name='c', help='-c [qualquer texto] para retornar uma resposta aleatoria')
async def c(ctx):
    respostas = ['Sim',
                 'Com certeza',
                 'Absolutamente',
                 'Sem dúvidas',
                 'Claro',
                 'Obviamente',
                 'Não tenho essa informação no momento',
                 'Talvez',
                 'Não faço ideia',
                 'Sei la mano',
                 'Não',
                 'Claro que não',
                 'Óbvio que não',
                 'De jeito nenhum',
                 'Sem chance',
                 'Nem'
                 ]
    await ctx.send(f'{random.choice(respostas)}')


@client.command(name='join', help='Quando em um canal de voz, -join para o bot entrar no mesmo canal')
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@client.command(name='leave', help='-leave para o bot deixar o canal de voz')
async def leave(ctx):
    channel = ctx.message.guild.voice_client
    await channel.disconnect()


@client.command()
async def queue_(ctx, url):
    global queue

    queue.append(url)
    await ctx.send(f'`{url}` added to queue!')


@client.command()
async def remove(ctx, number):
    global queue

    try:
        del (queue[int(number)])
        await ctx.send(f'Your queue is now `{queue}!`')

    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')


@client.command(name='play', help='-play [url youtube] para tocar uma musica')
async def play(ctx, url):
    global queue

    server = ctx.message.guild
    vc = server.voice_client

    player = await YTDLSource.from_url(url, loop=client.loop)
    vc.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send('**Tocando:** {}'.format(player.title))
    'del queue[0]'


@client.command(name='pause', help='-pause para pausar a musica')
async def pause(ctx):
    server = ctx.message.guild
    vc = server.voice_client

    vc.pause()


@client.command(name='resume', help='-resume para despausar a musica')
async def resume(ctx):
    server = ctx.message.guild
    vc = server.voice_client

    vc.resume()


@client.command(name='stop', help='-stop para parar de tocar a musica')
async def stop(ctx):
    server = ctx.message.guild
    vc = server.voice_client

    vc.stop()

client.run('token')
