import logging
import string

import discord
from discord import Embed

logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)

BOT_ID = 745385175856316556
DEFAULT_COLOUR = 0xffa900

# Can extend this so that it's not just the keywords but there are actual stats being recorded against each word
# being used so that we can retrieve statistics on their usages.
vaheguru_key_words = [
    'ਵਾਹਿਗੁਰੂ', 'vaheguru', 'vaheguroo', 'waheguru', 'waheguroo', 'guru', 'jesus', 'christ', 'god',
    'jai sri raam', 'raam', 'ram', 'allah', 'omg', 'rab', 'rabb', 'khuda', 'khudha', 'akaal', 'akal',
    'hari', 'har', 'gopal', 'gobind', 'paramatma', 'pati', 'satgur', 'udharan', 'parmeshwar', 'parmeswar',
    'gorak', 'gopal', 'kaal', 'akaal', 'akal', 'purkh', 'nanak', 'arjan', 'data', 'daataa', 'guru', 'parvadigar',
    'ek', 'oankar', 'hari', 'har', 'narayan'
]


def user_usage_log(ctx) -> str:
    # Use discords context object to build the string
    return f"{ctx.author} used the {ctx.command} command in the {ctx.message.channel} channel"


def vaheguru_check(message: str) -> bool:
    """Check if one of the key words exist in the provided message string"""
    # I want to linearly scan through the entire sentence and see if any of the words exist in the vaheguru_list
    msg = message.translate(str.maketrans('', '', string.punctuation)).split(" ")
    return any(w in vaheguru_key_words for w in msg)


async def message_handler(message: discord.Message):
    logger.debug("Message handler called")
    logger.debug(f"Following message detected by message handler: {message.author}: {message.content}")

    content = message.content.lower()

    # ID referenced here is the ID of the Gurmat Bot's account
    if vaheguru_check(content) and not message.author.id == BOT_ID:
        await message.channel.send(f"{message.author.mention} ਵਾਹਿਗੁਰੂ")


def embed_builder(colour, title, desc, img_url) -> Embed:
    embed = discord.Embed()
    embed.colour = colour if colour else DEFAULT_COLOUR
    embed.title = title
    embed.description = desc
    if img_url:
        embed.set_image(url=img_url)
    return embed
