import logging
import discord

from typing import Union
from discord.ext import commands
from pymongo.database import Database, Collection
from discord import Message, Reaction, Member, Embed, Role, utils

from utils import user_usage_log

# Stores key value pairs of channel_id:discord.Message
react_msgs = {}


class ReactionRoles(commands.Cog):
    """Class for handling assigning of roles based on the provided reaction"""
    def __init__(self, bot: commands.Bot, db: Database):
        self.bot: commands.Bot = bot
        self.db: Database = db
        self.logger: logging.Logger = logging.getLogger("ReactionRoles")
        self.logger.setLevel(logging.INFO)

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    @commands.group()
    async def roles(self, ctx: commands.Context):
        """View and manage reaction roles for the server"""
        self.logger.info(user_usage_log(ctx))
        # Run list sub-command if no subcommand was passed
        if not ctx.subcommand_passed:
            await self.list(ctx)

    @roles.command()
    async def list(self, ctx: commands.Context):
        """List all roles in the server"""

        # Get all roles (in an iterable) associated with the server the command was called from
        all_roles = ctx.guild.roles
        db_rr = list(self.db.reaction_roles.find({'guild_id': ctx.guild.id}))
        mapped = list(map(lambda r: f"{r['reaction']}: {utils.get(all_roles, id=r['role_id']).mention}", db_rr))
        reactions = list(map(lambda r: r['reaction'], db_rr))

        roles_as_string = '\n'.join(mapped)
        placeholder = self.test_embed(roles_as_string)

        message = await ctx.send(embed=placeholder)

        for r in reactions:
            await message.add_reaction(r)

        await self.track_message(message)

    @roles.command()
    async def add(self, ctx: commands.Context, reaction: str, role: Role):
        """Add a new server role reaction"""
        self.logger.info("Adding new server role")
        self.db.reaction_roles.insert_one(
            {
                'guild_id': ctx.guild.id,
                'role_id': role.id,
                'reaction': reaction,
            }
        )

    # Helper functions

    async def track_message(self, message: Message):
        channel_id = message.channel.id

        # Track message by the channel it's in
        if channel_id in react_msgs:
            # Delete previous message so it can't be reacted to
            await react_msgs[channel_id].delete()
            react_msgs[channel_id] = message
        else:
            react_msgs[channel_id] = message

    def test_embed(self, desc: str) -> Embed:
        embed = discord.Embed()
        embed.colour = 0xffa900
        embed.title = "Server Roles"
        embed.description = desc
        return embed


async def handle_role_assignment(reaction: Reaction, user: Member, database: Database):
    # Check that the message reacted to is the same one saved as a member value
    channel_id = reaction.message.channel.id
    if channel_id in react_msgs and not user.id == 745385175856316556:
        # Query database to get role associated with the given reaction
        r_obj = database.reaction_roles.find_one({'guild_id': reaction.message.guild.id, 'reaction': reaction.emoji})
        role: Role = discord.utils.get(user.guild.roles, id=r_obj['role_id'])
        await user.add_roles(role)


async def handle_role_unassignment(reaction: Reaction, user: Member, database: Database):
    channel_id = reaction.message.channel.id
    if channel_id in react_msgs and not user.id == 745385175856316556:
        # Query database to get role associated with the given reaction
        r_obj = database.reaction_roles.find_one({'guild_id': reaction.message.guild.id, 'reaction': reaction.emoji})
        role: Role = discord.utils.get(user.guild.roles, id=r_obj['role_id'])
        await user.remove_roles(role)
