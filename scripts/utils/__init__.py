from __future__ import annotations

from pathlib import Path

__all__ = ()

def write_bin_metadata(destination: Path, version: str):
    info_file = destination.joinpath("metadata.txt").open("w")
    info_file.write(f"""version: {version}""")
    info_file.close()

def bin_name_generator(bin_type_value: str, version: str) -> tuple[str, str]:
    tag_version = f"v{version.replace('v', '')}"

    bin_codename = f"tailwindcss-{bin_type_value}"

    if "windows" in bin_type_value:
        bin_codename += ".exe"

    return bin_codename, tag_version