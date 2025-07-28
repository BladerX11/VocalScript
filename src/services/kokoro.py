import io
import logging
from pathlib import Path
from typing import override

import soundfile
import torch
from huggingface_hub import snapshot_download
from kokoro import KPipeline
from kokoro.pipeline import LANG_CODES
from torch import FloatTensor, Tensor

from exceptions import SynthesisException
from services.tts_service import Services, Setting, TtsService

_logger = logging.getLogger(__name__)


class Kokoro(TtsService[Tensor]):
    SAMPLE_RATE: int = 24000

    def __init__(self, voice: str):
        """Initialize the Kokoro TTS service.

        Args:
            voice (str): The voice to use for synthesis. Defaults to "af_heart".
        """
        super().__init__()
        self.voice = voice

    @classmethod
    @override
    def type(cls):
        return Services.KOKORO

    @classmethod
    @override
    def setting_fields(cls) -> list[Setting]:
        return []

    @classmethod
    @override
    def _default_voice(cls):
        return "af_heart"

    @property
    @override
    def voices(self):
        remote_voice_folder = "voices"
        voice_dir = (
            Path(
                snapshot_download(
                    "hexgrad/Kokoro-82M", allow_patterns=f"{remote_voice_folder}/*.pt"
                )
            )
            / remote_voice_folder
        )
        voices: list[tuple[str, str]] = []

        for voice in [file.stem for file in voice_dir.glob("*.pt")]:
            voice_parts = voice.split("_")
            name = voice_parts[1].capitalize()
            locale_key = voice_parts[0][0]
            locale = (
                LANG_CODES.get(locale_key) if locale_key in LANG_CODES else "unknown"
            )
            gender = "Male" if voice_parts[0][1] == "m" else "Female"
            voices.append((f"{name} ({locale}) ({gender})", voice))

        return voices

    @property
    @override
    def voice(self):
        return self._voice

    @voice.setter
    @override
    def voice(self, voice: str):
        self._voice: str = voice
        self.pipeline: KPipeline = KPipeline(self._voice[0])

    @override
    def _synthesise_text_implementation(self, text: str) -> Tensor:
        generator = self.pipeline(text, self.voice)
        chunks: list[Tensor] = []

        for _, _, audio in list(generator):
            if isinstance(audio, FloatTensor):
                chunks.append(audio)

        return torch.cat(chunks)

    @override
    def _save_implementation(self, file: Path, data: Tensor):
        soundfile.write(file, data, self.SAMPLE_RATE)

    @override
    def _get_wav_bytes(self, data: Tensor):
        buffer = io.BytesIO()
        soundfile.write(buffer, data, self.SAMPLE_RATE, format="wav")
        return buffer.getvalue()

    @override
    def _has_information(self):
        return True
