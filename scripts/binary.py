from __future__ import annotations
from typing import Optional, List

import typer
import shutil
import logging
import requests
from enum import Enum
from pathlib import Path
from subprocess import Popen
from fastapi_tailwind.binary import get_tailwind_binary_path

from utils import write_bin_metadata, bin_name_generator

TAILWIND_VERSION = "4.0.3"
REPO_ID = "tailwindlabs/tailwindcss"

# TODO: use this to implement "pull all".
# NOTE: I don't think we need this as I think we'll be using BinType now for even 'pull all'. 
BINARY_CODENAMES = [
    "tailwindcss-linux-arm64",
    "tailwindcss-linux-arm64-musl",
    "tailwindcss-linux-x64",
    "tailwindcss-linux-x64-musl",
    "tailwindcss-macos-arm64",
    "tailwindcss-macos-x64",
    "tailwindcss-windows-x64.exe"
]

app = typer.Typer(no_args_is_help = True)

class BinType(str, Enum):
    LINUX_ARM64 = "linux-arm64"
    LINUX_ARM64_MUSL = "linux-arm64-musl"
    LINUX_X64 = "linux-x64"
    LINUX_X64_MUSL = "linux-x64-musl"
    MACOS_ARM64 = "macos-arm64"
    MACOS_X64 = "macos-x64"
    WINDOWS_X64 = "windows-x64"

    ALL = "all"

logger = logging.getLogger("binary")

bin_stash_folder_path = Path("./binary_stash")
library_bin_folder_path = Path("./fastapi_tailwind/binary")

logger.setLevel(logging.DEBUG)
logging.basicConfig(level = logging.INFO)

@app.command()
def pull(bin_type: BinType, version: Optional[str] = None, force: bool = False):
    bin_types_to_pull: List[BinType] = []

    if bin_type == BinType.ALL:
        bin_types_to_pull = [x for x in BinType if not x == BinType.ALL]
    else:
        bin_types_to_pull = [bin_type]

    if version is None:
        version = TAILWIND_VERSION

    for bin_type in bin_types_to_pull:
        bin_codename, tag_version = bin_name_generator(bin_type.value, version)

        destination_path = bin_stash_folder_path.joinpath(f"{bin_codename}-{tag_version}")

        if destination_path.exists() and force is False:
            logger.debug(f"'{destination_path.name}' is already pulled, skipping...")
            continue

        # TODO: move this code
        url = f"https://github.com/{REPO_ID}/releases/download/{tag_version}/{bin_codename}"

        logger.debug(f"Requesting download from --> {url}")
        request = requests.get(url)

        if not request.status_code == 200:
            logger.error(f"Failed to download tailwind bin from '{url}': {request}")
            raise typer.Exit(1)

        logger.debug(f"Writing --> {destination_path}")

        if not bin_stash_folder_path.exists():
            bin_stash_folder_path.mkdir()

        with destination_path.open("wb") as file:
            file.write(request.content)

        logger.info(f"Pulled '{bin_codename}' bin successfully!\n")

@app.command()
def select(bin_type: BinType, version: Optional[str] = None):

    if version is None:
        version = TAILWIND_VERSION

    tailwind_bin_name, tag_version = bin_name_generator(bin_type.value, version)

    binary_target_path = bin_stash_folder_path.joinpath(f"{tailwind_bin_name}-{tag_version}")
    binary_destination_path = library_bin_folder_path.joinpath(tailwind_bin_name) # yes, without tag version appended

    if not binary_target_path.exists():
        error_msg = f"That tailwind bin ({tailwind_bin_name}) does not exist! " \
            f"Make sure you have pulled it:\n   python scripts/binary pull {bin_type.value}"

        logger.error(error_msg)
        raise typer.Exit(1)

    logger.info("Cleaning up binary folder...")
    for binary_file in library_bin_folder_path.iterdir():

        if binary_file.name in [".gitkeep"]:
            continue

        logger.debug(f"Removing '{binary_file}'...")
        binary_file.unlink()

    logger.debug("\nWriting metadata file...")
    write_bin_metadata(library_bin_folder_path, version)

    logger.debug(f"Copying tailwindcss bin to {binary_destination_path}...")
    shutil.copy2(binary_target_path, binary_destination_path)

@app.command()
def exec(bin_args: Optional[List[str]] = typer.Argument(None)):
    """Execute the selected (or lib packaged) tailwindcss binary."""
    bin_path = get_tailwind_binary_path()

    if bin_path is None:
        logger.error("No binary is selected! Pull and select one.")
        raise typer.Exit(1)

    args = [
        str(bin_path.absolute())
    ]

    if bin_args is not None:
        args.extend(bin_args)

    popen = Popen(args)
    popen.wait()

if __name__ == "__main__":
    app()