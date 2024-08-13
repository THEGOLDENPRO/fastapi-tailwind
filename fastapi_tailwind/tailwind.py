from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Optional, Any

    from fastapi import FastAPI

import os
import logging
import platform
from pathlib import Path
from subprocess import Popen

from .errors import OSNotSupported

__all__ = (
    "watch"
)

logger = logging.getLogger(__name__)

binaries_path = Path(__file__).parent.joinpath("binaries")

def watch(
    output_stylesheet_path: str,
    tailwind_stylesheet_path: Optional[str] = None
) -> Popen:
    bin_path = get_tailwind_binary_path()

    if bin_path is None: # What OS would you even be on for this to even occur. 💀
        raise OSNotSupported(
            "Tailwind doesn't support this Operating System! " \
                "These are the only supported binaries: https://github.com/tailwindlabs/tailwindcss/releases"
        )

    output_stylesheet = Path(output_stylesheet_path)

    args = [
        str(bin_path.absolute()),
        "--watch",
        "-o",
        output_stylesheet,
    ]

    if tailwind_stylesheet_path is not None:
        tailwind_stylesheet_path: Path = Path(tailwind_stylesheet_path)

        if not tailwind_stylesheet_path.exists():
            raise FileNotFoundError(
                f"The tailwind stylesheet file specified doesn't exist at '{tailwind_stylesheet_path}'!"
            )

        args.extend(
            [
                "-i", str(tailwind_stylesheet_path.absolute())
            ]
        )

    logger.info("Calling tailwind to compile...")

    return Popen(args)


def get_tailwind_binary_path() -> Optional[Path]:
    cpu_architecture = platform.machine()

    if cpu_architecture == "x86_64":
        cpu_architecture = "x64" # tailwind bin is tagged with x64.

    operating_system: Literal["Windows", "Linux", "Darwin"] | Any = platform.system()

    if operating_system == "Windows":
        return binaries_path.joinpath(f"tailwindcss-windows-{cpu_architecture}.exe")

    elif operating_system == "Darwin":
        return binaries_path.joinpath(f"tailwindcss-macos-{cpu_architecture}")

    elif operating_system == "Linux":
        path = binaries_path.joinpath(f"tailwindcss-linux-{cpu_architecture}")

        # On linux the binary is required to be executable.
        is_executable = os.access(path, os.X_OK)

        if not is_executable:
            Popen(["chmod", "+x", path.absolute()]).wait()

        return path

    return None