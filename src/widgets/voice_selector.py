from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from services.tts_service import TtsService
from settings import settings


class VoiceSelector(QWidget):
    """Widget to select speech synthesis voice."""

    status: Signal = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._combobox: QComboBox = QComboBox(self)
        self._combobox.setEditable(True)
        self._combobox.setInsertPolicy(self._combobox.InsertPolicy.NoInsert)
        self._combobox.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        completer = QCompleter(self._combobox.model(), self._combobox)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._combobox.setCompleter(completer)
        (self._combobox.lineEdit() or self._combobox).setPlaceholderText(
            "Select a voice"
        )
        _ = self._combobox.currentIndexChanged.connect(self._on_current_index_changed)

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Voice"))
        layout.addWidget(self._combobox)
        layout.addStretch()
        self.setLayout(layout)

    @Slot(int)
    def _on_current_index_changed(self, _: int):
        """Handle combobox index change: update stored voice setting and synthesizer voice.

        Args:
            idx (int): New index selected in combobox.
        """
        data: str = self._combobox.currentData()
        service = TtsService.get_service()
        settings.setValue(service.voice_key(), data)
        service.voice = data

    def load_voices(self, voices: list[tuple[str, str]]):
        """Populate the combobox with a given list of voices.

        Args:
            voices (list[tuple[str, str]]): List of tuples containing voice names and codes.
        """
        _ = self._combobox.currentIndexChanged.disconnect(
            self._on_current_index_changed
        )
        self._combobox.clear()
        service = TtsService.get_service()

        for name, code in voices:
            self._combobox.addItem(name, code)

        idx = self._combobox.findData(service.voice)

        if idx == -1:
            self.status.emit(
                f"{'Saved' if settings.contains(service.voice_key()) else 'Default'} voice is invalid."
            )
        else:
            self._combobox.setCurrentIndex(idx)

        _ = self._combobox.currentIndexChanged.connect(self._on_current_index_changed)
