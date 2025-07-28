from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, TypeVar

from services.tts_service import TtsService

T = TypeVar("T")


class CloneService(TtsService[T], ABC):
    CLONE_VOICE: str = "clone"

    def __init__(self, sample_voice: str):
        """Initialises the CloneService with a voice and a sample voice file.

        Args:
            sample_voice (str): The path to the sample voice file used for cloning.

        Raises:
            ServiceCreationException: If there is an error during service creation.
        """
        super().__init__()
        self.sample_voice = Path(sample_voice)

    @classmethod
    def sample_voice_key(cls):
        """Returns the key for the sample voice setting used in cloning."""
        return f"{cls.type().value}/sample_voice"

    @property
    def sample_voice(self):
        """The path to the sample voice file used for cloning."""
        return self._sample_voice

    @sample_voice.setter
    def sample_voice(self, value: Path):
        self._sample_voice: Path = value

    @abstractmethod
    def _synthesise_clone_implementation(self, text: str) -> T:
        """Synthesises text to audio data using a sample voice.

        Returns:
            data: The audio data synthesised from the text using the sample voice.

        Raises:
            SynthesisException: If there is an error during synthesis.
        """
        pass

    def save_clone_to_file(self, text: str, show_status: Callable[[str], None]):
        """Saves the audio synthesised with the sample voice to a file.

        Args:
            text (str): The text to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.
        """
        self._synth_and_save(text, self._synthesise_clone_implementation, show_status)

    def play_clone(self, text: str, show_status: Callable[[str], None]):
        """Plays the audio synthesised with the sample voice.

        Args:
            text (str): The text to be converted to speech.
            show_status (Callable[[str], None]): A callback function to show status updates.
        """
        self._synth_and_play(text, self._synthesise_clone_implementation, show_status)
