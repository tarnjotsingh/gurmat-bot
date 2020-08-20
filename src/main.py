import os
import discord
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
    # Check if the bot IS NOT connected to a voice chat already. If it is not in a voice chat then call the join()
    # command to add it to the voice channel the author of the message is currently in.
    if not ctx.voice_client:
        await join(ctx)

    ctx.voice_client.play(source=discord.FFmpegPCMAudio("http://72.29.64.55:9302/;"))
    #source='https://www.ikirtan.com/Bhai_Amolak_Singh_Jee/Bhai_Amolak_Singh_Jee_01.mp3'))


@bot.command(pass_context=True, aliases=['s', 'stp'])
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
    else:
        await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, there isn't anything playing ji!")

bot.run(TOKEN)
