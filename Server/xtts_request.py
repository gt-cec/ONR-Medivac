"""  tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 \
    --list_speaker_idx


-model_name tts_models/en/ljspeech/tacotron2-DCA --use_cuda True

https://mbarnig.github.io/TTS-Models-Comparison/ """

from TTS.api import TTS
import numpy as np
import os
import sounddevice as sd
import soundfile as sf

os.environ['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
#tts = TTS("tts_models/en/ek1/tacotron2").to("cpu")
#ts = TTS("tts_models/en/multi-dataset/tortoise-v2")
""" def sample_speakers(text):
    speakers = ['Claribel Dervla', 'Daisy Studious', 'Gracie Wise', 'Tammie Ema', 'Alison Dietlinde', 'Ana Florence', 'Annmarie Nele', 'Asya Anara', 'Brenda Stern', 'Gitta Nikolina', 'Henriette Usha', 'Sofia Hellen', 'Tammy Grit', 'Tanja Adelina', 'Vjollca Johnnie', 'Andrew Chipper', 'Badr Odhiambo', 'Dionisio Schuyler', 'Royston Min', 'Viktor Eka', 'Abrahan Mack', 'Adde Michal', 'Baldur Sanjin', 'Craig Gutsy', 'Damien Black', 'Gilberto Mathias', 'Ilkin Urbano', 'Kazuhiko Atallah', 'Ludvig Milivoj', 'Suad Qasim', 'Torcull Diarmuid', 'Viktor Menelaos', 'Zacharie Aimilios', 'Nova Hogarth', 'Maja Ruoho', 'Uta Obando', 'Lidiya Szekeres', 'Chandra MacFarland', 'Szofi Granger', 'Camilla Holmström', 'Lilya Stainthorpe', 'Zofija Kendrick', 'Narelle Moon', 'Barbora MacLean', 'Alexandra Hisakawa', 'Alma María', 'Rosemary Okafor', 'Ige Behringer', 'Filip Traverse', 'Damjan Chapman', 'Wulf Carlevaro', 'Aaron Dreschner', 'Kumar Dahl', 'Eugenio Mataracı', 'Ferran Simen', 'Xavier Hayasaka', 'Luis Moray', 'Marcos Rudaski']
    for speaker in speakers:
        print(f"{speaker}:") 
        print()"""
        
if __name__ == "__main__":
    """ speaker='Ana Florence'
    text = "This is text to speech model voice"
    tts.tts_to_file(text="Hello, my name is Manmay , how are you?",
                file_path="output.wav",
                voice_dir="path/to/tortoise/voices/dir/",
                speaker="lj",
                preset="ultra_fast")
    data, samplerate = sf.read(file_path="output.wav")  # Load audio file
    print('playing')
    sd.play(data,samplerate)

config = XttsConfig()
config.load_json("config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="model/", eval=True)
#model.cuda()

outputs = model.synthesize(
    "This is Stefon Alfaro, I really said this. The sky is blue. Computers are good. Test 1 2 3 4.",
    config,
    speaker_wav="StefonNewMicSample.wav",
    gpt_cond_len=3,
    language="en",
    speed=1.5
)

#print(outputs)

# Extract the audio waveform from the 'wav' key.
raw_audio = outputs['wav']
# Use a predefined or configured sample rate. You might need to adjust this value.
sample_rate = 24000  # This is a common sample rate for TTS models, but check your model's configuration.

# Define the path where you want to save the audio file.
output_path = 'output2.wav'

# Save the audio data to a WAV file.
sf.write(output_path, raw_audio, sample_rate)
 """


# Load a multi-speaker model (ensure low-latency model is selected)
tts = TTS("tts_models/en/vctk/SpeedSpeech")

# List available speakers
print("Available speakers:", tts.speakers)

# Generate speech with a male voice and emotion
audio_male = tts.tts("Hello, this is a male voice.", speaker="p237", emotion="happy")

# Generate speech with a female voice and emotion
audio_female = tts.tts("Hi there, this is a female voice.", speaker="p294", emotion="neutral")
