from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from azure_service import speak_text_async
from utils import is_compiled
from widgets.settings import Settings
from widgets.status_bar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VocalScript")
        self.setCentralWidget(QWidget(self))
        self.setStatusBar(StatusBar(self))

        _ = (
            self.menuBar()
            .addAction("&Settings")
            .triggered.connect(lambda: Settings(self).open())
        )

        self.input_field: QPlainTextEdit = QPlainTextEdit(self)

        submit_button = QPushButton("Save", self)
        submit_button.setIcon(QIcon(self._get_resource("download.svg")))
        _ = submit_button.clicked.connect(
            lambda: speak_text_async(self.input_field.toPlainText().strip())
        )

        main_layout: QVBoxLayout = QVBoxLayout(self.centralWidget())
        main_layout.addWidget(self.input_field)
        main_layout.addWidget(submit_button)
        self.centralWidget().setLayout(main_layout)

    def _get_resource(self, name: str):
        basedir = Path(__file__).parent.parent

        if not is_compiled():
            basedir = basedir.parent

        return str(basedir / "resources" / name)
