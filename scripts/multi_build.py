# NOTE: This script must be run from the root of the repo, for example:
# python ./scripts/update_binaries

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import Dict, Tuple, List

import os
import sys
import time
import typer
import shutil
import logging
from pathlib import Path
from subprocess import Popen

from binary import bin_stash_folder_path, TAILWIND_VERSION, BinType, select

TAILWIND_PLATFORM_TO_PYPI_PLATFORM: Dict[str, Tuple[List[str], Dict[str, str]]] = {
    "linux": (
        ["manylinux2014"], 
        {
            "x64": "x86_64",
            "arm64": "aarch64",
            "armv7": "armv7l"
        }
    ),
    "linux-musl": (
        ["musllinux_1_2"],
        {
            "x64": "x86_64",
            "arm64": "aarch64",
            "armv7": "armv7l"
        }
    ),
    "windows": (
        ["win"], 
        {
            "x64": "amd64",
        }
    ),
    "macos": (
        ["macosx_10_9", "macosx_11_0"],
        {
            "x64": "x86_64",
            "arm64": "arm64"
        }
    )
}

app = typer.Typer()
logger = logging.getLogger("multi-build")

@app.command()
def multi_build(target_version: Optional[str] = typer.Option(None, "--target-version", "-v")):
    dist_folder_path = Path("./dist")
    dist_folder_path.mkdir(exist_ok = True)

    if target_version is None:
        target_version = TAILWIND_VERSION

    if not bin_stash_folder_path.exists():
        logger.error(
            f"The '{bin_stash_folder_path}' stash path does not exist! " \
                "Pull a binary before running a multi build: python scripts/binary.py pull linux-x64"
        )

        raise typer.Exit(1)

    build_cache_path = Path("./build")

    if build_cache_path.exists():
        shutil.rmtree(build_cache_path)

    build_output_path = dist_folder_path.joinpath(target_version)

    if build_output_path.exists():
        shutil.rmtree(build_output_path)

    for stashed_bin_path in bin_stash_folder_path.iterdir():

        if target_version not in stashed_bin_path.name:
            logger.debug(
                f"Ignoring '{stashed_bin_path}' as it is not the correct version tag ('{target_version}')..."
            )
            continue

        # this should never end up being none hence the strict type
        bin_type: BinType = None 

        for enum_bin_type in BinType:

            if enum_bin_type.value == "-".join(stashed_bin_path.name.split("-")[1:-1]).replace(".exe", ""):
                bin_type = enum_bin_type
                break

        assert bin_type is not None

        select(bin_type, target_version)

        operating_system, cpu_arch = bin_type.platform_split()

        platform_tags, tailwind_cpu_arch_to_pypi_cpu_arch = TAILWIND_PLATFORM_TO_PYPI_PLATFORM[operating_system]
        cpu_arch_tag = tailwind_cpu_arch_to_pypi_cpu_arch[cpu_arch]

        logger.info(f"Building package for '{bin_type}'...")
        popen = Popen(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                build_output_path.absolute()
            ]
        )

        popen.wait()

        built_wheel_path = None

        for wheel_path in build_output_path.iterdir():

            if wheel_path.is_file() and "-any.whl" in wheel_path.name:
                built_wheel_path = wheel_path
                break

        assert built_wheel_path is not None

        last_index = len(platform_tags) - 1

        for index, platform_tag in enumerate(platform_tags):
            destination_wheel_path = build_output_path.joinpath(
                built_wheel_path.name.replace("-any.whl", f"-{platform_tag}_{cpu_arch_tag}.whl")
            )

            logger.debug(f"Cloning built wheel into '{platform_tag}'...")

            if index == last_index:
                built_wheel_path.rename(destination_wheel_path)

            else:
                shutil.copyfile(
                    built_wheel_path,
                    destination_wheel_path
                )

                # because pypi doesn't like wheels with the same hash (can't upload multiple files with same hash)
                with open(destination_wheel_path, "ab") as file:
                    file.write(b"\x00") # yeah this is totally the same file pypi
                    # totally didn't just append a null byte

        logger.debug("Deleting build cache...")
        shutil.rmtree("./build")

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(level = logging.INFO)

    app()