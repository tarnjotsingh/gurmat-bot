import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from station import Radio
from utils import message_handler, user_usage_log


LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("bot_main")
logger.setLevel(LOG_LEVEL)
rad = Radio(LOG_LEVEL)

logger.info(f"Logging set to: {LOG_LEVEL}")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')


@bot.event
async def on_message(msg: discord.Message):
    if msg.content.startswith(bot.command_prefix):
        await bot.process_commands(msg)
    else:
        await message_handler(msg)

@bot.command()
async def ping(ctx: commands.Context):
    author = ctx.author
    channel = ctx.channel
    logger.info(user_usage_log(ctx))
    await channel.send(f"{author.mention} pong!")


@bot.command(aliases=['r', 'rad'])
async def radio(ctx: commands.Context, action: str = None, station: str = None):
    global rad
    logger.info(user_usage_log(ctx))

    switch = {
        "join": rad.join,
        "leave": rad.leave,
        "play": rad.play,
        "stop": rad.stop,
        "np": rad.np
    }

    handler = switch.get(action, lambda ctx: ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, invalid command ji"))

    if action.__eq__("play"):
        await handler(ctx, stream_alias=station)
    else:
        await handler(ctx)

bot.run(TOKEN)
