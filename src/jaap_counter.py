import logging
from typing import Union

import requests
from discord.ext import commands
from pymongo.database import Database

from utils import user_usage_log, BOT_ID



class JaapCounters(commands.Cog):
    __slots__ = ['bot', 'db', 'logger']

    def __init__(self, bot: commands.Bot, db: Database):
        self.bot: commands.Bot = bot
        self.db: Database = db
        self.logger: logging.Logger = logging.getLogger("JaapCounters")
        self.logger.setLevel(logging.INFO)

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    @commands.group()
    async def jaap(self, ctx: commands.Context):
        """View and add to the jaap counter"""
        self.logger.info(user_usage_log(ctx))

        url = "https://api.manjotsingh.xyz/jaapcounters?formname=yoyo"

        response = requests.get(url)
        json = response.json()

        await ctx.channel.send(json)
