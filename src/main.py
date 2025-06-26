from PySide6.QtWidgets import QApplication

QApplication.setApplicationName("vocalscript")
QApplication.setOrganizationName("vocalscript")
QApplication.setApplicationDisplayName("VocalScript")

import logging  # noqa: E402
import sys  # noqa: E402

from utils import from_data_dir  # noqa: E402
from widgets.main_window import MainWindow  # noqa: E402

app = QApplication(sys.argv)
try:
    logging.basicConfig(
        filename=str(from_data_dir("vocalscript.log")), level=logging.INFO
    )
except OSError as e:
    logging.error(
        "Creating log file failed. Using standard logger. Error: %s",
        e.strerror,
        exc_info=e,
    )

MainWindow().show()
sys.exit(app.exec())
