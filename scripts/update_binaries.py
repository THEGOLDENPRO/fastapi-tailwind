import os
import shutil
import requests
from pathlib import Path

REPO_ID = "tailwindlabs/tailwindcss"

binaries_folder_path = Path("./fastapi_tailwind/binaries")

if binaries_folder_path.exists():

    for binary_file in binaries_folder_path.iterdir():
        binary_file.unlink()

else:
    binaries_folder_path.mkdir()

tag_version = requests.get(f"https://api.github.com/repos/{REPO_ID}/tags").json()[0]["name"]

binary_codenames = [
    "tailwindcss-linux-arm64",
    "tailwindcss-linux-armv7",
    "tailwindcss-linux-x64",
    "tailwindcss-macos-arm64",
    "tailwindcss-macos-x64",
    "tailwindcss-windows-arm64.exe",
    "tailwindcss-windows-x64.exe"
]

for bin_codename in binary_codenames:
    request = requests.get(
        f"https://github.com/{REPO_ID}/releases/download/latest"
    )

    bin_name, extension = os.path.splitext(bin_codename)

    file = binaries_folder_path.joinpath(f"{bin_name}-{tag_version}{extension}").open("wb")

    file.write(request.content)

    file.close()