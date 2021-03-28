import logging
from typing import Union

from discord.ext import commands
from pymongo.database import Database

from utils import user_usage_log, embed_builder

from swagger_client import api_client, configuration
from swagger_client.api import jaapcounters_api
from swagger_client.models import rows


class JaapCounters(commands.Cog):
    __slots__ = ['bot', 'db', 'logger', 'config', 'client', 'jaap_api']

    def __init__(self, bot: commands.Bot, db: Database):
        self.bot: commands.Bot = bot
        self.db: Database = db
        self.logger: logging.Logger = logging.getLogger("JaapCounters")
        self.logger.setLevel(logging.INFO)

        config = configuration.Configuration()
        self.client = api_client.ApiClient(configuration=config)
        self.jaap_api = jaapcounters_api.JaapcountersApi(api_client=self.client)

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    @commands.group()
    async def jaap(self, ctx: commands.Context):
        """View and add to the jaap counter"""
        self.logger.info(user_usage_log(ctx))
        counters: rows.Rows = self.jaap_api.get_counter_by_name("gurmat_bot_test")
        counter = counters.rows[0]

        title = "Paath Counter"
        field_title = counter.title if counter.title else "No title available"
        embed = embed_builder(None, title, counter.description, None)

        embed.add_field(name=field_title, value=f"\n\nCounter name - {counter.formname}\n"
                                                f"Number of paaths completed - {counter.jaaps}", inline=False)

        await ctx.channel.send(embed=embed)
