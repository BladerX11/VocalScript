import importlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Generic, TypeVar

from settings import settings
from utils import from_data_dir

_logger = logging.getLogger(__name__)
T = TypeVar("T")


class Services(Enum):
    AZURE = "azure"


class TtsService(Generic[T], ABC):
    _current_service: "TtsService[object] | None" = None

    @abstractmethod
    def __init__(self, *args: str):
        pass

    @classmethod
    def get_service(cls) -> "TtsService[object]":
        """Returns existing instance or creates one based on saved type from settings."""
        if cls._current_service is None:
            try:
                service = Services(settings.value("service"))
            except ValueError:
                _logger.error(
                    "Restoring service from settings failed. Defaulting to Azure."
                )
                service = Services.AZURE
            cls.switch(service)
            assert cls._current_service is not None, "Service should be initialized."

        return cls._current_service

    @classmethod
    def _get_service_class(cls, service: Services) -> type["TtsService[object]"]:
        if service == Services.AZURE:
            return getattr(importlib.import_module("services.azure"), "Azure")

    @classmethod
    def switch(cls, service: Services):
        """Switches to a new TtsService instance for the given type."""
        cls._current_service = cls._get_service_class(service)(
            settings.value("azure/key") or " ",
            settings.value("azure/endpoint") or " ",
            str(settings.value("azure/voice", "")),
        )

    @classmethod
    def get_setting_fields_for(cls, service: Services):
        """Return setting_fields for a given service type."""
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
        """Saves the audio to the file

        Args:
        file (Path): The file path where the audio will be saved.
        data (T): The audio data to be saved.

        Raises:
        FileExistsError: If there is a file where the save directory or file is.
        IsADirectoryError If there is a directory where the save file is.
        PermissionError: If the save directory or file cannot be created due to lack of permissions.
        OSError: If there is an error creating the save directory.
        """
        pass

    @classmethod
    def save_audio(cls, data: T) -> str:
        """Creates save directory and saves audio to a file, handling its errors.

        Args:
        data (T): The audio data to be saved.

        Returns:
        msg (str): A message indicating the result of the save operation.
        """
        save_dir = "saved"
        file = None
        try:
            folder = from_data_dir(save_dir)
            _logger.info("Creating save directory. Directory: %s", save_dir)
            folder.mkdir(exist_ok=True)
            file = folder / (datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3] + ".wav")
            cls._save_implementation(file, data)
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

        return msg

    @property
    @abstractmethod
    def voices(self) -> list[tuple[str, str]]:
        """Returns a list of available voices for the TTS service."""
        pass

    @property
    @abstractmethod
    def voice(self) -> str:
        """Returns the currently selected voice for the TTS service.

        Returns:
            MissingInformationError: If the service information is not set.
            RuntimeError: If error occurs while retrieving the voice.
        """
        pass

    @voice.setter
    @abstractmethod
    def voice(self, voice: str):
        """Sets the currently selected voice for the TTS service."""
        pass

    @abstractmethod
    def save_text_to_file_async(self, text: str, show_status: Callable[[str], None]):
        """Saves the text to a file asynchronously.

        Args:
            text (str): The text to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.

        Raises:
            MissingInformationError: If the service information is not set.
        """
        pass

    @abstractmethod
    def play_text_async(self, text: str, show_status: Callable[[str], None]):
        """Plays the text asynchronously.

        Args:
            text (str): The text to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.

        Raises:
            MissingInformationError: If the service information is not set.
        """
        pass
