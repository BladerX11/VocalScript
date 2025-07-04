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
        pass

    @property
    @abstractmethod
    def voice(self) -> str:
        pass

    @voice.setter
    @abstractmethod
    def voice(self, voice: str):
        pass

    @abstractmethod
    def save_to_file(self, text: str, show_status: Callable[[str], None]):
        pass
