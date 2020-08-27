import logging
import discord
from discord.ext import commands
from typing import Union

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)

vaheguru_list = [
    'ਵਾਹਿਗੁਰੂ', 'vaheguru', 'vaheguroo', 'waheguru', 'waheguroo', 'guru' 'guru ji', 'jesus', 'christ', 'god',
    'jai sri raam', 'raam', 'ram', 'allah', 'omg', 'rab', 'rabb', 'khuda', 'khudha', 'akaal', 'akal'
]


def user_usage_log(ctx) -> str:
    # Use discords context object to build the string
    return f"{ctx.author} used the {ctx.command} command in the {ctx.message.channel} channel"


async def message_handler(message: discord.Message):
    logger.debug("Message handler called")
    logger.debug(f"Following message detected by message handler: {message.author}: {message.content}")

    content = message.content.lower()

    if any(v in content for v in vaheguru_list) and not message.author.id == 745385175856316556:
        await message.channel.send(f"{message.author.mention} ਵਾਹਿਗੁਰੂ")
