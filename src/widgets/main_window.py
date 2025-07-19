from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from services.tts_service import TtsService
from widgets.input import Input
from widgets.settings import Settings
from widgets.task_worker import dispatch
from widgets.voice_selector import VoiceSelector


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("VocalScript")
        self.setCentralWidget(QWidget(self))
        self.setStatusBar(QStatusBar(self))

        self._msg_box: QMessageBox = QMessageBox(self)
        self._msg_box.setText(
            "Please wait while the service retrieves required files and data."
        )
        self._msg_box.setIcon(QMessageBox.Icon.Information)
        self._msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)

        self.settings: Settings = Settings(self)
        _ = self.settings.accepted.connect(self.on_settings_accept)
        _ = self.settings.status.connect(self.statusBar().showMessage)
        _ = (
            self.menuBar()
            .addAction("&Settings")
            .triggered.connect(lambda: self.settings.open())
        )

        self.voice_selector: VoiceSelector = VoiceSelector(self.centralWidget())
        _ = self.voice_selector.status.connect(
            lambda msg: self.statusBar().showMessage(msg)
        )

        self.input: Input = Input(self.centralWidget())
        _ = self.input.status.connect(lambda msg: self.statusBar().showMessage(msg))

        self.main_layout: QVBoxLayout = QVBoxLayout(self.centralWidget())
        self.main_layout.addWidget(self.voice_selector)
        self.main_layout.addWidget(self.input)
        self.centralWidget().setLayout(self.main_layout)

    @Slot()
    def on_settings_accept(self):
        """Block UI then switch services and get voices asynchronously."""

        def switch_service():
            TtsService.switch(self.settings.selected_service)
            return TtsService.get_service().voices

        dispatch(
            self,
            switch_service,
            success_slot=self._on_services_switched,
            error_slot=self._on_services_switch_error,
        )
        _ = self._msg_box.exec()

    @Slot(list)
    def _on_services_switched(self, voices: list[tuple[str, str]]):
        """Handle UI updates after service switch and voice retrieval.

        Args:
            voices (list[tuple[str, str]]): List of available voices.
        """
        self.input.check_ssml()
        self.voice_selector.load_voices(voices)
        self._msg_box.accept()

    @Slot(Exception)
    def _on_services_switch_error(self, _: Exception):
        self.statusBar().showMessage(
            "Setting up service failed. Please select service and try again"
        )
        self._msg_box.reject()
