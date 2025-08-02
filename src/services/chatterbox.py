import io
import logging
import re
from pathlib import Path
from typing import Callable, override

import soundfile
import torch
from chatterbox.tts import ChatterboxTTS
from torch import Tensor

from exceptions import ServiceCreationException, SynthesisException
from services.clone_service import CloneService
from services.tts_service import Services, Setting

_logger = logging.getLogger(__name__)


class Chatterbox(CloneService[Tensor]):
    """
    Chatterbox TTS service.
    """

    def __init__(self, voice: str, sample_voice: str):
        """Initialises the Chatterbox TTS service with a voice and a sample voice file.

        Args:
            voice (str): The voice to be used for synthesis.
            sample_voice (str): The path to the sample voice file used for cloning.

        Raises:
            ServiceCreationException: If there is an error during service creation.
        """
        super().__init__(sample_voice)

        try:
            self._chatterbox: ChatterboxTTS = ChatterboxTTS.from_pretrained("cpu")
        except Exception as e:
            _logger.error("Creating chatterbox service failed", exc_info=True)
            raise ServiceCreationException("Check log") from e

        self.voice = voice

    @classmethod
    @override
    def type(cls):
        return Services.CHATTERBOX

    @classmethod
    @override
    def setting_fields(cls) -> list[Setting]:
        return []

    @classmethod
    @override
    def _default_voice(cls) -> str:
        return "default"

    @property
    @override
    def voice(self) -> str:
        return self._voice

    @voice.setter
    @override
    def voice(self, voice: str):
        self._voice: str = voice

    @property
    @override
    def voices(self) -> list[tuple[str, str]]:
        return [(self._default_voice().capitalize(), self._default_voice())]

    def _create_audio(self, text: str, function: Callable[[str], Tensor]):
        sentences = re.split(r"(?<=[.?!])\s+", text.strip())
        chunks: list[Tensor] = []
        current = ""

        try:
            for sent in sentences:
                if current and len(current) + 1 + len(sent) > 300:
                    chunks.append(function(current))
                    current = sent
                    continue

                current = sent if not current else f"{current} {sent}"

            if current:
                chunks.append(function(current))
        except Exception as e:
            _logger.error("Synthesis failed", exc_info=True)
            raise SynthesisException("Check log") from e

        return torch.cat(chunks)

    @override
    def _synthesise_text_implementation(self, text: str):
        return self._create_audio(
            text,
            lambda current: ChatterboxTTS.from_pretrained("cpu")
            .generate(current)
            .squeeze(0),
        )

    @override
    def _save_implementation(self, file: Path, data: Tensor):
        soundfile.write(file, data, self._chatterbox.sr)

    @override
    def _get_wav_bytes(self, data: Tensor):
        buffer = io.BytesIO()
        soundfile.write(buffer, data, self._chatterbox.sr, format="wav")
        return buffer.getvalue()

    @override
    def _has_information(self):
        return True

    @override
    def _synthesise_clone_implementation(self, text: str):
        if not self.sample_voice.is_file():
            msg = "Sample voice path does not exist or point to a file"
            _logger.error("Synthesis failed. %s", msg)
            raise SynthesisException(msg)

        return self._create_audio(
            text,
            lambda chunk: self._chatterbox.generate(
                chunk, audio_prompt_path=self._sample_voice
            ).squeeze(0),
        )
