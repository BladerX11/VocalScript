from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QCompleter,
    QHBoxLayout,
    QLabel,
    QWidget,
)
from azure.cognitiveservices.speech import PropertyId

from azure_service import get_voices, speech_synthesizer
from exceptions import MissingInformationError
from settings import settings


class VoiceSelector(QWidget):
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
        _ = self.combobox.currentIndexChanged.disconnect(self._on_current_index_changed)
        self.combobox.clear()

        try:
            voices = get_voices()

            if len(voices) == 0:
                self.status.emit(
                    "No voices retrieved. Ensure service information is correct."
                )
                return

            for name, code in voices:
                self.combobox.addItem(name, code)

            if settings.contains("voice"):
                idx = self.combobox.findData(settings.value("voice"))
                self.combobox.setCurrentIndex(idx)

                if idx == -1:
                    self.status.emit("Saved voice is invalid.")
        except RuntimeError:
            self.status.emit("Loading voices failed. Check logs.")
        except MissingInformationError:
            self.status.emit("Service information required to get voices.")
        finally:
            _ = self.combobox.currentIndexChanged.connect(
                self._on_current_index_changed
            )

    @Slot(int)
    def _on_current_index_changed(self, idx: int):
        data: str = self.combobox.itemData(idx)
        settings.setValue("voice", data)
        speech_synthesizer.properties.set_property(
            PropertyId.SpeechServiceConnection_SynthVoice, data
        )
