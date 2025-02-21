# from yapper import Yapper, PiperSpeaker, PiperVoiceUS, DefaultEnhancer, Persona

# speaker = PiperSpeaker(
#     voice=PiperVoiceUS.KUSAL
# )

# # Initialize TTS
# yapper = Yapper(enhancer=DefaultEnhancer(Persona.JARVIS))

# # Global flag for stopping speech
# current_speech_task = None

# def speak(text, speaker_name):
#     """Generate and play speech"""
#     global current_speech_task
#     yapper.yap(text, plain=True)


import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

