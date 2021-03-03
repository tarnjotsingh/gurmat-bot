import logging
from typing import Union

import discord
from discord import Message, Member, Embed, Role, RawReactionActionEvent, utils
from discord.ext import commands
from pymongo.database import Database
from pymongo.collection import Cursor

from utils import user_usage_log, BOT_ID

# Stores key value pairs of channel_id:discord.Message
react_msgs = {}


class ReactionRoles(commands.Cog):
    """Class for handling assigning of roles based on the provided reaction"""
    __slots__ = ['bot', 'db', 'logger']

    def __init__(self, bot: commands.Bot, db: Database):
        self.bot: commands.Bot = bot
        self.db: Database = db
        self.logger: logging.Logger = logging.getLogger("ReactionRoles")
        self.logger.setLevel(logging.INFO)

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    @commands.group(aliases=['role'])
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
        placeholder = self.embed_builder(0xffa900, "Server Roles", roles_as_string)

        message = await ctx.send(embed=placeholder)

        for r in reactions:
            await message.add_reaction(r)

        await self.track_message(message)

    @roles.command()
    async def add(self, ctx: commands.Context, r_type: str, *args: str):
        """
        Add a new server role reaction or reaction type

        type (str): The type of object we're adding to the database. This can be:
            - ROLE
            - GROUP
        """
        if len(args) < 1:
            await self.send_invalid_args_msg(ctx)
            return

        switch = {
            'GROUP': lambda: self.add_group(ctx, args),
            'ROLE': lambda: self.add_reaction(ctx, args)
        }

        # Wrap in try/except to handle case where bad r_type is given
        try:
            command = switch.get(r_type.upper())
            await command()
        except TypeError:
            await self.send_invalid_args_msg(ctx)

    async def add_group(self, ctx: commands.Context, *args: str):
        """
        Add a new server reaction role group

        Arguments:
            group_name string: Name of the new group you want to add
        """
        arg_list = list(args[0])
        if len(arg_list).__eq__(1):
            self.logger.info("Adding new reaction role group")
            # TODO: Check if the group already exists
            group_name = ''.join(arg_list[0])
            self.db.reaction_role_groups.insert_one(
                {
                    'guild_id': ctx.guild.id,
                    'name': group_name
                }
            )

            await ctx.message.add_reaction('🙏🏼')

    async def add_reaction(self, ctx: commands.Context, *args: str):
        """
        Add a new server role reaction

        Arguments:
            reaction string: String value of the reaction
            role Role: The role you want to associate with the reaction
            group string: The group you want to assign to the reaction role
        """
        arg_list = list(args[0])
        if len(arg_list).__eq__(3):
            self.logger.info("Adding new reaction role")
            # TODO: Check if the exact same reaction role already exists

            # Validate args
            reaction: str = ''.join(arg_list[0])
            role: Role = utils.get(ctx.guild.roles, mention=''.join(arg_list[1]))
            group_name: str = ''.join(arg_list[2])

            # Query db for group name to get group id
            group: Cursor = self.db.reaction_role_groups.find_one({'name': group_name}, {'_id': 1})
            if group:
                self.db.reaction_roles.insert_one(
                    {
                        'guild_id': ctx.guild.id,
                        'group_id': group.__getitem__('_id'),
                        'role_id': role.id,
                        'reaction': reaction,
                    }
                )

                await ctx.message.add_reaction('🙏🏼')
            else:
                embed = self.embed_builder(
                    0xff0000,
                    "Invalid group",
                    f"The group `{group_name}` does not exist")
                await ctx.send(embed=embed)

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

    async def send_invalid_args_msg(self, ctx: commands.Context):
        embed = self.embed_builder(
            0xff0000,
            "Invalid arguments",
            "Refer to command help by typing `.help roles [sub_command]`")
        await ctx.send(embed=embed)

    def embed_builder(self, colour, title, desc: str) -> Embed:
        embed = discord.Embed()
        embed.colour = colour
        embed.title = title
        embed.description = desc
        return embed


async def handle_role_assignment(payload: RawReactionActionEvent, user: Member, database: Database):
    channel_id = payload.channel_id
    if channel_id in react_msgs and not payload.user_id == BOT_ID:
        # Query database to get role associated with the given reaction
        r_obj = database.reaction_roles.find_one({'guild_id': payload.guild_id, 'reaction': payload.emoji.name})
        role: Role = discord.utils.get(user.guild.roles, id=r_obj['role_id'])

        switch = {
            'REACTION_ADD': lambda: user.add_roles(role),
            'REACTION_REMOVE': lambda: user.remove_roles(role)
        }

        action = switch.get(payload.event_type)
        await action()
