import logging
import discord
from discord import Embed
from typing import Union
from pymongo import MongoClient
from discord.ext import commands
from utils import user_usage_log


class ReactionRoles(commands.Cog):
    """Class for handling assigning of roles based on the provided reaction"""
    def __init__(self, bot: commands.Bot, db: MongoClient):
        self.logger = logging.getLogger("ReactionRoles")
        self.logger.setLevel(logging.INFO)
        self.bot = bot
        self.db = db

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    @commands.group()
    async def roles(self, ctx: commands.Context):
        """View and manage reaction roles for the server"""
        self.logger.info(user_usage_log(ctx))        

        placeholder = self.test_embed()
        await ctx.send(embed=placeholder)

    ######## Helper functions #########

    def test_embed(self) -> Embed:
        embed = discord.Embed()
        embed.colour = 0xffa900
        embed.title = "Server Roles"
        embed.description = f"This is a placeholder value for reaction roles feature"

        return embed
