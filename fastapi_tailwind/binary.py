from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Optional, Any, Dict

import os
import platform
from pathlib import Path
from subprocess import Popen

MACHINE_TYPE_TO_TAILWIND_TYPE: Dict[str, str] = {
    "x86_64": "x64",
    "amd64": "x64",
    "aarch64": "arm64",
    "armv7l": "armv7"
}

binary_path = Path(__file__).parent.joinpath("binary")

def get_tailwind_binary_path() -> Optional[Path]:
    path: Optional[Path] = None 

    operating_system: Literal["Windows", "Linux", "Darwin"] | Any = platform.system()

    for file_path in binary_path.glob("*"):

        if file_path.is_file() and "tailwindcss" in file_path.name:
            path = file_path
            break

    # TODO: before this step, let's check the binary checksum.

    if path is None:
        return path

    if operating_system == "Linux" or operating_system == "Darwin":
        # On linux and mac the binary is required to be made executable.
        #path: Path

        is_executable = os.access(path, os.X_OK)

        if not is_executable:
            Popen(["chmod", "+x", path.absolute()]).wait()

    return path