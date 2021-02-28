import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from radio import Radio
from reaction_roles import ReactionRoles
from utils import message_handler, user_usage_log

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MDB_PORT = int(os.getenv('MONGODB_PORT'))
LOG_LEVEL = logging.getLevelName(os.getenv('LOG_LEVEL'))

# Configure logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("bot_main")
logger.setLevel(LOG_LEVEL)
logger.info(f"Logging set to: {LOG_LEVEL}")

# Initialise discord bot and connection to database
bot = commands.Bot(command_prefix='.')
database = None

try:
    # Attempt to establish a connection with the local mongodb server
    logging.info("Connecting to the database")

    client = MongoClient(port=MDB_PORT)
    client.server_info()               # Will throw timeout exception when connection to database can't be made
    database = client.gurmatbot
except errors.ServerSelectionTimeoutError:
    logger.exception("Failed to connect to the database")


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


# Initialise relevant classes and have them added as cogs to the main bot object
bot.add_cog(Radio(bot, database).logging(LOG_LEVEL))
bot.add_cog(ReactionRoles(bot, database).logging(LOG_LEVEL))
bot.run(TOKEN)
