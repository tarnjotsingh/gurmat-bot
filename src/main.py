import os
import logging as log
import discord
from discord.ext import commands
from dotenv import load_dotenv
from station import Station
from utils import Utils


log.basicConfig(level=log.INFO)


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='.')
utils = Utils(log.DEBUG)
station = None


@bot.event
async def on_ready():
    log.info(f'{bot.user} has connected to Discord!')


@bot.event
async def on_message(msg: discord.Message):
    if msg.content.startswith(bot.command_prefix):
        await bot.process_commands(msg)
    else:
        await utils.message_handler(bot, msg)


@bot.command(pass_context=True)
async def ping(ctx: commands.Context):
    author = ctx.author
    channel = ctx.channel
    log.info(utils.user_usage_log(ctx))
    await channel.send(f"{author.mention} pong!")


@bot.command(pass_context=True)
async def join(ctx: commands.Context):
    log.info(utils.user_usage_log(ctx))
    connected = ctx.message.author.voice
    if connected:
        await ctx.message.add_reaction('🙏🏼')
        await connected.channel.connect()
    else:
        await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, you need to join a voice channel first ji")


@bot.command(pass_context=True)
async def leave(ctx: commands.Context):
    global station
    log.info(utils.user_usage_log(ctx))

    if ctx.voice_client:
        await ctx.message.add_reaction('🙏🏼')
        await ctx.voice_client.disconnect()
        station = None
    else:
        await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, I'm not in a voice channel")


@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx: commands.Context, stream_alias: str = "247kirtan"):
    global station
    log.info(utils.user_usage_log(ctx))

    # Check if the bot IS NOT connected to a voice chat already. If it is not in a voice chat then call the join()
    # command to add it to the voice channel the author of the message is currently in.
    if not ctx.voice_client:
        await join(ctx)

    # Set the station object
    if station and station.stream_alias.__eq__(stream_alias):
        await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, the selected station is already playing ji")
    else:
        station = Station(stream_alias)
        # Restart/Start the stream based on the configured station
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        ctx.voice_client.play(source=discord.FFmpegPCMAudio(station.url))
        
        # Send reaction as a confirmation the command has been registered.
        await ctx.message.add_reaction('🙏🏼')


@bot.command(pass_context=True, aliases=['s', 'stp'])
async def stop(ctx: commands.Context):
    global station
    log.info(utils.user_usage_log(ctx))

    if ctx.voice_client:
        await ctx.message.add_reaction('🙏🏼')
        ctx.voice_client.stop()
        station = None
    else:
        await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, there isn't anything playing ji")


bot.run(TOKEN)
