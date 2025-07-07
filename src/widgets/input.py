from pathlib import Path
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from exceptions import MissingInformationError
from services.tts_service import TtsService
from settings import settings
from utils import is_compiled


class Input(QWidget):
    """Widget for text input and triggering speech synthesis."""

    status: Signal = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.input_field: QPlainTextEdit = QPlainTextEdit(self)
        self.input_field.setPlaceholderText("Enter text to synthesise...")
        _ = self.input_field.textChanged.connect(
            lambda: character_count.setText(
                f"Characters: {len(self.input_field.toPlainText())}"
            )
        )

        character_count = QLabel(self, text="Characters: 0")

        self.use_ssml: QCheckBox = QCheckBox("Use SSML", self)
        self.use_ssml.setCheckState(
            Qt.CheckState.Checked
            if settings.value("use_ssml", False, bool)
            else Qt.CheckState.Unchecked
        )
        _ = self.use_ssml.stateChanged.connect(
            lambda state: settings.setValue(
                "use_ssml", state == Qt.CheckState.Checked.value
            )
        )

        play_button = QPushButton("Play", self)
        play_button.setIcon(QIcon(self._get_resource("play.svg")))
        _ = play_button.clicked.connect(self._on_play)

        save_button = QPushButton("Save", self)
        save_button.setIcon(QIcon(self._get_resource("download.svg")))
        _ = save_button.clicked.connect(self._on_save)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(character_count)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.use_ssml)
        bottom_layout.addWidget(play_button)
        bottom_layout.addWidget(save_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.input_field)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def _get_resource(self, name: str):
        """Resolve the path to a resource file, adjusting for compiled mode.

        Args:
            name (str): Filename of the resource.

        Returns:
            str: Full filesystem path to the resource file.
        """
        basedir = Path(__file__).parent.parent

        if not is_compiled():
            basedir = basedir.parent

        return str(basedir / "resources" / name)

    def _on_save(self):
        """Handle the submit button click by synthesizing speech or emitting error status."""
        input = self.input_field.toPlainText().strip()

        try:
            if self.use_ssml.isChecked():
                TtsService.get_service().save_ssml_to_file_async(
                    input, self.status.emit
                )
            else:
                TtsService.get_service().save_text_to_file_async(
                    input, self.status.emit
                )
        except MissingInformationError:
            self.status.emit("Service information required to generate audio.")

    def _on_play(self):
        """Handle the play button click by synthesizing speech or emitting error status."""
        input = self.input_field.toPlainText().strip()

        try:
            if self.use_ssml.isChecked():
                TtsService.get_service().play_ssml_async(input, self.status.emit)
            else:
                TtsService.get_service().play_text_async(input, self.status.emit)
        except MissingInformationError:
            self.status.emit("Service information required to generate audio.")
