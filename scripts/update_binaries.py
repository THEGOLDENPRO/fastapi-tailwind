# NOTE: This script must be run from the root of the repo, for example:
# python ./scripts/update_binaries

import requests
from pathlib import Path

REPO_ID = "tailwindlabs/tailwindcss"

BINARY_CODENAMES = [
    "tailwindcss-linux-arm64",
    "tailwindcss-linux-armv7",
    "tailwindcss-linux-x64",
    "tailwindcss-macos-arm64",
    "tailwindcss-macos-x64",
    "tailwindcss-windows-arm64.exe",
    "tailwindcss-windows-x64.exe"
]

if __name__ == "__main__":
    binaries_folder_path = Path("./fastapi_tailwind/binaries")

    if binaries_folder_path.exists():

        for binary_file in binaries_folder_path.iterdir():
            binary_file.unlink()

    else:
        binaries_folder_path.mkdir()

    # Get latest tag version.
    tag_version = requests.get(f"https://api.github.com/repos/{REPO_ID}/tags").json()[0]["name"]

    info_file = binaries_folder_path.joinpath("info.txt").open("w")
    info_file.write(f"""version: {tag_version}""")
    info_file.close()

    for bin_codename in BINARY_CODENAMES:
        url = f"https://github.com/{REPO_ID}/releases/download/{tag_version}/{bin_codename}"

        print(f"Requesting --> {url}")
        request = requests.get(url)

        print(f"Writing --> {bin_codename}\n")
        file = binaries_folder_path.joinpath(bin_codename).open("wb")

        file.write(request.content)

        file.close()