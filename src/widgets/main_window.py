from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from widgets.input import Input
from widgets.settings import Settings
from widgets.voice_selector import VoiceSelector


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("VocalScript")
        self.setCentralWidget(QWidget(self))
        self.setStatusBar(QStatusBar())

        self.voice_selector = VoiceSelector(self.centralWidget())
        _ = self.voice_selector.status.connect(
            lambda msg: self.statusBar().showMessage(msg)
        )

        settings = Settings(self)
        _ = settings.accepted.connect(self._on_setting_accept)
        _ = (
            self.menuBar()
            .addAction("&Settings")
            .triggered.connect(lambda: settings.open())
        )

        self.input = Input(self.centralWidget())
        _ = self.input.status.connect(lambda msg: self.statusBar().showMessage(msg))

        main_layout: QVBoxLayout = QVBoxLayout(self.centralWidget())
        main_layout.addWidget(self.voice_selector)
        main_layout.addWidget(self.input)
        self.centralWidget().setLayout(main_layout)

    @Slot()
    def _on_setting_accept(self):
        self.voice_selector.load_voices()
        self.input.check_ssml()
