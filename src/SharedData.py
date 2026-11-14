import json
import os
import subprocess

from constants import ROOT_DIR, get_host_env, get_logger

logg = get_logger(__name__)


class SharedData:
    """
    This class load in memory data that the application uses
    @ self.data => default_settings {dict}
    @ self.thumbnails_data => json
    @ self.script_path => gets the directory of this program
    @self.selectedImage -> shared at runtime

    """

    def __init__(self):
        self.script_path = ROOT_DIR
        self.selectedImage = None
        self.data = self.load_settings()
        self.check_monitors()
        self.monitors = self.data["monitors"]

    @classmethod
    def load_settings(cls):
        default_settings = {
            "monitors": [],
            "splash": False,
            "ipc": True,
            "dpi": None,
            "wallpapers_dir": None,
        }

        try:
            with open(os.path.join(ROOT_DIR, "agemo.json"), "r") as f:
                file_data = json.load(f)
                return {**default_settings, **file_data}

        except FileNotFoundError:
            logg.error("Error: Configuration file not found. Creating agemo.json")

            with open(os.path.join(ROOT_DIR, "agemo.json"), "w") as f:
                json.dump(default_settings, f, indent=4)
                return default_settings

        except json.JSONDecodeError:
            logg.error("Error: Malformed JSON in.")
            return {}

    def check_monitors(self):
        try:
            hypr_ctl = subprocess.run(
                ["hyprctl", "monitors", "-j"],
                stdout=subprocess.PIPE,
                text=True,
                env=get_host_env(),
            )
            hold = json.loads(hypr_ctl.stdout)

            # returns list of monitor names
            monitors = [m.get("name") for m in hold]
            self.data["monitors"] = monitors

            # Auto populate Monitors
            with open(os.path.join(self.script_path, "agemo.json"), "w") as f:
                json.dump(self.data, f, indent=4)

        except Exception as e:
            logg.error(e)
