import logging
import discord
from typing import Union
from datetime import datetime, timedelta


class Station:

    def __init__(self, name: str, url: str, started_by: discord.Member = None):
        if not name:
            raise InvalidStation("name", name)
        elif not url:
            raise InvalidStation("url", url)

        self.logger = logging.getLogger("Station")
        self.logger.setLevel(logging.INFO)

        self.name: str = name
        self.url: str = url
        self.started_by: discord.Member = started_by
        self.start_time: datetime = datetime.now()
        self.is_youtube: bool = True if "youtube" in self.url.lower() else False

    def logging(self, log_lvl: Union[int, str]):
        self.logger.setLevel(log_lvl)
        return self

    def get_runtime(self):
        self.logger.debug(f"get_runtime method for station {self.name} called")
        runtime = datetime.now() - self.start_time
        return runtime - timedelta(microseconds=runtime.microseconds)


class InvalidStation(Exception):
    """Raised when invalid station data is given"""
    def __init__(self, type: str, invalid_value: str):
        self.message = f"Invalid station {type} provided of: {invalid_value}"

