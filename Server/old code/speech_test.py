from tts_manager import TTSManager
import re
import time


tts_manager = TTSManager("tts_models/en/ljspeech/tacotron2-DDC")  

def handle_send_text(text):
    
    # Clean the text (remove non-alphanumeric characters except common punctuation)
    text = re.sub(r"[^a-zA-Z0-9.,'?! ]", "", text)
    
    # Add the clean text to the TTS manager
    tts_manager.add_text(text)
    tts_manager._generate_audio()



if __name__ == "__main__":
    time.sleep(10)
    handle_send_text("This is a test. I am trying to run this. why are you not running")
