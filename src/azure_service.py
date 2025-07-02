import logging
from datetime import datetime
import re

from azure.cognitiveservices.speech import (
    AudioDataStream,
    CancellationReason,
    PropertyId,
    SpeechConfig,
    SpeechSynthesisEventArgs,
    SpeechSynthesisResult,
    SpeechSynthesizer,
    SynthesisVoicesResult,
)
from azure.cognitiveservices.speech.diagnostics.logging import EventLogger

from exceptions import MissingInformationError
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
    """Log a message at the appropriate level based on its content.

    Args:
        msg (str): The message to log. If 'INFO' in msg, logs as info; if 'ERROR' in msg, logs as error.
    """
    if "INFO" in msg:
        _logger.info(msg)
    elif "ERROR" in msg:
        _logger.error(msg)


def _synthesis_canceled(event: SpeechSynthesisEventArgs):
    """Handle synthesis canceled events by logging based on cancellation reason.

    Args:
        event (SpeechSynthesisEventArgs): The event containing synthesis cancellation details.
    """
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


def _has_information():
    """Check if speech service key and endpoint information are set in the synthesizer properties.

    Returns:
        bool: True if both key and endpoint properties are non-empty strings.
    """
    properties = speech_synthesizer.properties
    return (
        properties.get_property(PropertyId.SpeechServiceConnection_Key).strip()
        and properties.get_property(PropertyId.SpeechServiceConnection_Endpoint).strip()
    )


def speak_text_async(text: str):
    """Asynchronously synthesize speech for the given text.

    Args:
        text (str): The text to synthesize.

    Raises:
        MissingInformationError: If service key or endpoint information is missing.
    """
    _logger.info("Synthesising. Text: %s", text)
    if _has_information():
        speech_synthesizer.speak_text_async(text)
    else:
        _logger.error("Service information is missing.")
        raise MissingInformationError


def save_to_wav_file(
    result: SpeechSynthesisResult,
):
    """Save a speech synthesis result to a WAV file in the data directory.

    Args:
        result (SpeechSynthesisResult): The speech synthesis result to save.

    Returns:
        str: A message indicating the outcome of the save operation.
    """
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
    except RuntimeError as e:
        _logger.error("Saving failed.", exc_info=e)
        msg = "Saving failed. Check log."
    else:
        _logger.info("Saving completed")
        msg = "Saving completed."

    return msg


def get_voices():
    """Retrieve available voices from the speech service.

    Returns:
        list[tuple[str, str]]: A list of tuples containing voice display names and their service names.

    Raises:
        MissingInformationError: If service key or endpoint information is missing.
        RuntimeError: If retrieving voices fails at runtime.
    """
    _logger.info("Getting voices")
    if _has_information():
        voices: list[tuple[str, str]] = []
        try:
            voices_result = speech_synthesizer.get_voices_async().get()

            if isinstance(voices_result, SynthesisVoicesResult):
                for voice in voices_result.voices:
                    name_split = voice.short_name.split("-")
                    voices.append(
                        (
                            f"{' '.join(re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z]+|[A-Z]+|[a-z]+', name_split[2]))} ({'-'.join(name_split[:2])}) ({voice.gender.name})",
                            voice.short_name,
                        )
                    )

            _logger.info("%d voices retrieved.", len(voices))
            return voices
        except RuntimeError as e:
            _logger.error("Failed to get voices.", exc_info=e)
            raise RuntimeError
    else:
        _logger.error("Service information is missing.")
        raise MissingInformationError
