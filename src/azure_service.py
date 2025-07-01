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
from utils import from_data_dir

_logger = logging.getLogger(__name__)
_speech_config = SpeechConfig(
    subscription=settings.value("key") or " ",
    endpoint=settings.value("endpoint") or " ",
)
_speech_config.speech_synthesis_voice_name = str(settings.value("voice", ""))
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
    save_dir = "saved"

    try:
        folder = from_data_dir(save_dir)
        _logger.info("Creating save directory. Directory: %s", save_dir)
        folder.mkdir(exist_ok=True)
        file = folder / (datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3] + ".wav")
        _logger.info("Saving file. File: %s", file.name)
        stream.save_to_wav_file(str(file))
    except FileExistsError as e:
        _logger.error(
            "Creating save directory failed. Error: %s", e.strerror, exc_info=e
        )
        msg = f"Creating save directory failed. Folder {save_dir} already exists as a file. Please move it and try again."
    except PermissionError as e:
        _logger.error(
            "Creating save directory failed. Error: %s", e.strerror, exc_info=e
        )
        msg = "Creating save directory failed. Insufficient Permissions."
    except OSError as e:
        _logger.error(
            "Creating save directory failed. Error: %s", e.strerror, exc_info=e
        )
        msg = "Creating Save directory failed. Filesystem error."
    except Exception as e:
        _logger.error("Saving failed.", exc_info=e)
        msg = "Saving failed. Check log."
    else:
        _logger.info("Saving completed")
        msg = "Saving completed."

    return msg
