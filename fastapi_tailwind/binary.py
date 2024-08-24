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

binaries_path = Path(__file__).parent.joinpath("binaries")

def get_tailwind_binary_path() -> Optional[Path]:
    path: Optional[Path] = None 
    cpu_architecture = platform.machine().lower()

    cpu_architecture = MACHINE_TYPE_TO_TAILWIND_TYPE.get(cpu_architecture, cpu_architecture)

    if cpu_architecture == "i386": # tailwind doesn't support i386 to my understanding, correct me if I'm wrong.
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