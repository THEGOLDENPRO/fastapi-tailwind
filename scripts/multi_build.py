# NOTE: This script must be run from the root of the repo, for example:
# python ./scripts/update_binaries

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from typing import Dict, Tuple

import sys
import typer
import shutil
import logging
from pathlib import Path
from subprocess import Popen

from binary import bin_stash_folder_path, TAILWIND_VERSION, BinType, select

TAILWIND_PLATFORM_TO_PYPI_PLATFORM: Dict[str, Tuple[str, Dict[str, str]]] = {
    "linux": (
        "manylinux2014", 
        {
            "x64": "x86_64",
            "arm64": "aarch64",
            "armv7": "armv7l"
        }
    ),
    "linux-musl": (
        "musllinux_1_2",
        {
            "x64": "x86_64",
            "arm64": "aarch64",
            "armv7": "armv7l"
        }
    ),
    "windows": (
        "win", 
        {
            "x64": "amd64",
        }
    ),
    "macos": (
        "macosx_10_9",
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
        print(
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

        if not target_version in stashed_bin_path.name:
            logger.debug(
                f"Ignoring '{stashed_bin_path}' as it is not the correct version tag ('{target_version}')..."
            )
            continue

        # this should never end up being none hence the strict type
        bin_type: BinType = None 

        for enum_bin_type in BinType:

            if enum_bin_type.value in "-".join(stashed_bin_path.name.split("-")[:-1]):
                bin_type = enum_bin_type
                break

        assert bin_type is not None

        select(bin_type, target_version)

        os, cpu_arch = bin_type.platform_split()

        platform_tag, tailwind_cpu_arch_to_pypi_cpu_arch = TAILWIND_PLATFORM_TO_PYPI_PLATFORM[os]
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

        built_wheel_path.rename(
            build_output_path.joinpath(
                built_wheel_path.name.replace("-any.whl", f"-{platform_tag}_{cpu_arch_tag}.whl")
            )
        )

        logger.debug("Deleting build cache...")
        shutil.rmtree("./build")

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(level = logging.INFO)

    app()