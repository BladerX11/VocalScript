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

        self.combobox: QComboBox = QComboBox(self)
        self.combobox.setEditable(True)
        self.combobox.setInsertPolicy(self.combobox.InsertPolicy.NoInsert)
        self.combobox.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        completer = QCompleter(self.combobox.model(), self.combobox)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.combobox.setCompleter(completer)
        (self.combobox.lineEdit() or self.combobox).setPlaceholderText("Select a voice")
        _ = self.combobox.currentIndexChanged.connect(self._on_current_index_changed)

        self.load_voices()

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Voice"))
        layout.addWidget(self.combobox)
        layout.addStretch()
        self.setLayout(layout)

    def load_voices(self):
        """Fetch voices from the speech service and populate the combobox.

        Emits status bar messages if retrieval fails or no voices returned.
        """
        _ = self.combobox.currentIndexChanged.disconnect(self._on_current_index_changed)
        self.combobox.clear()
        service = TtsService.get_service()

        voices = service.voices

        if len(voices) == 0:
            self.status.emit(
                "No voices retrieved. Ensure service information is correct."
            )
            return

        for name, code in voices:
            self.combobox.addItem(name, code)

        voice_key = service.type().value + "/voice"

        if settings.contains(voice_key):
            idx = self.combobox.findData(settings.value(voice_key))

            if idx == -1:
                self.status.emit("Saved voice is invalid.")
            else:
                self.combobox.setCurrentIndex(idx)

        _ = self.combobox.currentIndexChanged.connect(self._on_current_index_changed)

    @Slot(int)
    def _on_current_index_changed(self, idx: int):
        """Handle combobox index change: update stored voice setting and synthesizer voice.

        Args:
            idx (int): New index selected in combobox.
        """
        data: str = self.combobox.itemData(idx)
        service = TtsService.get_service()
        settings.setValue(service.type().value + "/voice", data)
        service.voice = data
