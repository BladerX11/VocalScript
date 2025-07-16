from PySide6.QtWidgets import QApplication

QApplication.setApplicationName("vocalscript")
QApplication.setOrganizationName("vocalscript")
QApplication.setApplicationDisplayName("VocalScript")

import logging  # noqa: E402

from utils import from_data_dir, is_compiled  # noqa: E402

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

import sys  # noqa: E402

from std_logger import StderrToLogger  # noqa: E402

if is_compiled():
    sys.stderr = StderrToLogger()

from widgets.main_window import MainWindow  # noqa: E402

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.on_settings_accept()
sys.exit(app.exec())
