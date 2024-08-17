from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

import sys
import logging
from pathlib import Path
from subprocess import Popen

from .errors import OSNotSupported
from .binary import get_tailwind_binary_path

__all__ = (
    "compile"
)

logger = logging.getLogger(__name__)

def compile(
    output_stylesheet_path: str,
    tailwind_stylesheet_path: Optional[str] = None,
    watch: Optional[bool] = None,
    minify: bool = False,
    poll: bool = False,
    autoprefixer = True
) -> Popen:
    """
    Compiles your TailwindCSS to the output css path you set.

    Params:
        output_stylesheet_path: The path to output your TailwindCSS stylesheet file (css). It typically should be placed where ever your fastapi static dir is.
        tailwind_stylesheet_path: Path to the TailwindCSS input stylesheet file. (e.g input.css, style.css)
        watch: Let TailwindCSS watch for file changes and rebuild if needed. (`True` by default in FastAPI dev mode)
        minify: Minify the TailwindCSS output.
        poll: Tell TailwindCSS to use polling instead of filesystem events when watching.
        autoprefixer: Disable / enable TailwindCSS autoprefixer. (`True` by default)
    """
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

    if minify is True:
        args.append("--minify")

    if poll is True:
        args.append("--poll")

    if autoprefixer is False:
        args.append("--no-autoprefixer")

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