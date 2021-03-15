import logging
import discord
import asyncio
import youtube_dl

from typing import Union
from discord.ext import commands
from pymongo.database import Database, Collection

from station import Station
from utils import user_usage_log

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Radio(commands.Cog):
    # Radio will have a station which can be set up accordingly since they all use the station object
    def __init__(self, bot: commands.Bot, db: Database):
        self.station: Station = None
        self.bot: commands.Bot = bot
        self.db: Database = db
        self.stations: Collection = db.stations

        self.logger: logging.Logger = logging.getLogger("Radio")
        self.logger.setLevel(logging.INFO)

        # Log stations available from database
        # self.logger.info(list(self.stations.find()))

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    @commands.group(aliases=['rad'])
    async def radio(self, ctx: commands.Context):
        """Controls the playback of Kirtan radio stations"""
        self.logger.info(f"Invoked subcommand: {ctx.invoked_subcommand}")
        if ctx.invoked_subcommand is None:
            await ctx.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, invalid command ji")

    @radio.command()
    async def join(self, ctx: commands.Context):
        """Join the voice channel of the user that invoked the command"""

        self.logger.info(user_usage_log(ctx))
        connected = ctx.message.author.voice
        if connected:
            await ctx.message.add_reaction('🙏🏼')
            await connected.channel.connect()
        else:
            await ctx.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, you need to join a voice channel first ji")

    @radio.command()
    async def leave(self, ctx: commands.Context):
        """Leave the current voice channel"""

        self.logger.info(user_usage_log(ctx))
        if ctx.voice_client:
            await ctx.message.add_reaction('🙏🏼')
            await ctx.voice_client.disconnect()
            self.station = None
        else:
            await ctx.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, I'm not in a voice channel")

    @radio.command()
    async def play(self, ctx: commands.Context, station_name: str = "247"):
        """Start playing one of the predefined Kirtan radio stations"""

        self.logger.info(user_usage_log(ctx))

        # Check if the bot IS NOT connected to a voice chat already. If it is not in a voice chat then call the join()
        # command to add it to the voice channel the author of the message is currently in.
        if not ctx.voice_client:
            await self.join(ctx)

        # Set the station object
        if self.station and self.station.name.__eq__(station_name):
            await ctx.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, the selected station is already playing ji")
        else:
            # Query database to get station url
            station_link_db: Collection = self.stations.find_one({'name': station_name}, {'link': 1})
            self.station = Station(station_name, station_link_db['link'], ctx.author)
            # Restart/Start the stream based on if something is already playing
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()

            if self.station.is_youtube:
                self.logger.info(f"Will play youtube link {self.station.url}")
                await self._stream_yt(ctx, self.station.url)
            else:
                self.logger.info(f"Will play stream from link {self.station.url}")
                await self._stream_url(ctx, self.station.url)

    @radio.command()
    async def stop(self, ctx: commands.Context):
        """Stops the stream of the currently playing station"""

        self.logger.info(user_usage_log(ctx))

        if ctx.voice_client:
            await ctx.message.add_reaction('🙏🏼')
            ctx.voice_client.stop()
            self.station = None
        else:
            await ctx.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, there isn't anything playing ji")

    @radio.command()
    async def np(self, ctx: commands.Context):
        """Displays information about the current station being played"""

        self.logger.info(user_usage_log(ctx))

        if ctx.voice_client and self.station:
            embed = discord.Embed()
            embed.title = "Now Playing"
            embed.colour = 0xffa900
            embed.description = f"{self.station.name}[{self.station.started_by.mention}]\nElapsed time: {self.station.get_runtime()}"
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{ctx.author.mention} ਵਾਹਿਗੁਰੂ, there isn't anything playing ji")

    @radio.command()
    async def stations(self, ctx: commands.Context):
        """Lists all the available stations that can be chosen"""

        self.logger.info(user_usage_log(ctx))

        embed = discord.Embed()
        embed.title = "Available stations"

        # Replace links with database stuff
        stations_list = list(self.stations.find())
        # Want to use map to convert each of the dics in the list into a string
        station_strings = list(map(lambda stn: f"- {stn['name']}:\t\t{stn['link']}", stations_list))

        if station_strings:
            description = '\n'.join(station_strings)
            embed.colour = 0xffa900
        else:
            description = "No stations available"
            embed.color = 0x8B0000

        embed.description = description
        await ctx.send(embed=embed)

    async def _stream_yt(self, ctx: commands.Context, url: str):
        """Streams from a youtube url"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    async def _stream_url(self, ctx: commands.Context, url: str):
        """Streams from the provided url"""

        async with ctx.typing():
            ctx.voice_client.play(source=discord.FFmpegPCMAudio(self.station.url, **ffmpeg_options))
