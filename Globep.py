import tkinter as tk
from tkinter import filedialog, ttk
import pathlib as path
from pathlib import Path
import tempfile
import platform
import requests
import zipfile
import shutil
import threading

temp_path = tempfile.gettempdir()
temp_path = Path(temp_path)
temp_path = Path(temp_path) / "Globep_TempFiles"
temp_path.mkdir(exist_ok=True)
game_path = ""
# make sure temp dir is empty
for item in Path(temp_path).iterdir():
    if item.is_file():
        item.unlink()
    elif item.is_dir():
        shutil.rmtree(item)

BEPINEX_VERSION = "5.4.23.5"
BASE_URL = (
    f"https://github.com/BepInEx/BepInEx/releases/download/v{BEPINEX_VERSION}/"
)

versions = {
    "win_x64": BASE_URL + f"BepInEx_win_x64_{BEPINEX_VERSION}.zip",
    "win_x86": BASE_URL + f"BepInEx_win_x86_{BEPINEX_VERSION}.zip",
    "lin_x64": BASE_URL + f"BepInEx_linux_x64_{BEPINEX_VERSION}.zip",
    "lin_x86": BASE_URL + f"BepInEx_linux_x86_{BEPINEX_VERSION}.zip",
    "mac": BASE_URL + f"BepInEx_macos_universal_{BEPINEX_VERSION}.zip",
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Globep")
        self.root.geometry("500x300")

        self.progress = ttk.Progressbar(
            root,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        # Frame for button + status text
        controls = ttk.Frame(root)
        controls.pack(pady=10)
        self.gamepath = ttk.Label(controls, text="Please choose a file")
        self.gamepath.pack(side="left", padx=(0, 10))

        self.pickfile = tk.Button(controls,text="Choose EXE",command=self.pick)
        self.pickfile.pack(side="left", padx=5)

        self.injectbutton = tk.Button(controls,text="Inject",command=self.injectstart, state="disabled")
        self.injectbutton.pack(side="left", padx=5)

        self.progress.pack(pady=5)

        self.log = tk.Text(root, height=20, width=60)
        self.log.pack(pady=10)

    def write_log(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)

    def injectstart(self):
        self.injectbutton.config(state="disabled")
        self.progress["value"] = 0
        self.log.delete("1.0", tk.END)
        os_name = platform.system()
        arch = platform.architecture()[0]
        if os_name == "Windows":
            if arch == "64bit":
                thread = threading.Thread(target=self.inject("win_x64"))
                thread.daemon = True
                thread.start()
            else:
                thread = threading.Thread(target=self.inject("win_x86"))
                thread.daemon = True
                thread.start()
        elif os_name == "Linux":
            if arch == "64bit":
                thread = threading.Thread(target=self.inject("lin_x64"))
                thread.daemon = True
                thread.start()
            else:
                thread = threading.Thread(target=self.inject("lin_x86"))
                thread.daemon = True
                thread.start()
        elif os_name == "Darwin":  # MacOS
            thread = threading.Thread(target=self.inject("mac"))
            thread.daemon = True
            thread.start()
        else:
            self.write_log("!FATAL_ERROR! Could Not Recognize Your PC")

    def download_file(self, url, folder, filename=None):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)

        if filename is None:
            filename = url.split("/")[-1]

        file_path = folder / filename

        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        self.write_log("downloading bepinex_zipped.zip: " + url)
        self.progress["maximum"] = total_size
        self.progress["value"] = 0

        with open(file_path, "wb") as f:
            downloaded = 0

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

                    downloaded += len(chunk)

                    self.progress["value"] = downloaded
                    self.root.update_idletasks()

        return str(file_path)

    def unzip_file(self, zip_path, extract_to):
        self.write_log("Unzipping: " + str(zip_path) + " To: " + str(extract_to))
        extract_to = Path(extract_to)
        extract_to.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

    def move_all(self, src, dst):
        self.write_log("Moving Files")
        src = Path(src)
        dst = Path(dst)

        dst.mkdir(parents=True, exist_ok=True)

        for item in src.iterdir():
            target = dst / item.name

            if item.is_dir():
                if target.exists():
                    self.move_all(item, target)
                    item.rmdir()
                else:
                    shutil.move(str(item), str(target))
            else:
                shutil.move(str(item), str(target))

    def inject(self, version):
        bepinex = Path(temp_path)
        bepinex = Path(temp_path) / "bepinex"
        self.unzip_file(self.download_file(versions[version], temp_path, "bepinex_zipped.zip"), bepinex)
        self.move_all(bepinex, game_path)
        self.write_log("Please run game atleast once before installing any plugins/mods")
        self.write_log("INSTALL FINISHED")
        self.injectbutton.config(state="normal")

    def pick(self):
        self.pickfile.config(state="disabled")
        self.write_log("Choose Game EXE")
        game_path = filedialog.askopenfilename(
            title="Select Unity Game EXE",
            filetypes=[("Executable Files", "*.exe")]
        )
        game_path = Path(game_path)
        game = Path(game_path)
        game_path = game_path.parent
        if (
                (game_path / "UnityPlayer.dll").is_file()
                and (game_path / "UnityCrashHandler64.exe").is_file()
                and (game_path / "MonoBleedingEdge").is_dir()
                and any(
            p.is_dir() and p.name.endswith("_Data")
            for p in game_path.iterdir()
        )
        ):
            self.write_log("Chose Game: " + str(game.name))
            self.gamepath.config(text=str(game.name))
            self.pickfile.config(state="normal")
            self.injectbutton.config(state="normal")
        else:
            self.write_log("Game Not Recognized as a valid unity game, Please try again")
            self.pickfile.config(state="normal")
            self.injectbutton.config(state="disabled")

root = tk.Tk()
app = App(root)
root.mainloop()
