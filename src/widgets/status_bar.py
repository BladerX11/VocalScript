from azure.cognitiveservices.speech import SpeechSynthesisEventArgs
from azure.cognitiveservices.speech.speech import CancellationReason
from PySide6.QtWidgets import QStatusBar

from azure_service import save_to_wav_file, speech_synthesizer


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        speech_synthesizer.synthesis_started.connect(
            lambda _: self.showMessage("Synthesising.")
        )
        speech_synthesizer.synthesis_completed.connect(self._synthesis_completed)
        speech_synthesizer.synthesis_canceled.connect(self._synthesis_canceled)

    def _synthesis_completed(self, event: SpeechSynthesisEventArgs):
        self.showMessage("Saving.")
        self.showMessage(save_to_wav_file(event.result))

    def _synthesis_canceled(self, event: SpeechSynthesisEventArgs):
        cancellation_details = event.result.cancellation_details

        if cancellation_details.reason == CancellationReason.Error:
            msg = "Synthesis failed. Check log."
        else:
            msg = "Synthesis canceled."

        self.showMessage(msg)
