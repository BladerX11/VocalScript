from datetime import datetime
import logging
from time import sleep

from azure.cognitiveservices.speech import (
    AudioDataStream,
    CancellationReason,
    SpeechConfig,
    SpeechSynthesisEventArgs,
    SpeechSynthesizer,
)
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from azure.cognitiveservices.speech.diagnostics.logging import EventLogger

from settings import settings
from utils import get_folder

speech_config = SpeechConfig(
    subscription=str(settings.value("key", " ")),
    endpoint=str(settings.value("endpoint", " ")),
)
speech_config.speech_synthesis_voice_name = str(
    settings.value("voice_name", "en-US-AlloyTurboMultilingualNeural")
)
speech_synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=None)
logger = logging.getLogger(__name__)


def log(msg: str):
    if "INFO" in msg:
        logger.info(msg)
    elif "ERROR" in msg:
        logger.error(msg)


def synthesis_completed(event: SpeechSynthesisEventArgs):
    stream = AudioDataStream(event.result)
    folder = get_folder() / "saved"

    if not folder.exists():
        folder.mkdir()

    file = str(folder / (datetime.now().isoformat() + ".wav"))
    stream.save_to_wav_file(file)


def synthesis_canceled(event: SpeechSynthesisEventArgs):
    cancellation_details = event.result.cancellation_details
    if cancellation_details.reason == CancellationReason.Error:
        logger.error(cancellation_details.error_details)


EventLogger.set_callback(log)

speech_synthesizer.synthesis_completed.connect(
    lambda e: AudioDataStream(e.result).save_to_wav_file(
        str(get_folder() / "saved" / (datetime.now().isoformat() + ".wav"))
    )
)
speech_synthesizer.synthesis_canceled.connect(synthesis_canceled)
speech_synthesizer.synthesis_completed.connect(synthesis_completed)
