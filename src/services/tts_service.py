from abc import ABC, abstractmethod
from enum import Enum
import importlib
import logging
from typing import Callable

from settings import settings

_logger = logging.getLogger(__name__)


class Services(Enum):
    AZURE = "azure"


class TtsService(ABC):
    _current_service: "TtsService | None" = None

    @abstractmethod
    def __init__(self, *args: str):
        pass

    @classmethod
    def get_service(cls) -> "TtsService":
        """Returns existing instance or creates one based on saved type from settings."""
        if cls._current_service is None:
            try:
                service = Services(settings.value("tts_service/type"))
            except ValueError:
                _logger.error(
                    "Restoring service from settings failed. Defaulting to Azure."
                )
                service = Services.AZURE
            cls.switch(service)
            assert cls._current_service is not None, "Service should be initialized."

        return cls._current_service

    @classmethod
    def _get_service_class(cls, service: Services) -> type["TtsService"]:
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
    def save_ssml_to_file_async(self, ssml: str, show_status: Callable[[str], None]):
        """Saves the SSML to a file asynchronously.

        Args:
            ssml (str): The SSML to be converted to speech.
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

    @abstractmethod
    def play_ssml_async(self, ssml: str, show_status: Callable[[str], None]):
        """Plays the SSML asynchronously.

        Args:
            ssml (str): The SSML to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.

        Raises:
            MissingInformationError: If the service information is not set.
        """
        pass
