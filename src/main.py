import logging
import sys

from PySide6.QtWidgets import QApplication

from widgets.main_window import MainWindow

logging.basicConfig(filename="vocalscript.log", level=logging.INFO)
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
