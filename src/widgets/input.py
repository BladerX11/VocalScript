from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
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

from services.clone_service import CloneService
from services.ssml_service import SsmlService
from services.tts_service import TtsService
from settings import settings
from utils import is_compiled
from widgets.task_worker import dispatch


class Input(QWidget):
    """Widget for text input and triggering speech synthesis."""

    status: Signal = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._input_field: QPlainTextEdit = QPlainTextEdit(self)
        self._input_field.setPlaceholderText("Enter text to synthesise...")
        _ = self._input_field.textChanged.connect(
            lambda: character_count.setText(
                f"Characters: {len(self._input_field.toPlainText())}"
            )
        )

        character_count = QLabel(self, text="Characters: 0")

        self._use_ssml: QCheckBox = QCheckBox("Use SSML", self)
        self._use_ssml.setCheckState(
            Qt.CheckState.Checked
            if settings.value("use_ssml", False, bool)
            else Qt.CheckState.Unchecked
        )
        _ = self._use_ssml.stateChanged.connect(
            lambda state: settings.setValue(
                "use_ssml", state == Qt.CheckState.Checked.value
            )
        )

        self._play_button = QPushButton("Play", self)
        self._play_button.setIcon(QIcon(self._get_resource("play.svg")))
        _ = self._play_button.clicked.connect(self._on_play)

        self._save_button = QPushButton("Save", self)
        self._save_button.setIcon(QIcon(self._get_resource("download.svg")))
        _ = self._save_button.clicked.connect(self._on_save)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(character_count)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self._use_ssml)
        bottom_layout.addWidget(self._play_button)
        bottom_layout.addWidget(self._save_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self._input_field)
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

    @Slot()
    def _toggle_buttons(self):
        """Toggles the Play and Save buttons."""
        current_play = self._play_button.isEnabled()
        current_save = self._save_button.isEnabled()
        self._play_button.setEnabled(not current_play)
        self._save_button.setEnabled(not current_save)

    def _on_save(self):
        """Handle the submit button click by synthesizing speech or emitting error status."""
        service = TtsService.get_service()

        if isinstance(service, SsmlService) and self._use_ssml.isChecked():
            fn = service.save_ssml_to_file
        elif (
            isinstance(service, CloneService)
            and service.voice == CloneService.CLONE_VOICE
        ):
            fn = service.save_clone_to_file
        else:
            fn = service.save_text_to_file

        self._toggle_buttons()
        dispatch(
            self,
            lambda: fn(self._input_field.toPlainText().strip(), self.status.emit),
            finished_slot=self._toggle_buttons,
        )

    def _on_play(self):
        """Handle the play button click by synthesizing speech or emitting error status."""
        service = TtsService.get_service()

        if isinstance(service, SsmlService) and self._use_ssml.isChecked():
            fn = service.play_ssml
        elif (
            isinstance(service, CloneService)
            and service.voice == CloneService.CLONE_VOICE
        ):
            fn = service.play_clone
        else:
            fn = service.play_text

        self._toggle_buttons()
        dispatch(
            self,
            lambda: fn(self._input_field.toPlainText().strip(), self.status.emit),
            finished_slot=self._toggle_buttons,
        )

    def check_ssml(self):
        """Enable or disable SSML checkbox based on service support."""
        if isinstance(TtsService.get_service(), SsmlService):
            self._use_ssml.setEnabled(True)
        else:
            self._use_ssml.setEnabled(False)
