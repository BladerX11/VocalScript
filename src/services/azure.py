import logging
import re
from pathlib import Path
from typing import Callable, override

from azure.cognitiveservices.speech import (
    CancellationReason,
    PropertyId,
    SpeechConfig,
    SpeechSynthesisEventArgs,
    SpeechSynthesizer,
    SynthesisVoicesResult,
    VoiceInfo,
)
from azure.cognitiveservices.speech.diagnostics.logging import EventLogger
from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from exceptions import MissingInformationError
from services.tts_service import Services, TtsService

_logger = logging.getLogger(__name__)


class Azure(TtsService[SpeechSynthesisEventArgs]):
    def __init__(self, subscription: str, endpoint: str, voice: str):
        speech_config = SpeechConfig(subscription=subscription, endpoint=endpoint)
        speech_config.speech_synthesis_voice_name = voice
        self.speech_synthesizer: SpeechSynthesizer = SpeechSynthesizer(
            speech_config=speech_config, audio_config=None
        )
        self.output: QAudioOutput = QAudioOutput()
        self.player: QMediaPlayer = QMediaPlayer()
        self.player.setAudioOutput(self.output)
        self.buffer: QBuffer

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
    @override
    def _save_implementation(cls, file: Path, data: SpeechSynthesisEventArgs):
        _logger.info("Saving file. File: %s", file.name)
        with file.open("xb") as f:
            _ = f.write(data.result.audio_data)

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

    def _check_information(self):
        properties = self.speech_synthesizer.properties
        if not (
            properties.get_property(PropertyId.SpeechServiceConnection_Key).strip()
            and properties.get_property(
                PropertyId.SpeechServiceConnection_Endpoint
            ).strip()
        ):
            _logger.error("Service information is missing.")
            raise MissingInformationError

    def _format_voices(self, voices: list[VoiceInfo]):
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
        self._check_information()

        try:
            voices: list[tuple[str, str]] = []
            voices_result = self.speech_synthesizer.get_voices_async().get()

            if isinstance(voices_result, SynthesisVoicesResult):
                voices = self._format_voices(voices_result.voices)

            _logger.info("%d voices retrieved.", len(voices))
            return voices
        except RuntimeError as e:
            _logger.error("Failed to get voices. Check logs", exc_info=e)
            raise e

    def _clear_callbacks(self):
        self.speech_synthesizer.synthesis_started.disconnect_all()
        self.speech_synthesizer.synthesis_completed.disconnect_all()
        self.speech_synthesizer.synthesis_canceled.disconnect_all()

    def _create_synthesis_started(self, show_status: Callable[[str], None]):
        def synthesis_started(_: SpeechSynthesisEventArgs):
            show_status("Synthesising.")

        return synthesis_started

    def _create_file(self, show_status: Callable[[str], None]):
        def synthesis_completed(event: SpeechSynthesisEventArgs):
            show_status("Saving.")
            show_status(self.save_audio(event))
            self._clear_callbacks()

        return synthesis_completed

    def _create_play(self, show_status: Callable[[str], None]):
        def synthesis_completed(event: SpeechSynthesisEventArgs):
            _logger.info("Playing audio")
            self.buffer = QBuffer()
            self.buffer.setData(event.result.audio_data)

            if not self.buffer.open(QIODevice.OpenModeFlag.ReadOnly):
                _logger.error("Opening data failed")
                show_status("Playing failed. Could not open data")

            self.player.setSourceDevice(self.buffer)

            self.player.play()
            self.buffer.close()
            self._clear_callbacks()

        return synthesis_completed

    def _create_synthesis_canceled(self, show_status: Callable[[str], None]):
        def synthesis_canceled(event: SpeechSynthesisEventArgs):
            cancellation_details = event.result.cancellation_details

            if cancellation_details.reason == CancellationReason.Error:
                _logger.error(
                    "Synthesis failed. Error details: %s",
                    cancellation_details.error_details,
                )
                msg = "Synthesis failed. Check log."
            else:
                _logger.info("Synthesis canceled")
                msg = "Synthesis canceled."

            show_status(msg)
            self._clear_callbacks()

        return synthesis_canceled

    def _create_file_callbacks(self, show_status: Callable[[str], None]):
        self.speech_synthesizer.synthesis_started.connect(
            self._create_synthesis_started(show_status)
        )
        self.speech_synthesizer.synthesis_completed.connect(
            self._create_file(show_status)
        )
        self.speech_synthesizer.synthesis_canceled.connect(
            self._create_synthesis_canceled(show_status)
        )

    def _create_play_callbacks(self, show_status: Callable[[str], None]):
        self.speech_synthesizer.synthesis_started.connect(
            self._create_synthesis_started(show_status)
        )
        self.speech_synthesizer.synthesis_completed.connect(
            self._create_play(show_status)
        )
        self.speech_synthesizer.synthesis_canceled.connect(
            self._create_synthesis_canceled(show_status)
        )

    @override
    def save_text_to_file_async(self, text: str, show_status: Callable[[str], None]):
        _logger.info("Synthesising. Text: %s", text)
        self._check_information()
        self._create_file_callbacks(show_status)
        self.speech_synthesizer.speak_text_async(text)

    @override
    def save_ssml_to_file_async(self, ssml: str, show_status: Callable[[str], None]):
        _logger.info("Synthesising. SSML: %s", ssml)
        self._check_information()
        self._create_file_callbacks(show_status)
        self.speech_synthesizer.speak_ssml_async(ssml)

    @override
    def play_text_async(self, text: str, show_status: Callable[[str], None]):
        _logger.info("Synthesising. Text: %s", text)
        self._check_information()
        self._create_play_callbacks(show_status)
        self.speech_synthesizer.speak_text_async(text)

    @override
    def play_ssml_async(self, ssml: str, show_status: Callable[[str], None]):
        _logger.info("Synthesising. SSML: %s", ssml)
        self._check_information()
        self._create_play_callbacks(show_status)
        self.speech_synthesizer.speak_ssml_async(ssml)
