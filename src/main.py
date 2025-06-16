import sys

from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication

from widgets.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()
QtAsyncio.run()
