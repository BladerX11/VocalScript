import importlib
import logging
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Generic, TypeVar

from playsound3 import AVAILABLE_BACKENDS, playsound

from exceptions import SynthesisException
from settings import settings
from utils import from_data_dir

_logger = logging.getLogger(__name__)
T = TypeVar("T")


class Services(Enum):
    AZURE = "azure"
    KOKORO = "kokoro"


class TtsService(Generic[T], ABC):
    _current_service: "TtsService[object] | None" = None
    DEFAULT_SERVICE: Services = Services.AZURE

    def __init__(self, *args: str):
        """Initialize the TTS service by setting up the media player and audio output."""

    @classmethod
    def _get_service_class(cls, service: Services) -> type["TtsService[object]"]:
        """Return the TtsService subclass for the given service type.

        Args:
            service (Services): The enum value representing the desired service.

        Returns:
            type[TtsService]: The TtsService subclass corresponding to the service.
        """
        match service:
            case Services.AZURE:
                return getattr(importlib.import_module("services.azure"), "Azure")
            case Services.KOKORO:
                return getattr(importlib.import_module("services.kokoro"), "Kokoro")

    @classmethod
    def switch(cls, service: Services):
        """Switches to a new TtsService instance for the given type."""
        match service:
            case Services.AZURE:
                cls._current_service = cls._get_service_class(service)(
                    settings.value("azure/key") or " ",
                    settings.value("azure/endpoint") or " ",
                    str(settings.value("azure/voice", "")),
                )
            case Services.KOKORO:
                cls._current_service = cls._get_service_class(service)(
                    settings.value("kokoro/voice")
                )

    @classmethod
    def get_service(cls) -> "TtsService[object]":
        """Returns existing instance or creates one based on saved type from settings."""
        if cls._current_service is None:
            try:
                service = Services(settings.value("service"))
            except ValueError:
                _logger.error(
                    f"Restoring service from settings failed. Defaulting to {cls.DEFAULT_SERVICE.name.capitalize()}."
                )
                service = TtsService.DEFAULT_SERVICE

            cls.switch(service)
            assert cls._current_service is not None, "Service should be initialized."

        return cls._current_service

    @classmethod
    def get_setting_fields_for(cls, service: Services):
        """Retrieve the list of configurable setting keys for a specific TTS service.

        Args:
            service (Services): The enum value representing the TTS service.

        Returns:
            list[str]: The list of setting field names required by the service.
        """
        return cls._get_service_class(service).setting_fields()

    @classmethod
    @abstractmethod
    def type(cls) -> Services:
        """Returns the type of the TTS service."""
        pass

    @classmethod
    @abstractmethod
    def setting_fields(cls) -> list[str]:
        """Returns the setting fields for the TTS service."""
        pass

    @classmethod
    @abstractmethod
    def _save_implementation(cls, file: Path, data: T):
        """Saves audio data to a file.

        Args:
            file (Path): The file path where the audio will be saved.
            data (T): The audio data to be saved.

        Raises:
            FileExistsError: If a file already exists at the target path.
            IsADirectoryError: If the target path is a directory.
            PermissionError: If lacking permissions to create or write the file.
            OSError: For other filesystem errors.
        """
        pass

    @property
    @abstractmethod
    def voices(self) -> list[tuple[str, str]]:
        """Returns a list of available voices for the TTS service and the string the service recognises it by. External data may need to be fetched."""
        pass

    @property
    @abstractmethod
    def voice(self) -> str:
        """Gets the currently selected voice for the TTS service.

        Returns:
            str: The short name of the currently selected voice.
        """
        pass

    @voice.setter
    @abstractmethod
    def voice(self, voice: str):
        """Sets the currently selected voice for the TTS service."""
        pass

    @abstractmethod
    def _synthesise_text_implementation(self, text: str) -> T:
        """Synthesises plain text to audio data.

        Args:
            text (str): The text to be converted to speech.

        Returns:
            T: The audio data resulting from synthesis.

        Raises:
            SynthesisException: If there is an error during synthesis.
        """
        pass

    @abstractmethod
    def _get_wav_bytes(self, data: T) -> bytes:
        """Convert synthesized audio data to WAV byte format for playback.

        Args:
            data (T): The raw audio data returned by the synthesis implementation.

        Returns:
            bytes: The synthesized audio encoded in WAV format.
        """
        pass

    @abstractmethod
    def _has_information(self) -> bool:
        """Checks if the service has the necessary information to function.

        Returns:
            bool: True if the service has the necessary information, False otherwise.
        """
        pass

    def _perform_synthesis(
        self,
        label: str,
        input_str: str,
        synth: Callable[[str], T],
        show_status: Callable[[str], None],
    ) -> T | None:
        """Perform synthesis of input, checking configuration and handling synthesis errors.

        Args:
            label (str): A label describing the input type (e.g., 'Text' or 'SSML').
            input_str (str): The string to synthesise.
            synth (Callable[[str], T]): The low-level synthesis function to call.
            show_status (Callable[[str], None]): Callback to report status messages.

        Returns:
            Optional[T]: The synthesized audio data, or None if synthesis failed or configuration is missing.
        """
        _logger.info("Synthesising. %s: %s", label, input_str)
        if not self._has_information():
            show_status("Service information required to generate audio.")
            return None
        show_status("Synthesising.")
        try:
            return synth(input_str)
        except SynthesisException as e:
            _logger.error("Synthesis failed: %s", str(e), exc_info=e)
            show_status(str(e))
            return None

    def _synth_and_save(
        self,
        label: str,
        input_str: str,
        synth: Callable[[str], T],
        show_status: Callable[[str], None],
    ):
        """Generic helper to synthesise input and save the result to a WAV file.

        Args:
            label (str): A label describing the input type (e.g., 'Text' or 'SSML').
            input_str (str): The string to synthesise.
            synth (Callable[[str], T]): The low-level synthesis function to call.
            show_status (Callable[[str], None]): Callback to report status messages.
        """
        data = self._perform_synthesis(label, input_str, synth, show_status)
        if data is None:
            return
        save_dir = "saved"
        file = None
        show_status("Saving.")

        try:
            folder = from_data_dir(save_dir)
            _logger.info("Creating save directory. Directory: %s", save_dir)
            folder.mkdir(exist_ok=True)
            file = folder / (datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3] + ".wav")
            self._save_implementation(file, data)
        except FileExistsError as e:
            _logger.error("Saving failed. Error: %s", e.strerror, exc_info=e)
            target = f"File {file.name}" if file else f"Folder {save_dir}"
            msg = (
                f"Saving failed. {target} already exists. Please move it and try again."
            )
        except IsADirectoryError as e:
            _logger.error("Saving failed. Error: %s", e.strerror, exc_info=e)
            msg = f"Saving failed. File {file} already exists. Please try again."
        except PermissionError as e:
            _logger.error("Saving failed. Error: %s", e.strerror, exc_info=e)
            target = f"File {file.name}" if file else f"Folder {save_dir}"
            msg = f"Saving failed. Insufficient permissions for {target}."
        except OSError as e:
            _logger.error("Saving failed. Error: %s", e.strerror, exc_info=e)
            msg = "Saving failed. Filesystem error."
        else:
            _logger.info("Saving completed")
            msg = "Saving completed."

        show_status(msg)

    def _synth_and_play(
        self,
        label: str,
        input_str: str,
        synth: Callable[[str], T],
        show_status: Callable[[str], None],
    ):
        """Generic helper to synthesise input and play the resulting audio.

        Args:
            label (str): A label describing the input type (e.g., 'Text' or 'SSML').
            input_str (str): The string to synthesise.
            synth (Callable[[str], T]): The low-level synthesis function to call.
            show_status (Callable[[str], None]): Callback to report status messages.
        """
        data = self._perform_synthesis(label, input_str, synth, show_status)
        if data is None:
            return
        _logger.info("Playing audio.")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            _ = tmp.write(self._get_wav_bytes(data))
            tmp.flush()
            tmp_path = Path(tmp.name)

        _ = playsound(
            tmp_path, True, "ffplay" if "ffplay" in AVAILABLE_BACKENDS else None
        )
        tmp_path.unlink()

    def save_text_to_file(self, text: str, show_status: Callable[[str], None]):
        """Saves the text to a file asynchronously.

        Args:
            text (str): The text to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.
        """
        self._synth_and_save(
            "Text", text, self._synthesise_text_implementation, show_status
        )

    def play_text(self, text: str, show_status: Callable[[str], None]):
        """Plays the text asynchronously.

        Args:
            text (str): The text to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.
        """
        self._synth_and_play(
            "Text", text, self._synthesise_text_implementation, show_status
        )
