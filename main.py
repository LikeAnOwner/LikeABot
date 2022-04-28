from dis import disco
import discord
from discord.ext import commands
from sqlalchemy import null
import youtube_dl
import random
from youtubesearchpython import *

prefix = '!'
watching = '00 Schneider – Jagd auf Nihil Baxter'

default_role = 'Member'
gameshow_role = 'Spielshow'

response_channels = [727254770531958875, 827625896756117585, 827627169903542313, 727252459524718659]

voice_category_id = 727484335015460916
voice_channel_list = []

private_category_id = 941980141972766760
private_creating_room = 941983561337159720

with open('token.txt', 'r') as token_file:
  token = token_file.read()

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    print(f'Hallo, ich bin {client.user.name}!')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=watching))

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=default_role)
    await member.add_roles(role)

@client.command()
async def help(ctx):
    if ctx.channel.id in response_channels:
        await ctx.send('Aktuell stehen noch keine Befehle zur Verfügung!')

@client.command()
async def play(ctx, *args):
    if len(args) == 1 and args[0].startswith("http"):
        url = args[0]
    elif len(args) == 0:
        await ctx.reply('Dieser Befehl erfordert einen Wert!', mention_author=False)
        return
    else:
        videosSearch = CustomSearch("".join(args), VideoSortOrder.relevance, limit = 1)
        dict = videosSearch.result()
        url = dict['result'][0]['link']
    if ctx.author.voice is None:
        await ctx.reply('Du musst einem Sprachkanal beitreten, um diesen Befehl verwenden zu können!', mention_author=False)
        return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    ctx.voice_client.stop()
    FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn'}
    YDL_OPTIONS = {'format':'bestaudio'}
    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        title = info['title']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        vc.play(source)
        await ctx.reply('{} wird nun gespielt!'.format(title), mention_author=False)

@client.command()
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.reply('Der Bot befindet sich in keinem Sprachkanal!', mention_author=False)
    else:
        await ctx.voice_client.disconnect()

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel == after.channel:
        return
    for guild in client.guilds:
        for channel in guild.voice_channels:
            if channel.category_id == voice_category_id:
                if not channel.members:
                    voice_channel_list.append(channel.id)
                if channel.bitrate != 128000:
                    await channel.edit(bitrate=128000)

    if not voice_channel_list:
        category = client.get_channel(voice_category_id)
        await member.guild.create_voice_channel('Game Room', category = category)

    if len(voice_channel_list) == 2:
        existing_channel = discord.utils.get(member.guild.channels, id=random.choice(voice_channel_list))
        if existing_channel is not None:
            await existing_channel.delete()
        else:
            print('Fehler beim Löschen eines Game Rooms: ', str(existing_channel))

    voice_channel_list.clear()

    # private talk
    if not before.channel:
        if after.channel.id == private_creating_room:
            category = client.get_channel(private_category_id)
            await member.guild.create_voice_channel(member.name + '\'s Room', category = category)
            channel = discord.utils.get(client.get_all_channels(), name=member.name + '\'s Room')
            overwrite = discord.PermissionOverwrite()
            overwrite.move_members = True
            overwrite.mute_members = True
            overwrite.view_channel = True
            overwrite.connect = True
            await channel.set_permissions(member, overwrite=overwrite)
            await channel.edit(user_limit=5, bitrate=128000)
            await member.move_to(channel)
    elif before.channel and after.channel:
        if before.channel.name == member.name + '\'s Room':
            if after.channel.id == private_creating_room:
                channel = discord.utils.get(client.get_all_channels(), name='Wartezimmer')
                await member.move_to(channel)
                existing_channel = discord.utils.get(member.guild.channels, id=before.channel.id)
                if existing_channel is not None:
                    await existing_channel.delete()
                else:
                    print(str(existing_channel))
                return
        if after.channel.id == private_creating_room:
            category = client.get_channel(private_category_id)
            await member.guild.create_voice_channel(member.name + '\'s Room', category = category)
            channel = discord.utils.get(client.get_all_channels(), name=member.name + '\'s Room')
            overwrite = discord.PermissionOverwrite()
            overwrite.move_members = True
            overwrite.mute_members = True
            overwrite.view_channel = True
            overwrite.connect = True
            await channel.set_permissions(member, overwrite=overwrite)
            await channel.edit(user_limit=5, bitrate=128000)
            await member.move_to(channel)
        if before.channel.name == member.name + '\'s Room':
            existing_channel = discord.utils.get(member.guild.channels, id=before.channel.id)
            if existing_channel is not None:
                await existing_channel.delete()
            else:
                print(str(existing_channel))
    elif before.channel and not after.channel:
        if before.channel.name == member.name + '\'s Room':
            existing_channel = discord.utils.get(member.guild.channels, id=before.channel.id)
            if existing_channel is not None:
                await existing_channel.delete()
            else:
                print(str(existing_channel))

client.run(token)
