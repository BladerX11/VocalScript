import logging
import re
from pathlib import Path
from typing import override

from azure.cognitiveservices.speech import (
    CancellationReason,
    PropertyId,
    SpeechConfig,
    SpeechSynthesisCancellationDetails,
    SpeechSynthesisResult,
    SpeechSynthesizer,
    SynthesisVoicesResult,
    VoiceInfo,
)
from azure.cognitiveservices.speech.diagnostics.logging import EventLogger

from exceptions import ServiceCreationException, SynthesisException
from services.ssml_service import SsmlService
from services.tts_service import Services

_logger = logging.getLogger(__name__)


class Azure(SsmlService[SpeechSynthesisResult]):
    def __init__(self, subscription: str, endpoint: str, voice: str):
        """Initialize Azure TTS service.

        Args:
            subscription (str): Azure subscription key.
            endpoint (str): Azure service endpoint URL.
            voice (str): Default synthesis voice short name.
        """
        super().__init__()

        try:
            speech_config = SpeechConfig(subscription=subscription, endpoint=endpoint)
            speech_config.speech_synthesis_voice_name = voice
            self.speech_synthesizer: SpeechSynthesizer = SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )
        except Exception as e:
            _logger.error("Creating azure service failed", exc_info=True)
            raise ServiceCreationException("Check log") from e

        def _log(msg: str):
            if "INFO" in msg:
                _logger.info(msg)
            elif "ERROR" in msg:
                _logger.error(msg)

        EventLogger.set_callback(_log)

    @classmethod
    @override
    def type(cls):
        return Services.AZURE

    @classmethod
    @override
    def setting_fields(cls):
        return ["key", "endpoint"]

    @classmethod
    def _has_error(
        cls,
        details: SpeechSynthesisCancellationDetails | None,
    ):
        """Check synthesis cancellation details and raise exception on error or cancellation.

        Args:
            details (SpeechSynthesisCancellationDetails | None): The cancellation details from synthesis.

        Raises:
            SynthesisException: If synthesis failed or was canceled.
        """
        if details is None:
            return

        if details.reason == CancellationReason.Error:
            _logger.error("Synthesis failed. Error details: %s", details.error_details)
            msg = "Synthesis failed. Check log."
        else:
            _logger.info("Synthesis canceled")
            msg = "Synthesis canceled."

        raise SynthesisException(msg)

    @property
    def key(self) -> str:
        """Azure subscription key property getter."""
        return self.speech_synthesizer.properties.get_property(
            PropertyId.SpeechServiceConnection_Key
        )

    @key.setter
    def key(self, value: str):
        """Azure subscription key property setter."""
        self.speech_synthesizer.properties.set_property(
            PropertyId.SpeechServiceConnection_Key, value
        )

    @property
    def endpoint(self) -> str:
        """Azure endpoint property getter."""
        return self.speech_synthesizer.properties.get_property(
            PropertyId.SpeechServiceConnection_Endpoint
        )

    @endpoint.setter
    def endpoint(self, value: str):
        """Azure endpoint property setter."""
        self.speech_synthesizer.properties.set_property(
            PropertyId.SpeechServiceConnection_Endpoint, value
        )

    @property
    @override
    def voice(self):
        return self.speech_synthesizer.properties.get_property(
            PropertyId.SpeechServiceConnection_SynthVoice
        )

    @voice.setter
    @override
    def voice(self, voice: str):
        self.speech_synthesizer.properties.set_property(
            PropertyId.SpeechServiceConnection_SynthVoice, voice
        )

    def _format_voices(self, voices: list[VoiceInfo]):
        """Format a list of Azure VoiceInfo into display tuples.

        Args:
            voices (list[VoiceInfo]): The retrieved list of Azure VoiceInfo objects.

        Returns:
            list[tuple[str, str]]: List of tuples (formatted display name, voice short name).
        """
        formatted_voices: list[tuple[str, str]] = []
        for voice in voices:
            name_split = voice.short_name.split("-")
            formated_name = " ".join(
                re.findall(
                    r"[A-Z]+(?=[A-Z][a-z])|[A-Z][a-z]+|[A-Z]+|[a-z]+",
                    name_split[2],
                )
            )
            formatted_voices.append(
                (
                    f"{formated_name} ({voice.locale}) ({voice.gender.name})",
                    voice.short_name,
                )
            )
        return formatted_voices

    @property
    @override
    def voices(self):
        _logger.info("Getting voices")
        voices: list[tuple[str, str]] = []

        if self._has_information():
            voices_result = self.speech_synthesizer.get_voices_async().get()

            if isinstance(voices_result, SynthesisVoicesResult):
                voices = self._format_voices(voices_result.voices)

            _logger.info("%d voices retrieved", len(voices))
            return voices
        else:
            return voices

    @override
    def _synthesise_text_implementation(self, text: str):
        result = self.speech_synthesizer.speak_text(text)
        self._has_error(result.cancellation_details)
        return result

    @override
    def _save_implementation(self, file: Path, data: SpeechSynthesisResult):
        _logger.info("Saving file. File: %s", file.name)
        with file.open("xb") as f:
            _ = f.write(data.audio_data)

    @override
    def _get_wav_bytes(self, data: SpeechSynthesisResult):
        return data.audio_data

    @override
    def _has_information(self):
        properties = self.speech_synthesizer.properties

        if (
            properties.get_property(PropertyId.SpeechServiceConnection_Key).strip()
            and properties.get_property(
                PropertyId.SpeechServiceConnection_Endpoint
            ).strip()
        ):
            return True
        else:
            return False

    @override
    def _synthesise_ssml_implementation(self, ssml: str):
        result = self.speech_synthesizer.speak_ssml(ssml)
        self._has_error(result.cancellation_details)
        return result
