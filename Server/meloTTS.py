
from melo.api import TTS
import nltk
import numpy as np
import sounddevice as sd



speed = 1.0

device = "cpu"

# English 
text = "Did you ever hear a folk tale about a giant turtle?"
model = TTS(language='EN_V2', device=device)
speaker_ids = model.hps.data.spk2id

# American accent
output_path = 'en-us.wav'

output_path=model.tts_to_file(text, speaker_ids['EN-US'], output_path, speed=speed)
#model.synthesizer.tts
audio = model.synthesize(text, speaker_idx=speaker_ids['EN-US'], speed=1.0)
audio = np.array(audio, dtype=np.float32)
sd.play(audio, samplerate=22050)
sd.wait()