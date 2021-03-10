import logging
import os

import discord
from discord import Message, Member, Guild, RawReactionActionEvent
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient, errors

from radio import Radio
from reaction_roles import ReactionRoles, handle_role_assignment
from utils import message_handler, user_usage_log

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MDB_HOST = os.getenv('MONGODB_HOST')
MDB_PORT = int(os.getenv('MONGODB_PORT'))
LOG_LEVEL = logging.getLevelName(os.getenv('LOG_LEVEL'))

# Configure logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("bot_main")
logger.setLevel(LOG_LEVEL)
logger.info(f"Logging set to: {os.getenv('LOG_LEVEL')}")

# Initialise discord bot and connection to database
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)
database = None

try:
    # Attempt to establish a connection with the local mongodb server
    logging.info(f"Connecting to the database at: {MDB_HOST}")

    client = MongoClient(MDB_HOST, port=MDB_PORT)
    client.server_info()  # Will throw timeout exception when connection to database can't be made
    database = client.gurmatbot
except errors.ServerSelectionTimeoutError:
    logger.exception("Failed to connect to the database")
    exit(1)


@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')


@bot.event
async def on_message(msg: Message):
    if msg.content.startswith(bot.command_prefix):
        await bot.process_commands(msg)
    else:
        await message_handler(msg)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    logger.info(error)


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    # This method will capture reactions then call the relvant code to handle it
    # In this case, when we get a reaction on a message sent by the bot we add the relevant role to the user.
    guild: Guild = bot.get_guild(payload.guild_id)
    user: Member = guild.get_member(payload.user_id)

    logger.debug(f"{user} reacted with {payload.emoji}")
    await handle_role_assignment(payload, user, database)


@bot.event
async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    guild: Guild = bot.get_guild(payload.guild_id)
    user: Member = guild.get_member(payload.user_id)

    logger.debug(f"{user} removed reaction {payload.emoji}")
    await handle_role_assignment(payload, user, database)


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
