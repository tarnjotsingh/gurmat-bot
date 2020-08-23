import logging
import discord
from typing import Union
from discord.ext import commands
from datetime import datetime, timedelta
from utils import message_handler, user_usage_log


links = {
    "pratanakj": "http://72.29.64.55:9302/;",
    "dskirtan": "http://live16.sgpc.net:8000/;nocache=889869",
    "247kirtan": "http://janus.shoutca.st:8195/stream"
}


class Station:
    url: str = None
    stream_alias: str = None
    start_time: str = None 
    logger = logging.getLogger("Station")

    def __init__(self, stream_alias: str = "247kirtan", started_by: discord.Member = None):
        # If the provided stream alias doesn't exist, default to 247kirtan
        if stream_alias not in links:
            stream_alias = "247kirtan"

        self.stream_alias = stream_alias
        self.url = links[self.stream_alias]
        self.started_by = started_by
        self.start_time = datetime.now()
        self.logger.setLevel(logging.INFO)

    def get_runtime(self):
        self.logger.debug(f"get_runtime method for station {self.stream_alias} called")
        runtime = datetime.now() - self.start_time
        return runtime - timedelta(microseconds=runtime.microseconds)


class Radio:
    # Radio will have a station which can be set up accordingly since they all use the station object
    def __init__(self, log_lvl: Union[int, str] = logging.INFO):
        self.station: Station = None
        self.logger = logging.getLogger("Radio")
        self.logger.setLevel(log_lvl)

    async def join(self, ctx: commands.Context):
        self.logger.info(user_usage_log(ctx))
        connected = ctx.message.author.voice
        if connected:
            await ctx.message.add_reaction('🙏🏼')
            await connected.channel.connect()
        else:
            await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, you need to join a voice channel first ji")

    async def leave(self, ctx: commands.Context):
        self.logger.info(user_usage_log(ctx))
        if ctx.voice_client:
            await ctx.message.add_reaction('🙏🏼')
            await ctx.voice_client.disconnect()
            self.station = None
        else:
            await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, I'm not in a voice channel")

    async def play(self, ctx: commands.Context, stream_alias: str = "247kirtan"):
        self.logger.info(user_usage_log(ctx))

        # Check if the bot IS NOT connected to a voice chat already. If it is not in a voice chat then call the join()
        # command to add it to the voice channel the author of the message is currently in.
        if not ctx.voice_client:
            await self.join(ctx)

        # Set the station object
        if self.station and self.station.stream_alias.__eq__(stream_alias):
            await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, the selected station is already playing ji")
        else:
            self.station = Station(stream_alias, ctx.author)
            # Restart/Start the stream based on if something is already playing
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            ctx.voice_client.play(source=discord.FFmpegPCMAudio(self.station.url))

    async def stop(self, ctx: commands.Context):
        self.logger.info(user_usage_log(ctx))

        if ctx.voice_client:
            await ctx.message.add_reaction('🙏🏼')
            ctx.voice_client.stop()
            self.station = None
        else:
            await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, there isn't anything playing ji")

    async def np(self, ctx: commands.Context):
        self.logger.info(user_usage_log(ctx))

        if ctx.voice_client and self.station:
            embed = discord.Embed()
            embed.colour = 0xffa900
            embed.description = f"Playing: {self.station.stream_alias}[{self.station.started_by.mention}]\nElapsed time: {self.station.get_runtime()}"
            await ctx.channel.send(embed=embed)
        else:
            await ctx.channel.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, there isn't anything playing ji")
