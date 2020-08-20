import discord
from discord.ext import commands

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

@bot.command(pass_context=True)
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command(pass_context=True)
async def start(ctx):
    # Check if we're already connected to a voice channel, if not connect to
    # the one the author of the message is in.
    if ctx.voice_client:
        # Actually start playing something
        await ctx.channel.send(f"{ctx.author.mention} placeholder for playing something.")
    else:
        await ctx.channel.send(f"{ctx.author.mention} you need to join a voice channel before you can use this command!")