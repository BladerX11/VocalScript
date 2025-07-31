from pathlib import Path
from typing import cast

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from services.clone_service import CloneService
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
        _ = self._combobox.activated.connect(self._on_activate)
        _ = self._combobox.currentIndexChanged.connect(self._on_current_index_changed)

        self._selected_sample: QLabel = QLabel(self)

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Voice"))
        layout.addWidget(self._combobox)
        layout.addWidget(self._selected_sample)
        layout.addStretch()
        self.setLayout(layout)

    def _is_cloning(self):
        """Return True if current service supports cloning and combobox is set to clone mode."""
        service = TtsService.get_service()
        return (
            isinstance(service, CloneService)
            and self._combobox.currentData() == CloneService.CLONE_VOICE
        )

    def _update_selected_sample(self):
        """Check if the service is capable of cloning and show the selected sample voice."""
        if self._is_cloning():
            service = cast(CloneService, TtsService.get_service())
            self._selected_sample.setText(f"Selected sample: {service.sample_voice}")
            self._selected_sample.show()
        else:
            self._selected_sample.hide()

    @Slot(int)
    def _on_activate(self, _: int):
        """Handle combobox activation: update sample voice."""
        if not self._is_cloning():
            self._selected_sample.hide()
            return

        service = cast(CloneService, TtsService.get_service())
        selected_sample_voice = QFileDialog.getOpenFileName(
            self, "Select Sample Voice", "", "Audio Files (*.wav)"
        )[0]

        if selected_sample_voice:
            settings.setValue(service.sample_voice_key(), selected_sample_voice)
            service.sample_voice = Path(selected_sample_voice)

        self._update_selected_sample()

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

        if isinstance(service, CloneService):
            self._combobox.addItem("Clone a voice...", CloneService.CLONE_VOICE)
            self._combobox.insertSeparator(1)

        for name, code in voices:
            self._combobox.addItem(name, code)

        idx = self._combobox.findData(service.voice)

        if idx == -1:
            self.status.emit(
                f"{'Saved' if settings.contains(service.voice_key()) else 'Default'} voice is invalid."
            )
        else:
            self._combobox.setCurrentIndex(idx)

        self._update_selected_sample()
        _ = self._combobox.currentIndexChanged.connect(self._on_current_index_changed)
