import logging
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from azure_service import speech_synthesizer
from widgets.settings import Settings
from widgets.status_bar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger: logging.Logger = logging.getLogger(__name__)

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
        submit_button.setIcon(QIcon(self.__get_resource("download.svg")))
        _ = submit_button.clicked.connect(self.__on_submit)

        main_layout: QVBoxLayout = QVBoxLayout(self.centralWidget())
        main_layout.addWidget(self.input_field)
        main_layout.addWidget(submit_button)
        self.centralWidget().setLayout(main_layout)

    def __on_submit(self):
        text = self.input_field.toPlainText().strip()
        self.logger.info(f"Synthesising started for: {text}")
        _ = speech_synthesizer.speak_text_async(text)

    def __get_resource(self, name: str):
        basedir = Path(__file__).parent.parent

        if "__compiled__" not in globals():
            basedir = basedir.parent

        return str(basedir / "resources" / name)
