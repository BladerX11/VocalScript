import logging
import os

from azure.cognitiveservices.speech import (
    CancellationReason,
    SpeechConfig,
    SpeechSynthesisEventArgs,
    SpeechSynthesizer,
)
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from azure.cognitiveservices.speech.diagnostics.logging import EventLogger

speech_config = SpeechConfig(
    subscription=os.environ.get("SPEECH_KEY"), endpoint=os.environ.get("ENDPOINT")
)
speech_config.speech_synthesis_voice_name = "en-US-AlloyTurboMultilingualNeural"
audio_config = AudioOutputConfig(filename="output.wav")
speech_synthesizer = SpeechSynthesizer(
    speech_config=speech_config, audio_config=audio_config
)
logger = logging.getLogger(__name__)


def log(msg: str):
    if "INFO" in msg:
        logger.info(msg)
    elif "ERROR" in msg:
        logger.error(msg)


def synthesis_canceled(event: SpeechSynthesisEventArgs):
    cancellation_details = event.result.cancellation_details
    if cancellation_details.reason == CancellationReason.Error:
        logger.error(cancellation_details.error_details)
    EventLogger.set_callback()


EventLogger.set_callback(log)

speech_synthesizer.synthesis_canceled.connect(synthesis_canceled)
