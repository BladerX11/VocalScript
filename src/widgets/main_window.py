from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from azure_service import speak_text_async
from exceptions import MissingInformationError
from utils import is_compiled
from widgets.settings import Settings
from widgets.status_bar import StatusBar
from widgets.voice_selector import VoiceSelector


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VocalScript")
        self.setCentralWidget(QWidget(self))
        self.setStatusBar(StatusBar(self))

        voice_selector = VoiceSelector(self)
        _ = voice_selector.status.connect(lambda msg: self.statusBar().showMessage(msg))

        settings = Settings(self)
        _ = settings.accepted.connect(lambda: voice_selector.load_voices())
        _ = (
            self.menuBar()
            .addAction("&Settings")
            .triggered.connect(lambda: settings.open())
        )

        self.input_field: QPlainTextEdit = QPlainTextEdit(self)

        submit_button = QPushButton("Save", self)
        submit_button.setIcon(QIcon(self._get_resource("download.svg")))
        _ = submit_button.clicked.connect(self._on_submit)

        main_layout: QVBoxLayout = QVBoxLayout(self.centralWidget())
        main_layout.addWidget(voice_selector, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.input_field)
        main_layout.addWidget(submit_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.centralWidget().setLayout(main_layout)

    def _get_resource(self, name: str):
        basedir = Path(__file__).parent.parent

        if not is_compiled():
            basedir = basedir.parent

        return str(basedir / "resources" / name)

    def _on_submit(self):
        try:
            speak_text_async(self.input_field.toPlainText().strip())
        except MissingInformationError:
            self.statusBar().showMessage(
                "Service information required to generate audio."
            )
