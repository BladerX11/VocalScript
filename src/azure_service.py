import logging
from datetime import datetime

from azure.cognitiveservices.speech import (
    AudioDataStream,
    CancellationReason,
    SpeechConfig,
    SpeechSynthesisEventArgs,
    SpeechSynthesisResult,
    SpeechSynthesizer,
)
from azure.cognitiveservices.speech.diagnostics.logging import EventLogger

from settings import settings
from utils import from_executable

_logger = logging.getLogger(__name__)
_speech_config = SpeechConfig(
    subscription=str(settings.value("key", " ")),
    endpoint=str(settings.value("endpoint", " ")),
)
_speech_config.speech_synthesis_voice_name = str(
    settings.value("voice_name", "en-US-AlloyTurboMultilingualNeural")
)
speech_synthesizer = SpeechSynthesizer(speech_config=_speech_config, audio_config=None)


def _log(msg: str):
    if "INFO" in msg:
        _logger.info(msg)
    elif "ERROR" in msg:
        _logger.error(msg)


def _synthesis_canceled(event: SpeechSynthesisEventArgs):
    cancellation_details = event.result.cancellation_details
    if cancellation_details.reason == CancellationReason.Error:
        _logger.error(
            "Synthesis failed. Error details: %s", cancellation_details.error_details
        )
    else:
        _logger.info("Synthesis canceled")


EventLogger.set_callback(_log)
speech_synthesizer.synthesis_completed.connect(
    lambda _: _logger.info("Synthesis completed")
)
speech_synthesizer.synthesis_canceled.connect(_synthesis_canceled)


def speak_text_async(text: str):
    _logger.info("Synthesising. Text: %s", text)
    speech_synthesizer.speak_text_async(text)


def save_to_wav_file(
    result: SpeechSynthesisResult,
):
    stream = AudioDataStream(result)
    folder = from_executable("saved")
    file = folder / (datetime.now().isoformat() + ".wav")
    _logger.info("Saving. File name: %s", file.name)

    try:
        folder.mkdir(exist_ok=True)
        stream.save_to_wav_file(str(file))
    except FileExistsError as e:
        msg = f"Saving failed. File {folder.name} already exists. Please move it and try again."
        _logger.error("Saving failed.", exc_info=e)
    except Exception as e:
        msg = "Saving failed. Check log."
        _logger.error("Saving failed.", exc_info=e)
    else:
        msg = "Saving completed."
        _logger.info("Saving completed")

    return msg
