import logging
from typing import Union
from validator_collection import checkers
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
    async def list(self, ctx: commands.Context, group_name: str):
        """
        List all roles in the server

        Arguments:
              group_name: str - The group associated with the reaction roles you want to list
        """
        # Get all roles (in an iterable) associated with the server the command was called from
        all_roles = ctx.guild.roles

        # Check provided group exists
        group: Cursor = self.db.reaction_role_groups.find_one({'name': group_name.lower()})
        if not group:
            await self.send_invalid_group_msg(ctx, group_name)
            return

        db_rr = list(self.db.reaction_roles.find({'guild_id': ctx.guild.id, 'group_id': group.__getitem__('_id')}))
        mapped = list(map(lambda r: f"{r['reaction']} - {utils.get(all_roles, id=r['role_id']).name}", db_rr))
        reactions = list(map(lambda r: r['reaction'], db_rr))
        image_url = group['image_url'] if 'image_url' in group else None

        roles_as_string = '\n\n'.join(mapped)
        desc = f"Reaction roles configured with group `{group_name}`\n\n" + roles_as_string
        embed = self.embed_builder(0xffa900, f"{group_name.capitalize()} Roles", desc, image_url)

        message = await ctx.send(embed=embed)

        # TODO: Try and look for a faster method if possible
        for r in reactions:
            await message.add_reaction(r)

        await self.track_message(message)

    @roles.command()
    async def groups(self, ctx: commands.Context):
        # Query database for all groups
        groups: list = list(self.db.reaction_role_groups.find({'guild_id': ctx.guild.id}))
        mapped = list(map(lambda g: f"- {g['name'].capitalize()}", groups))

        desc = f"All role groups configured for `{ctx.guild.name}`:\n\n"
        groups_as_string = '\n'.join(mapped)
        embed = self.embed_builder(0xffa900, "Role Groups", desc + groups_as_string, None)

        await ctx.send(embed=embed)

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
            img_url string: (Optional) Url for an optional image to associate with the group
        """
        # TODO: Break this function down a bit. Move validators into a separate function. Easier testing that way.
        arg_list = list(args[0])

        # Validate group details
        if len(arg_list) >= 1:
            group_name = ''.join(arg_list[0])  # Mandatory
            group_check = self.db.reaction_role_groups.find_one({'name': group_name})
            if group_check:
                await self.send_entry_exists_msg(ctx, "group", group_name)
                return
        else:
            await self.send_invalid_args_msg(ctx)
            return

        # Default value is None unless provided as an argument where it will go through validation
        image_url = None
        if len(arg_list) == 2:
            url_string = ''.join(arg_list[1])   # Optional
            if checkers.is_url(url_string):
                image_url = url_string
            else:
                # TODO: Change this to an invalid URL message rather than invalid for clarity
                await self.send_invalid_args_msg(ctx)
                return

        # Add group to the database if previous validation succeeded
        if group_name:
            self.logger.info("Adding new reaction role group")
            self.db.reaction_role_groups.insert_one(
                {
                    'guild_id': ctx.guild.id,
                    'name': group_name,
                    'image_url': image_url
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
            # Validate args
            reaction: str = ''.join(arg_list[0])
            role: Role = utils.get(ctx.guild.roles, mention=''.join(arg_list[1]))
            group_name: str = ''.join(arg_list[2])

            # Query db for group name to get group id and if a reaction role of the same type exists already
            group: Cursor = self.db.reaction_role_groups.find_one({'name': group_name}, {'_id': 1})
            rr_check = self.db.reaction_roles.find_one({'reaction': reaction, 'group_id': group.__getitem__('_id')})

            if rr_check:
                await self.send_entry_exists_msg(ctx, "reaction role", "")
                return

            if group:
                self.logger.info("Adding new reaction role")
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
                await self.send_invalid_group_msg(ctx, group_name)

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
            "Refer to command help by typing `.help roles [sub_command]`",
            None)
        await ctx.send(embed=embed)

    async def send_invalid_group_msg(self, ctx: commands.Context, group_name: str):
        embed = self.embed_builder(
            0xff0000,
            "Invalid group",
            f"The group `{group_name}` does not exist",
            None)
        await ctx.send(embed=embed)

    async def send_entry_exists_msg(self, ctx: commands.Context, entry_type: str, entry_name: str):
        embed = self.embed_builder(
            0xff0000,
            "Entry already exists",
            f"The {entry_type.casefold()} `{entry_name}` already exists",
            None)
        await ctx.send(embed=embed)

    def embed_builder(self, colour, title, desc: str, img_url) -> Embed:
        embed = discord.Embed()
        embed.colour = colour
        embed.title = title
        embed.description = desc
        if img_url:
            embed.set_image(url=img_url)
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
