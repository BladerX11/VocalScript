from pathlib import Path

from PySide6.QtCore import QStandardPaths


def is_compiled():
    return "__compiled__" in globals()


def from_data_dir(path: str | None = None):
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
