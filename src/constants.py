import logging
import os
import sys
from pathlib import Path

RESOURCE_DIR = Path(__file__).resolve().parent
FROZEN = bool(getattr(sys, "frozen", False))
dev_mode = not FROZEN and (RESOURCE_DIR.parent / ".git").exists()


def get_logger(name: str) -> logging.Logger:
    formatter = " %(levelname)s | %(funcName)s| %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)
    return logging.getLogger(name)


def get_root():
    if dev_mode:
        return RESOURCE_DIR
    else:
        data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
        root_dir = data_home / "agemo/src"
        root_dir.mkdir(parents=True, exist_ok=True)
        return root_dir


def get_host_env():
    """Keep bundled libraries out of Hyprland and thumbnailer subprocesses."""
    env = os.environ.copy()
    if FROZEN:
        original = env.get("LD_LIBRARY_PATH_ORIG")
        if original is None:
            env.pop("LD_LIBRARY_PATH", None)
        else:
            env["LD_LIBRARY_PATH"] = original
    return env


if dev_mode:
    print("Running DEV")


__version__ = "2.8.0"
# returning strings for old os module
ROOT_DIR = get_root()
ASSETS_DIR = (RESOURCE_DIR if FROZEN else RESOURCE_DIR.parent) / "assets"
GLOBAL_VERSION = __version__
CACHE_FILE = ROOT_DIR / "xdgcache.json"
