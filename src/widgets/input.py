from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from exceptions import MissingInformationError
from services.tts_service import TtsService
from utils import is_compiled


class Input(QWidget):
    """Widget for text input and triggering speech synthesis."""

    status: Signal = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        submit_button = QPushButton("Save", self)
        submit_button.setIcon(QIcon(self._get_resource("download.svg")))
        _ = submit_button.clicked.connect(self._on_submit)

        character_count = QLabel(self, text="Characters: 0")

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(character_count)
        bottom_layout.addStretch()
        bottom_layout.addWidget(submit_button)

        self.input_field: QPlainTextEdit = QPlainTextEdit(self)
        self.input_field.setPlaceholderText("Enter text to synthesise...")
        _ = self.input_field.textChanged.connect(
            lambda: character_count.setText(
                f"Characters: {len(self.input_field.toPlainText())}"
            )
        )

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

    def _on_submit(self):
        """Handle the submit button click by synthesizing speech or emitting error status."""
        try:
            TtsService.get_service().save_to_file_async(
                self.input_field.toPlainText().strip(), self.status.emit
            )
        except MissingInformationError:
            self.status.emit("Service information required to generate audio.")
