from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QHBoxLayout,
    QLabel,
    QWidget,
)
from azure.cognitiveservices.speech import PropertyId, SynthesisVoicesResult

from azure_service import speech_synthesizer
from settings import settings


class VoiceSelector(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.combobox: QComboBox = QComboBox(self)
        self.combobox.setEditable(True)
        self.combobox.setInsertPolicy(self.combobox.InsertPolicy.NoInsert)

        completer = QCompleter(self.combobox.model(), self.combobox)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        self.combobox.setCompleter(completer)

        if settings.contains("endpoint"):
            voices_result = speech_synthesizer.get_voices_async().get()

            if isinstance(voices_result, SynthesisVoicesResult):
                for voice in voices_result.voices:
                    name_split = voice.short_name.split("-")
                    self.combobox.addItem(
                        f"{name_split[2]} ({'-'.join(name_split[:2])}) ({voice.gender.name})",
                        voice.short_name,
                    )

            if settings.contains("voice"):
                self.combobox.setCurrentIndex(
                    self.combobox.findData(settings.value("voice"))
                )
            else:
                self.combobox.setCurrentIndex(-1)
                self.combobox.setPlaceholderText("Select a voice")

            _ = self.combobox.currentIndexChanged.connect(
                self._on_current_index_changed
            )

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Voice"))
        layout.addWidget(self.combobox)
        self.setLayout(layout)

    def _on_current_index_changed(self, idx: int):
        data: str = self.combobox.itemData(idx)
        settings.setValue("voice", data)
        speech_synthesizer.properties.set_property(
            PropertyId.SpeechServiceConnection_SynthVoice, data
        )
