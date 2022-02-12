import discord
from discord.ext import commands
import random

prefix = '!'
watching = 'gerne Filme'
starter_role = 'Member'
channels = [727254770531958875, 827625896756117585, 827627169903542313, 727252459524718659]
voice_category_id = 727484335015460916
voice_channel_list = []

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
    role = discord.utils.get(member.guild.roles, name=starter_role)
    await member.add_roles(role)

@client.command()
async def help(ctx):
    if ctx.channel.id in channels:
        await ctx.send('Aktuell stehen noch keine Befehle zur Verfügung!')

@client.event
async def on_voice_state_update(member, before, after):
    for guild in client.guilds:
        for channel in guild.voice_channels:
            if channel.category_id == voice_category_id:
                if not channel.members:
                    voice_channel_list.append(channel.id)

    if len(voice_channel_list) == 0:
        category = client.get_channel(voice_category_id)
        await member.guild.create_voice_channel('Game Room', category = category)

    if len(voice_channel_list) == 2:
        existing_channel = discord.utils.get(member.guild.channels, id=random.choice(voice_channel_list))
        if existing_channel is not None:
            await existing_channel.delete()
        else:
            print(str(existing_channel))

    voice_channel_list.clear()

client.run(token)
