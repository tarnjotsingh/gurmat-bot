import logging
import discord
from typing import Union
from discord.ext import commands
from datetime import datetime, timedelta
from utils import message_handler, user_usage_log


links = {
    "pratanakj": "http://72.29.64.55:9302/;",
    "dskirtan": "http://live16.sgpc.net:8000/;nocache=889869",
    "247kirtan": "http://janus.shoutca.st:8195/stream",
    "dgnlofi": "https://www.youtube.com/watch?v=tsshX6bWsNg"
}


class Station:
    url: str
    stream_alias: str
    start_time: str
    is_youtube: bool

    def __init__(self, stream_alias: str = "247kirtan", started_by: discord.Member = None):
        # If the provided stream alias doesn't exist, default to 247kirtan
        if stream_alias not in links:
            stream_alias = "247kirtan"

        self.logger = logging.getLogger("Station")
        self.logger.setLevel(logging.INFO)

        self.url: str = links[self.stream_alias]
        self.stream_alias: str = stream_alias
        self.started_by: discord.Member = started_by
        self.start_time = datetime.now()

    def get_runtime(self):
        self.logger.debug(f"get_runtime method for station {self.stream_alias} called")
        runtime = datetime.now() - self.start_time
        return runtime - timedelta(microseconds=runtime.microseconds)
