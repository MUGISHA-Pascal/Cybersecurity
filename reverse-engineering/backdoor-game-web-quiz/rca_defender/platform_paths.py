from __future__ import annotations

import os
from pathlib import Path


def get_app_data_dir(app_folder_name: str = "RCA-Defender") -> Path:
    """
    Return a per-user writable application data directory.

    Windows: %APPDATA%\\<app_folder_name>
    Linux:   $XDG_DATA_HOME/<app_folder_name> or ~/.local/share/<app_folder_name>
    """
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / app_folder_name
        return Path.home() / "AppData" / "Roaming" / app_folder_name

    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / app_folder_name
    return Path.home() / ".local" / "share" / app_folder_name

