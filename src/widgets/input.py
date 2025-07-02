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

from azure_service import speak_text_async
from exceptions import MissingInformationError
from utils import is_compiled


class Input(QWidget):
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
        basedir = Path(__file__).parent.parent

        if not is_compiled():
            basedir = basedir.parent

        return str(basedir / "resources" / name)

    def _on_submit(self):
        try:
            speak_text_async(self.input_field.toPlainText().strip())
        except MissingInformationError:
            self.status.emit("Service information required to generate audio.")
