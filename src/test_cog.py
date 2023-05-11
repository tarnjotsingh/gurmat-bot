import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands


class Example(commands.Cog):

    group = SlashCommandGroup("group", "Message from test cog")

    def __init__(self, bot_: discord.Bot):
        self.bot = bot_

    @group.command()
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond("Hello this is a slash subcommand from the test cog")


