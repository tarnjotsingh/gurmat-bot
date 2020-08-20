import os

links = {
    "pratanakj": "http://72.29.64.55:9302/;",
    "dskirtan": "http://live16.sgpc.net:8000/;nocache=889869",
    "247kirtan": "http://janus.shoutca.st:8195/stream"
}

class Station:
    url: str = None
    stream_alias: str = None
    start_time: str = None 

    def __init__(self, stream_alias: str = "247kirtan"):
        # If the provided stream alias doesn't exist, default to 247kirtan
        if stream_alias not in links:
            stream_alias = "247kirtan"

        self.stream_alias = stream_alias
        self.url = links[self.stream_alias]

    def get_runtime() -> int:
        pass
