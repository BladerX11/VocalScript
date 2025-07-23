from abc import ABC, abstractmethod
import logging
from typing import Callable, TypeVar
from services.tts_service import TtsService

T = TypeVar("T")

_logger = logging.getLogger(__name__)


class SsmlService(TtsService[T], ABC):
    @abstractmethod
    def _synthesise_ssml_implementation(self, ssml: str) -> T:
        """Synthesises SSML to audio data.

        Args:
            text (str): The SSML to be converted to speech.

        Returns:
            data: The audio data synthesised from the SSML.

        Raises:
            SynthesisException: If there is an error during synthesis.
        """
        pass

    def save_ssml_to_file(self, ssml: str, show_status: Callable[[str], None]):
        """Saves the SSML to a file.

        Args:
            ssml (str): The SSML to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.
        """
        self._synth_and_save(ssml, self._synthesise_ssml_implementation, show_status)

    def play_ssml(self, ssml: str, show_status: Callable[[str], None]):
        """Plays the SSML as audio.

        Args:
            ssml (str): The SSML to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.
        """
        self._synth_and_play(ssml, self._synthesise_ssml_implementation, show_status)
