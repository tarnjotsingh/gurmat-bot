import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from radio import Radio
from utils import message_handler, user_usage_log

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("bot_main")
logger.setLevel(LOG_LEVEL)

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
    """Just for testing if the bot is up!"""
    author = ctx.author
    channel = ctx.channel
    logger.info(user_usage_log(ctx))
    await channel.send(f"{author.mention} pong!")


bot.add_cog(Radio(bot).logging(LOG_LEVEL))
bot.run(TOKEN)
