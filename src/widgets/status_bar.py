from azure.cognitiveservices.speech import SpeechSynthesisEventArgs
from azure.cognitiveservices.speech.speech import CancellationReason
from PySide6.QtWidgets import QStatusBar

from azure_service import speech_synthesizer


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        speech_synthesizer.synthesis_started.connect(
            lambda _: self.showMessage("Synthesising")
        )
        speech_synthesizer.synthesis_completed.connect(
            lambda _: self.showMessage("Synthesis complete")
        )
        speech_synthesizer.synthesis_canceled.connect(self.synthesis_canceled)

    def synthesis_canceled(self, event: SpeechSynthesisEventArgs):
        cancellation_details = event.result.cancellation_details

        if cancellation_details.reason == CancellationReason.Error:
            msg = f"Error: {cancellation_details.error_details}"
        else:
            msg = "Canceled"

        self.showMessage(msg)
