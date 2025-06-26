import logging
from PySide6.QtCore import QSettings

from utils import from_data_dir, is_compiled

_logger = logging.getLogger(__name__)
QSettings.setDefaultFormat(QSettings.Format.IniFormat)

try:
    settings = (
        QSettings()
        if is_compiled()
        else QSettings(
            str(from_data_dir("vocalscript.ini")), QSettings.Format.IniFormat
        )
    )
except OSError as e:
    _logger.error(
        "Creating settings file failed. Using system settings. Error: %s",
        e.strerror,
        exc_info=e,
    )
    settings = QSettings()
