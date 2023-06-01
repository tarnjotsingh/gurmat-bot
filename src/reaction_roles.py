import logging
from typing import Union

import discord
from discord import Message, Member, Embed, Role, RawReactionActionEvent, utils
from discord.ext import commands
from pymongo.database import Database
from validator_collection import checkers

from utils import user_usage_log, BOT_ID, DEFAULT_COLOUR


class ReactionRoles(commands.Cog):
    """Class for handling assigning of roles based on the provided reaction"""
    __slots__ = ['bot', 'db', 'logger']

    role = discord.SlashCommandGroup("role", "Configure roles for the current discord server")

    def __init__(self, bot: commands.Bot, db: Database):
        self.bot: commands.Bot = bot
        self.db: Database = db
        self.logger: logging.Logger = logging.getLogger("ReactionRoles")
        self.logger.setLevel(logging.INFO)

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    @role.command()
    async def list(self, ctx: discord.ApplicationContext, group_name: str):
        """
        List all roles configured for the provided group_name

        Arguments:
              group_name: str - The group associated with the reaction roles you want to list
        """
        # Get all roles (in an iterable) associated with the server the command was called from
        all_roles = ctx.guild.roles

        # Check provided group exists, find_one returns a dictionary type
        group = self.db.reaction_role_groups.find_one({'name': group_name.lower(), 'guild_id': ctx.guild.id})
        if not group:
            await self.send_invalid_group_msg(ctx, group_name)
            return

        db_rr = list(self.db.reaction_roles.find({'guild_id': ctx.guild.id, 'group_id': group['_id']}))
        mapped = list(map(lambda r: self.reaction_role_display_string(r, all_roles), db_rr))
        reactions = list(map(lambda r: r['reaction'], db_rr))
        image_url = group['image_url'] if 'image_url' in group else None

        roles_as_string = '\n\n'.join(mapped)
        desc = f"Reaction roles configured with group `{group_name}`.\n" \
               f"Each emoji has a server role associated with it. If you would like one of the roles listed you can " \
               f"click the associated emoji below this message.\n\n" \
               + roles_as_string
        embed = self.embed_builder(DEFAULT_COLOUR, f"{group_name.capitalize()} Roles", desc, image_url)

        # Send the interaction response for the slash command so that discord knows the command has been acknowledged
        interaction = await ctx.respond(f"Listing role group {group_name}")
        # Send a new message that we can easily track. Tracking the interactions is frustrating.
        message = await ctx.send(embed=embed)

        for r in reactions:
            await message.add_reaction(r)

        # Delete the interaction to clean up the chat
        await interaction.delete_original_response()
        await self.track_message(ctx, message, group)

    @staticmethod
    def reaction_role_display_string(r, all_roles):
        role = utils.get(all_roles, id=r['role_id'])
        return f"{r['reaction']} - {'!!ROLE DOES NOT EXIST!!' if not role else role.name}"

    @role.command()
    async def groups(self, ctx: discord.ApplicationContext):
        """
        List all groups configured for the current server
        """
        # Query database for all groups
        if ctx.guild_id:
            groups: list = list(self.db.reaction_role_groups.find({'guild_id': ctx.guild_id}))
            mapped = list(map(lambda g: f"- {g['name'].capitalize()}", groups))

            desc = f"All role groups configured for `{ctx.guild.name}`:\n\n"
            groups_as_string = '\n'.join(mapped)
            full_description = f"{desc}{groups_as_string}"
            groups_embed = self.embed_builder(DEFAULT_COLOUR, "Role Groups", full_description, None)

            await ctx.respond(embed=groups_embed)
        else:
            await ctx.respond("You cannot do this from a private chat...")

    @role.command(name="addgroup")
    async def add_group(self, ctx: discord.ApplicationContext, group_name: str, image_url: str = None):
        """
        Add a new server reaction role group

        Arguments:
            group_name string: Name of the new group you want to add
            img_url string: (Optional) Url for an optional image to associate with the group
        """
        if not checkers.is_url(image_url) and image_url:
            # TODO: Change this to an invalid URL message rather than invalid for clarity
            await self.send_invalid_args_msg(ctx, "Invalid URL provided, cannot add group")
            return

        # Add group to the database if previous validation succeeded
        if group_name:
            sanitised_group_name = group_name.lower()

            # Check if group already exists....
            group_check = self.db.reaction_role_groups.find_one({'name': sanitised_group_name, 'guild_id': ctx.guild.id})
            if group_check:
                await self.send_entry_exists_msg(ctx, "group", sanitised_group_name)
                return

            self.logger.info(f"Adding new group '{sanitised_group_name}' to database with guild_id '{ctx.guild.id} and image_url '{image_url}'")
            self.db.reaction_role_groups.insert_one(
                {
                    'guild_id': ctx.guild.id,
                    'name': sanitised_group_name,
                    'image_url': image_url
                }
            )

            await ctx.respond(f"Successfully add group `{sanitised_group_name}` 🙏🏼")

    @role.command(name="addreaction")
    async def add_reaction(self, ctx: discord.ApplicationContext, group_name: str, role_name: str, reaction: str):
        """
        Add a new server role reaction

        Arguments:
            reaction string: String value of the reaction
            role_name string: The role you want to associate with the reaction
            group string: The group you want to assign to the reaction role
        """
        # Validate args
        role: Role = utils.get(ctx.guild.roles, name=role_name)

        # Query db for group name to get group id and if a reaction role of the same type exists already
        group = self.db.reaction_role_groups.find_one({'name': group_name, 'guild_id': ctx.guild.id})
        rr_check = self.db.reaction_roles.find_one({'reaction': reaction, 'group_id': group['_id']})

        if rr_check:
            await self.send_entry_exists_msg(ctx, "reaction role", "")
            return

        if group and role:
            self.logger.info("Adding new reaction role")
            self.db.reaction_roles.insert_one(
                {
                    'guild_id': ctx.guild.id,
                    'group_id': group['_id'],
                    'role_id': role.id,
                    'reaction': reaction,
                }
            )
            await ctx.respond('Reaction role added 🙏🏼')
        elif not group:
            await self.send_invalid_group_msg(ctx, group_name)
        elif not role:
            await ctx.respond("Role doesn't exist")

    @role.command(name="removegroup")
    async def remove_group(self, ctx: discord.ApplicationContext, group_name: str):
        """
        Remove an existing server reaction role group

        This command also removes all roles configured under the given group, so you need to be sure that you
        REALLY want to remove the group.

        Arguments:
            group_name string: Name of the new group you want to remove
        """
        # Validate group details
        sanitised_group_name = group_name.lower()
        group_check = self.db.reaction_role_groups.find_one({'name': sanitised_group_name, 'guild_id': ctx.guild.id})
        if group_check:
            # If group exists, we need to remove it, but we also should check if there are roles
            # associated with the group
            group_rr = list(self.db.reaction_roles.find({'group_id': group_check['_id']}))
            # Remove all existing roles under the group
            for reaction in group_rr:
                await self.remove_reaction(ctx, sanitised_group_name, (reaction['reaction']))
            # Remove group after all associated roles have been removed
            self.db.reaction_role_groups.delete_one({'_id': group_check['_id']})
            await self.track_message(ctx, None, group_check)
            await ctx.respond(f"Reaction role group {sanitised_group_name} has been removed. All reaction roles "
                              f"associated with this group have also been removed.")
        else:
            await self.send_invalid_group_msg(ctx, sanitised_group_name)

    @role.command(name="removereaction")
    async def remove_reaction(self, ctx: discord.ApplicationContext, group_name: str, reaction_emoji: str):
        """
       Remove an existing server reaction role

        Arguments:
            reaction string: String value of the reaction
            group string: The group the existing reaction role is assigned to
        """
        # Query database for an existing reaction role with the given reaction and group_name
        group = self.db.reaction_role_groups.find_one({'name': group_name, 'guild_id': ctx.guild.id})
        rr_check = self.db.reaction_roles.find_one({'reaction': reaction_emoji, 'group_id': group['_id']})

        if rr_check:
            # Reaction role exists, we will attempt to remove it
            self.db.reaction_roles.delete_one({'_id': rr_check['_id']})
            await ctx.respond(f"Removed reaction {reaction_emoji} from group {group_name}")
        else:
            await self.send_invalid_reaction_msg(ctx, reaction_emoji, group_name)

    # Helper functions

    async def track_message(self, ctx: discord.ApplicationContext, message: Message, group: dict):
        channel_id = ctx.channel_id
        group_id = group['_id']

        # Check if message in the same channel and group_id is already tracked in database. Result is dict type.
        result = self.db.messages.find_one({'channel_id': channel_id, 'group_id': group_id})

        # If a reaction message already exists, then we need to replace it
        if result:
            msg_id = result['_id']

            try:
                # Find and delete the previously tracked message from the discord chat and from the database
                old_msg = await ctx.fetch_message(msg_id)
                await old_msg.delete()
            except discord.errors.NotFound as not_found:
                # Not found would mean the original message was deleted manually
                self.logger.info(f"Tracked message for group '{group['name']}' could not be found")

            # Once attempting to delete the old message has been done, we can remove the entry from the db
            self.db.messages.delete_one({'_id': msg_id})

            if message:
                self.db.messages.insert_one({'_id': message.id, 'channel_id': channel_id, 'group_id': group_id})
        elif message:
            # Add msg to db for tracking
            logging.info(f"message added for tracking {message.id}")
            self.db.messages.insert_one({'_id': message.id, 'channel_id': channel_id, 'group_id': group_id})

    async def send_invalid_args_msg(self, ctx: discord.ApplicationContext, description: str):
        embed = self.embed_builder(
            0xff0000,
            "Invalid arguments",
            "Refer to command help by typing `.help roles [sub_command]`",
            None
        )
        await ctx.respond(embed=embed)

    async def send_invalid_group_msg(self, ctx: discord.ApplicationContext, group_name: str):
        embed = self.embed_builder(
            0xff0000,
            "Invalid group",
            f"The group `{group_name}` does not exist",
            None
        )
        await ctx.respond(embed=embed)

    async def send_invalid_reaction_msg(self, ctx: discord.ApplicationContext, reaction: str, group_name: str):
        embed = self.embed_builder(
            0xff0000,
            "Invalid reaction",
            f"The reaction `{reaction}` has not been configured in the `{group_name}` group",
            None
        )
        await ctx.respond(embed=embed)

    async def send_entry_exists_msg(self, ctx: discord.ApplicationContext, entry_type: str, entry_name: str):
        embed = self.embed_builder(
            0xff0000,
            "Entry already exists",
            f"The {entry_type.casefold()} `{entry_name}` already exists",
            None
        )
        await ctx.respond(embed=embed)

    @staticmethod
    def embed_builder(colour, title, desc, img_url) -> Embed:
        embed = discord.Embed()
        embed.colour = colour
        embed.title = title
        embed.description = desc
        if img_url:
            embed.set_image(url=img_url)
        return embed


async def handle_role_assignment(payload: RawReactionActionEvent, user: Member, database: Database):
    # Try and load Cursor object from messages collection that has the exact _id and channel_id pair
    msg_cursor = database.messages.find_one({'_id': payload.message_id, 'channel_id': payload.channel_id})
    emoji_name = str(payload.emoji) if payload.emoji.is_custom_emoji() else payload.emoji.name
    if msg_cursor and not payload.user_id == BOT_ID:
        # Query database to get role associated with the given reaction
        r_obj = database.reaction_roles.find_one({'guild_id': payload.guild_id, 'reaction': emoji_name})
        role: Role = discord.utils.get(user.guild.roles, id=r_obj['role_id'])

        switch = {
            'REACTION_ADD': lambda: user.add_roles(role),
            'REACTION_REMOVE': lambda: user.remove_roles(role)
        }

        action = switch.get(payload.event_type)
        await action()
