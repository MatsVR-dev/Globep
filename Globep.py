import tkinter as tk
from tkinter import filedialog
import pathlib as path
from pathlib import Path
import colorama
import time
import tempfile
import platform
import requests
import tqdm
from tqdm import tqdm
import zipfile
import shutil
import subprocess

temp_path = tempfile.gettempdir()
temp_path = Path(temp_path)
temp_path = Path(temp_path) / "Globep_TempFiles"

# make sure temp dir is empty
for item in Path(temp_path).iterdir():
    if item.is_file():
        item.unlink()
    elif item.is_dir():
        shutil.rmtree(item)

print("Select Game EXE file to inject BepinEx")
game_path = filedialog.askopenfilename(
    title="Select Unity Game EXE",
    filetypes=[("Executable Files", "*.exe")]
)
game = Path(game_path)

versions = {
    "win_x64" : "https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.5/BepInEx_win_x64_5.4.23.5.zip",
    "win_x86" : "https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.5/BepInEx_win_x86_5.4.23.5.zip",
    "lin_x64": "https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.5/BepInEx_linux_x64_5.4.23.5.zip",
    "lin_x86": "https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.5/BepInEx_linux_x86_5.4.23.5.zip",
    "mac": "https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.5/BepInEx_macos_universal_5.4.23.5.zip",
}

def download_file(url, folder, filename=None):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = url.split("/")[-1]

    file_path = folder / filename

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))

    with open(file_path, "wb") as f, tqdm(
        desc=filename,
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024
    ) as bar:

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    return str(file_path)

def unzip_file(zip_path, extract_to):
    extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def move_all(src, dst):
    src = Path(src)
    dst = Path(dst)

    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        target = dst / item.name

        if item.is_dir():
            if target.exists():
                move_all(item, target)
                item.rmdir()
            else:
                shutil.move(str(item), str(target))
        else:
            shutil.move(str(item), str(target))

def inject(version):
    bepinex = Path(temp_path)
    bepinex = Path(temp_path) / "bepinex"
    unzip_file(download_file(versions[version], temp_path, "bepinex_zipped.zip"), bepinex)
    move_all(bepinex, game_path)
    print("after game opens please close it")
    subprocess.run(game)
    print(colorama.Fore.GREEN + "INSTALL FINISHED")
    time.sleep(2)
    exit()

game_path = Path(game_path)
game_path = game_path.parent
temp_path.mkdir(exist_ok=True)

if (
    (game_path / "UnityPlayer.dll").is_file()
    and (game_path / "UnityCrashHandler64.exe").is_file()
    and (game_path / "MonoBleedingEdge").is_dir()
    and any(
        p.is_dir() and p.name.endswith("_Data")
        for p in game_path.iterdir()
    )
):
    os_name = platform.system()
    arch = platform.architecture()[0]
    if os_name == "Windows":
        if arch == "64bit":
            inject("win_x64")
        else:
            inject("win_x86")
    elif os_name == "Linux":
        if arch == "64bit":
            inject("lin_x64")
        else:
            inject("lin_x86")
    elif os_name == "Darwin": # MacOS
        inject("mac")
    else:
        print(colorama.Fore.RED + "Could Not Recognize Your Computer. Computer is recognized as " + colorama.Fore.BLUE + os_name)
        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("0...  Exiting")
        quit()
else:
    print(colorama.Fore.RED + "Game not recognised as a Unity game, exiting in")
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("0...  Exiting")
    quit()