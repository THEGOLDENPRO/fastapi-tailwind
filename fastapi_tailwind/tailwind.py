from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Optional, Any

import os
import sys
import logging
import platform
from pathlib import Path
from subprocess import Popen

from .errors import OSNotSupported

__all__ = (
    "compile"
)

logger = logging.getLogger(__name__)

binaries_path = Path(__file__).parent.joinpath("binaries")

def compile(
    output_stylesheet_path: str,
    tailwind_stylesheet_path: Optional[str] = None,
    watch: Optional[bool] = None,
) -> Popen:
    bin_path = get_tailwind_binary_path()

    if bin_path is None: # What OS would you even be on for this to even occur. 💀
        raise OSNotSupported(
            "Tailwind either doesn't support this operating system or CPU architecture! " \
                "These are the only supported binaries: https://github.com/tailwindlabs/tailwindcss/releases \n" \
                    "If this is incorrect please report it here: https://github.com/THEGOLDENPRO/fastapi-tailwind/issues"
        )

    output_stylesheet = Path(output_stylesheet_path)

    args = [
        str(bin_path.absolute()),
        "-o",
        output_stylesheet,
    ]

    # Set watch to true if in dev mode.
    if watch is None and ("--reload" in sys.argv or "dev" == sys.argv[1]):
        logger.debug("Setting watch to True as reload / development mode was detected...")
        watch = True

    if watch is True:
        args.append("--watch")

    if tailwind_stylesheet_path is not None:
        tailwind_stylesheet_path: Path = Path(tailwind_stylesheet_path)

        if not tailwind_stylesheet_path.exists():
            raise FileNotFoundError(
                f"The tailwind stylesheet file specified doesn't exist at '{tailwind_stylesheet_path}'!"
            )

        args.extend(
            [
                "-i", tailwind_stylesheet_path.absolute()
            ]
        )

    logger.info("Calling tailwind to compile...")

    return Popen(args)


def get_tailwind_binary_path() -> Optional[Path]:
    path: Optional[Path] = None 
    cpu_architecture = platform.machine()

    if cpu_architecture == "x86_64":
        cpu_architecture = "x64" # tailwind bin is tagged with x64.

    elif cpu_architecture == "i386": # tailwind doesn't support i386 to my understanding, correct me if I'm wrong.
        return None

    operating_system: Literal["Windows", "Linux", "Darwin"] | Any = platform.system()

    if operating_system == "Windows":
        path = binaries_path.joinpath(f"tailwindcss-windows-{cpu_architecture}.exe")

    elif operating_system == "Darwin":
        path = binaries_path.joinpath(f"tailwindcss-macos-{cpu_architecture}")

    elif operating_system == "Linux":
        path = binaries_path.joinpath(f"tailwindcss-linux-{cpu_architecture}")

        # On linux the binary is required to be executable.
        if path.exists():
            is_executable = os.access(path, os.X_OK)

            if not is_executable:
                Popen(["chmod", "+x", path.absolute()]).wait()

    if not path.exists():
        raise FileNotFoundError(
            f"Couldn't find the tailwindcss binary for '{operating_system}'! '{path}' does not exist!"
        )

    return path