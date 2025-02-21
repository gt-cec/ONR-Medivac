from yapper import Yapper, PiperSpeaker, PiperVoiceUS, DefaultEnhancer, Persona

speaker = PiperSpeaker(
    voice=PiperVoiceUS.KUSAL
)

# Initialize TTS
yapper = Yapper(speaker=speaker)

# Global flag for stopping speech
current_speech_task = None

def speak(text, speaker_name):
    """Generate and play speech"""
    global current_speech_task
    yapper.yap(text, plain=True)