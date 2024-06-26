from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, Optional

import os
import typer
import subprocess
import pytermgui as ptg
from datetime import datetime
from dasbus.connection import SessionMessageBus
# from mpd import MPDClient

from .metadata import Metadata

__all__ = ()

app = typer.Typer()

_status: Tuple[int, Optional[Tuple[Metadata, str]]] = (0, None)

STATUS_UPDATE_RATE = int(os.environ.get("LR_STATUS_UPDATE_RATE", 2))

@app.command(help = "🏮 Display your music status in your Linux terminal.")
def main():
    bus = SessionMessageBus()

    def update_status(key: str) -> str:
        metadata = get_status(bus)[0]

        if key == "artist":
            return str(metadata.__getattribute__("artists")[0])

        return str(metadata.__getattribute__(key))

    def update_image(_) -> str:
        _, image_string = get_status(bus)

        # ptg.get_terminal().print(image_string, flush = False)

        return image_string

    ptg.tim.define("!image", update_image)
    ptg.tim.define("!status", update_status)

    with ptg.WindowManager() as manager:
        manager.layout.add_slot("Body")

        window = ptg.Window(
            "[!image]_[/!image]", 
            "[bold][!status]title[/!status] ~ [!status]artist[/!status][/]", 
            box = "EMPTY"
        )

        manager.add(window)

def get_status(bus: SessionMessageBus) -> Tuple[Metadata, str]:
    global _status

    if datetime.now().timestamp() >= _status[0] + STATUS_UPDATE_RATE:
        spotify_bus = bus.get_proxy(
            service_name = "org.mpris.MediaPlayer2.spotify", 
            object_path = "/org/mpris/MediaPlayer2"
        )

        metadata = Metadata(data = spotify_bus.Metadata)

        if _status[1] is None or not _status[1][0].image_url == metadata.image_url:
            print("HUH!")
            image_output = subprocess.check_output(
                ["kitty", "icat", metadata.image_url], 
                text = True
            )

        else:
            image_output = _status[1][1]

        _status = (datetime.now().timestamp(), (metadata, image_output))

    return _status[1]