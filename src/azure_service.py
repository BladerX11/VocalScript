import os

import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("SPEECH_KEY"), endpoint=os.environ.get("ENDPOINT")
)
speech_config.speech_synthesis_voice_name = "en-US-AlloyTurboMultilingualNeural"
audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")
speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config, audio_config=audio_config
)
