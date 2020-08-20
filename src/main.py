import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='#')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(pass_context=True)
async def ping(ctx):
    author = ctx.message.author
    channel = ctx.message.channel
    await channel.send(f"{author.mention} pong!")


@bot.command(pass_context=True)
async def join(ctx):
    connected = ctx.message.author.voice
    if connected:
        await connected.channel.connect()

@bot.command(pass_context=True)
async def leave(ctx):
    await ctx.voice_client.disconnect()

bot.run(TOKEN)
