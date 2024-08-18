# NOTE: This script must be run from the root of the repo, for example:
# python ./scripts/update_binaries

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Tuple

import sys
import shutil
import logging
from pathlib import Path
from subprocess import Popen

from update_binaries import BINARY_CODENAMES

TAILWIND_PLATFORM_TO_PYPI_PLATFORM: Dict[str, Tuple[str, Dict[str, str]]] = {
    "linux": (
        "manylinux2014", 
        {
            "x64": "x86_64",
            "arm64": "aarch64",
            "armv7": "armv7l"
        }
    ),
    "windows": (
        "win", 
        {
            "x64": "amd64"
        }
    ),
    "macos": (
        "macosx_11_0",
        {
            "x64": "x86_64"
        }
    )
}

logger = logging.getLogger("multi-build")

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    library_folder_path = Path("./fastapi_tailwind")
    binaries_folder_path = library_folder_path.joinpath("binaries")
    dist_folder_path = Path("./dist")

    custom_build_folder_path = Path("./custom_build")
    temp_dist_folder_path = custom_build_folder_path.joinpath("dist")
    temp_binaries_folder_path = custom_build_folder_path.joinpath("binaries")

    if custom_build_folder_path.exists():
        shutil.rmtree(custom_build_folder_path)

    custom_build_folder_path.mkdir(exist_ok = True)
    temp_dist_folder_path.mkdir(exist_ok = True)
    dist_folder_path.mkdir(exist_ok = True)

    if not binaries_folder_path.exists():
        print(
            f"The '{binaries_folder_path}' binaries path does not exist! " \
                "Be sure to run the update_binaries.py script first."
        )

        exit(1)

    shutil.move(binaries_folder_path, temp_binaries_folder_path.parent)

    for bin_path in list(temp_binaries_folder_path.iterdir()):

        if bin_path.name not in BINARY_CODENAMES:
            logger.debug(f"Ignoring '{bin_path}' as it is not a tailwind binary...")
            continue

        binaries_folder_path.mkdir(exist_ok = True)
        shutil.move(bin_path, binaries_folder_path)

        bin_platform = bin_path.stem.split("-")[1]

        platform_id, cpu_arch_converter = TAILWIND_PLATFORM_TO_PYPI_PLATFORM[bin_platform]

        cpu_arch = bin_path.stem.split("-")[-1]
        cpu_arch = cpu_arch_converter.get(cpu_arch, cpu_arch)

        output_path = temp_dist_folder_path.joinpath(f"{platform_id}_{cpu_arch}")
        output_path.mkdir()

        logger.info(f"Building for '{output_path}'...")
        popen = Popen(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                output_path.absolute()
            ]
        )

        popen.wait()

        logger.debug("Deleting build cache...")
        shutil.rmtree("./build")

        logger.debug(
            f"Moving binary '{bin_path.name}' back to temp binaries folder '{temp_binaries_folder_path}'..."
        )
        shutil.move(
            binaries_folder_path.joinpath(bin_path.name), temp_binaries_folder_path
        )

    logger.debug("Moving back all binaries...")
    binaries_folder_path.rmdir()
    shutil.move(temp_binaries_folder_path, binaries_folder_path)

    logger.debug("Renaming and moving all wheels to dist...")
    for platform_dist_path in temp_dist_folder_path.iterdir():
        wheel_file_path = next(platform_dist_path.iterdir())

        new_name = f"{wheel_file_path.stem.replace('-any', f'-{platform_dist_path.stem}')}.whl"

        wheel_file_path = wheel_file_path.rename(platform_dist_path.joinpath(new_name))

        shutil.move(wheel_file_path, dist_folder_path)

    logger.debug("Duplicating manylinux wheels to make musllinux wheels...")

    for wheel_path in dist_folder_path.iterdir():

        if not "manylinux2014" in wheel_path.stem:
            continue

        new_name = f"{wheel_path.stem.replace('-manylinux2014', '-musllinux_0_5')}.whl"

        new_wheel_path = dist_folder_path.joinpath(new_name)

        print(">>", new_wheel_path)

        shutil.copy(wheel_path, new_wheel_path)