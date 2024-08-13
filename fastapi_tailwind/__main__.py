from __future__ import annotations
from typing import Optional, List

import typer
import subprocess

from .tailwind import get_tailwind_binary_path

app = typer.Typer(
    pretty_exceptions_enable = False, 
    help = ""
)

@app.command()
def command(
    command_args: Optional[List[str]] = typer.Argument(
        None, help = "Args to pass directly to ``tailwindcss init``."
    )
):
    """
    Executes the ``tailwindcss init`` command.

    To pass arguments and options directly to the tailwind command use "--" like so --> fastapi-tailwind-init -- --help
    """

    bin_path = get_tailwind_binary_path()

    if bin_path is None:
        print("Tailwind is not supported on this OS!")
        typer.Exit(1)

    args = [bin_path, "init"]

    if command_args is not None:
        args.extend(command_args)

    subprocess.check_call(args)