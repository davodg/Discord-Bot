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
queues = []


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


@client.command()
async def count(ctx):
    member_count = len(ctx.guild.members)
    await ctx.send(f'Esse servidor tem {member_count} membros')


@client.command()
async def clear(ctx, linhas=5):
    await ctx.channel.purge(limit=linhas)
    await ctx.send(f'Ok, removi {linhas} mensagens')


@client.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} foi kickado, {reason}')


@client.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member} foi banido, {reason}')


@client.command()
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} foi desbanido')
            return


@client.command()
async def c(ctx):
    respostas = ['Sim',
                 'Com certeza',
                 'Absolutamente',
                 'Sem dúvidas',
                 'Claro',
                 'Obviamente',
                 'Não tenho essa informação no momento',
                 'Sepa',
                 'Não faço ideia',
                 'Sei la mano',
                 'Não',
                 'Claro que não',
                 'Óbvio que não',
                 'De jeito nenhum',
                 'Sem chance',
                 'Que pergunta idiota'
                 ]
    await ctx.send(f'{random.choice(respostas)}')


@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@client.command()
async def leave(ctx):
    channel = ctx.message.guild.voice_client

    await channel.disconnect()


@client.command()
async def play(ctx, url):
    global queues

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Tocando:** {}'.format(player.title))
    del queues[0]


@client.command()
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()


@client.command()
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()


@client.command()
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()


'''@client.command(aliases=['p', 'f'])
async def fila(ctx, url, ):
    global queues

    queues.append(url)
    await ctx.send(f'`{url}` Adicionada á fila')


@client.command()
async def remove(ctx, number):
    global queues

    try:
        del (queues[int(number)])
        await ctx.send(f'A fila agora é `{queues}!`')
    except:
        await ctx.send('Ou a fila ta vazia ou você digitou um numero errado!')
Ainda não funcional
        '''


client.run('NzU5NTgwOTYwODgxNjM5NDc0.X2_k5Q.zYWuWVGLEu19DadRCJvz2ivAwtU')
