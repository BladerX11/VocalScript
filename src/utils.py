from pathlib import Path
import sys


def from_executable(path: str | None = None):
    location = Path(sys.argv[0]).parent

    if "__compiled__" not in globals():
        location = location.parent

    if path is not None:
        location = location / path

    return location
