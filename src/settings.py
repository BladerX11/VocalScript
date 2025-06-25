from PySide6.QtCore import QSettings

from utils import get_folder

settings = QSettings(
    str((get_folder() / "vocalscript.ini")), QSettings.Format.IniFormat
)
