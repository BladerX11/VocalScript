from pathlib import Path
import sys


def get_folder():
    folder = Path(sys.argv[0]).parent

    if "__compiled__" not in globals():
        folder = folder.parent

    return folder
