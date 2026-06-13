"""Open files with the operating system's default application."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def open_file(path: str | Path) -> None:
    """Open ``path`` in the OS default application.

    Raises an exception when the file cannot be opened so callers can warn the
    user while still keeping the already-created file on disk.
    """
    target = os.fspath(path)
    if sys.platform.startswith("win"):
        os.startfile(target)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", target])
    else:
        subprocess.Popen(["xdg-open", target])
