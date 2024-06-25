from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

import typer
from mpd import MPDClient

__all__ = ()

app = typer.Typer()

@app.command(help = "🏮 Display your music status in your Linux terminal.")
def main():
    client = MPDClient()               # create client object
    client.timeout = 10                # network timeout in seconds (floats allowed), default: None
    client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
    client.connect("localhost", 6600)  # connect to localhost:6600
    print(client.mpd_version)          # print the MPD version
    print(client.find("any", "house")) # print result of the command "find any house"
    client.close()                     # send the close command
    client.disconnect()