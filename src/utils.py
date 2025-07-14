from pathlib import Path
import sys

from PySide6.QtCore import QStandardPaths


def is_compiled():
    """Return whether the application is running in compiled mode.

    Returns:
        bool: True if running as a compiled executable, False otherwise.
    """
    return hasattr(sys, "_MEIPASS")


def from_data_dir(path: str | None = None):
    """Get the application data directory path, optionally appending a subpath.

    Args:
        path (str | None): Optional relative path or filename under the data directory.

    Returns:
        Path: A pathlib.Path to the data directory or the specific file/directory.

    Raises:
        PermissionError: If compiled and the writable location cannot be determined.
        FileExistsError: If a file exists where a directory needs to be created.
        OSError: For other filesystem-related errors when creating directories.
    """
    if is_compiled():
        folder = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )

        if len(folder) == 0:
            raise PermissionError

        location = Path(folder)
    else:
        location = Path(__file__).parent.parent / "data"

    location.mkdir(parents=True, exist_ok=True)

    if path is not None and len(path) > 0:
        location = location / path

    return location
