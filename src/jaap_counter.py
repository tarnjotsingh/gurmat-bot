import logging
from typing import Union

from discord.ext import commands
from pymongo.database import Database
from pymongo.collection import Cursor

from utils import user_usage_log, embed_builder

from swagger_client import api_client, configuration
from swagger_client.api import jaapcounters_api
from swagger_client.models import rows
from swagger_client.rest import ApiException


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
        self.counter_name = "gurmat_bot_test"

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    @commands.group()
    async def jaap(self, ctx: commands.Context):
        if not ctx.subcommand_passed:
            await self.view(ctx)

    @jaap.command()
    async def set(self, ctx: commands.Context, counter_name: str):
        """ Sets the counter to use on the server """

        # Check if counter is already set in guild, check if it's the same one, otherwise overwrite
        counter_check: Cursor = self.db.jaap_counters.find_one({'guild_id': ctx.guild.id})
        print("asdf")
        # self.db.jaap_counters.insert_one({'guild_id': ctx.guild.id, 'counter_name': counter_name})
        pass


    @jaap.command()
    async def view(self, ctx: commands.Context):
        """View and add to the jaap counter"""

        self.logger.info(user_usage_log(ctx))
        counters: rows.Rows = self.jaap_api.get_counter_by_name(self.counter_name)
        counter = counters.rows[0]

        title = "Paath Counter"
        field_title = counter.title if counter.title else "No title available"
        embed = embed_builder(None, title, counter.description,
                              "https://cdn.discordapp.com/attachments/749767325317857290/825842078700929054/"
                              "Screenshot_from_2021-03-28_22-21-13.png")

        progress = (float(counter.jaaps)/500) * 100

        embed.add_field(name=field_title, value=f"Counter name - {counter.formname}\n"
                                                f"Number of paaths completed - {counter.jaaps}\n"
                                                f"Progress - {counter.jaaps}/500 - {progress}%", inline=False)

        await ctx.channel.send(embed=embed)

    @jaap.command()
    async def submit(self, ctx: commands.Context, jaaps):
        title = "Submit Jaaps"
        desc = f"Submitted {jaaps} jaaps to {self.counter_name} counter"
        embed = embed_builder(None, title, desc, None)

        try:
            self.jaap_api.submit_new_counter("test", float(jaaps))
        except ApiException as e:
            self.logger.error(e)
            # embed.add_field(name="Error encountered", value=f"HTTP Status - {e.status}", inline=False)

        await ctx.channel.send(embed=embed)
