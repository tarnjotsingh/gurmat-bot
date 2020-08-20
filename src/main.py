import os
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(pass_context=True)
async def ping(ctx):
    author = ctx.author
    channel = ctx.channel
    await channel.send(f"{author.mention} pong!")

@bot.command(pass_context=True)
async def join(ctx):
    connected = ctx.message.author.voice
    if connected:
        await connected.channel.connect()
    else:
        await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, you need to join a voice channel first ji.")

@bot.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, I'm not in a voice channel.")

@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx):
    # Check if we're already connected to a voice channel, if not connect to
    # the one the author of the message is in.
    if ctx.voice_client:
        ctx.voice_client.play(discord.FFmpegPCMAudio("http://72.29.64.55:9302/;"))
            #source='https://www.ikirtan.com/Bhai_Amolak_Singh_Jee/Bhai_Amolak_Singh_Jee_01.mp3'))
    else:
        await ctx.channel.send(f"{ctx.author.mention} you need to join a voice channel before you can use this command.")

@bot.command(pass_context=True, aliases=['s', 'stp'])
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
    else:
        await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, there isn't anything playing ji!")

bot.run(TOKEN)
