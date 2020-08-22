import logging
import discord
from discord.ext import commands
from typing import Union

vaheguru_list = [
    'ਵਾਹਿਗੁਰੂ', 'vaheguru', 'vaheguroo', 'waheguru', 'waheguroo', 'guru'
    'guru ji', 'jesus', 'christ', 'god', 'jai sri raam', 'raam', 'ram',
    'allah', 'omg', 'rab', 'rabb', 'khuda', 'khudha'
    ]

class Utils:

    def __init__(self, log_lvl: Union[int, str] = logging.INFO):
        self.logger = logging.getLogger("utils")
        self.logger.setLevel(log_lvl)

    def _init_logging(self):
        # ISO8601 timestamp + log level padded + message
        formatter = logging.Formatter('%(asctime)s %(levelname)7s - %(message)s', "%Y-%m-%dT%H:%M:%S%z")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    # Use discords context object to build the string
    def user_usage_log(self, ctx) -> str:
        return f"{ctx.author} used the {ctx.command} command in the {ctx.message.channel} channel"

    def vaheguru_handler(self) -> str:
        self.logger.debug("Vaheguru handler called")
        pass

    async def message_handler(self, bot: discord.Client, message: discord.Message):
        self.logger.debug("Message handler called")
        self.logger.debug(f"Following message detected by message handler: {message.author}: {message.content}")
        
        content = message.content.lower()

        if any(v in content for v in vaheguru_list) and not message.author.id == 745385175856316556:
            await message.channel.send(f"{message.author.mention} ਵਾਹਿਗੁਰੂ")
