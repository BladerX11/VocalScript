from PySide6.QtCore import QSettings

from utils import from_executable

settings = QSettings(
    str(from_executable("vocalscript.ini")), QSettings.Format.IniFormat
)
