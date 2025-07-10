from abc import ABC, abstractmethod
from typing import Callable, TypeVar
from services.tts_service import TtsService

T = TypeVar("T")


class SsmlService(TtsService[T], ABC):
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
    def play_ssml_async(self, ssml: str, show_status: Callable[[str], None]):
        """Plays the SSML asynchronously.

        Args:
            ssml (str): The SSML to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.

        Raises:
            MissingInformationError: If the service information is not set.
        """
        pass
