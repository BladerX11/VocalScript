import os

from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
from azure.cognitiveservices.speech.audio import AudioOutputConfig

speech_config = SpeechConfig(
    subscription=os.environ.get("SPEECH_KEY"), endpoint=os.environ.get("ENDPOINT")
)
speech_config.speech_synthesis_voice_name = "en-US-AlloyTurboMultilingualNeural"
audio_config = AudioOutputConfig(filename="output.wav")
speech_synthesizer = SpeechSynthesizer(
    speech_config=speech_config, audio_config=audio_config
)
