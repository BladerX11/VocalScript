from PySide6.QtCore import Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from exceptions import ServiceCreationException
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

        self._settings: Settings = Settings(self)
        _ = self._settings.accepted.connect(self.on_settings_accept)
        _ = self._settings.status.connect(self.statusBar().showMessage)
        _ = (
            self.menuBar()
            .addMenu("&Application")
            .addAction("&Settings")
            .triggered.connect(self._settings.open)
        )

        self._voice_selector: VoiceSelector = VoiceSelector(self.centralWidget())
        _ = self._voice_selector.status.connect(
            lambda msg: self.statusBar().showMessage(msg)
        )

        self._input: Input = Input(self.centralWidget())
        _ = self._input.status.connect(lambda msg: self.statusBar().showMessage(msg))

        self._main_layout: QVBoxLayout = QVBoxLayout(self.centralWidget())
        self._main_layout.addWidget(self._voice_selector)
        self._main_layout.addWidget(self._input)
        self.centralWidget().setLayout(self._main_layout)

    @Slot()
    def on_settings_accept(self):
        """Block UI then switch services and get voices asynchronously."""

        def switch_service():
            TtsService.switch(self._settings.selected_service)
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
        self._input.check_ssml()
        self._voice_selector.load_voices(voices)
        self._msg_box.accept()

    @Slot(Exception)
    def _on_services_switch_error(self, e: Exception):
        if isinstance(e, ServiceCreationxception):
            self.statusBar().showMessage(
                "Setting up service failed. Please select service and try again"
            )
        else:
            raise e
        self._msg_box.reject()
