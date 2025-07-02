from azure.cognitiveservices.speech import SpeechSynthesisEventArgs
from azure.cognitiveservices.speech.speech import CancellationReason
from PySide6.QtWidgets import QStatusBar

from azure_service import save_to_wav_file, speech_synthesizer


class StatusBar(QStatusBar):
    """Status bar that updates messages based events and results."""

    def __init__(self, parent=None):
        super().__init__(parent)

        speech_synthesizer.synthesis_started.connect(
            lambda _: self.showMessage("Synthesising.")
        )
        speech_synthesizer.synthesis_completed.connect(self._synthesis_completed)
        speech_synthesizer.synthesis_canceled.connect(self._synthesis_canceled)

    def _synthesis_completed(self, event: SpeechSynthesisEventArgs):
        """Handle synthesis completed event by saving audio and displaying status message.

        Args:
            event (SpeechSynthesisEventArgs): Event containing synthesis result.
        """
        self.showMessage("Saving.")
        self.showMessage(save_to_wav_file(event.result))

    def _synthesis_canceled(self, event: SpeechSynthesisEventArgs):
        """Handle synthesis canceled event by displaying an error or canceled message.

        Args:
            event (SpeechSynthesisEventArgs): Event containing cancellation details.
        """
        cancellation_details = event.result.cancellation_details

        if cancellation_details.reason == CancellationReason.Error:
            msg = "Synthesis failed. Check log."
        else:
            msg = "Synthesis canceled."

        self.showMessage(msg)
