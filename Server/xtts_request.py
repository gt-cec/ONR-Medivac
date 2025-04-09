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
tts = TTS("tts_models/en/multi-dataset/tortoise-v2")
""" def sample_speakers(text):
    speakers = ['Claribel Dervla', 'Daisy Studious', 'Gracie Wise', 'Tammie Ema', 'Alison Dietlinde', 'Ana Florence', 'Annmarie Nele', 'Asya Anara', 'Brenda Stern', 'Gitta Nikolina', 'Henriette Usha', 'Sofia Hellen', 'Tammy Grit', 'Tanja Adelina', 'Vjollca Johnnie', 'Andrew Chipper', 'Badr Odhiambo', 'Dionisio Schuyler', 'Royston Min', 'Viktor Eka', 'Abrahan Mack', 'Adde Michal', 'Baldur Sanjin', 'Craig Gutsy', 'Damien Black', 'Gilberto Mathias', 'Ilkin Urbano', 'Kazuhiko Atallah', 'Ludvig Milivoj', 'Suad Qasim', 'Torcull Diarmuid', 'Viktor Menelaos', 'Zacharie Aimilios', 'Nova Hogarth', 'Maja Ruoho', 'Uta Obando', 'Lidiya Szekeres', 'Chandra MacFarland', 'Szofi Granger', 'Camilla Holmström', 'Lilya Stainthorpe', 'Zofija Kendrick', 'Narelle Moon', 'Barbora MacLean', 'Alexandra Hisakawa', 'Alma María', 'Rosemary Okafor', 'Ige Behringer', 'Filip Traverse', 'Damjan Chapman', 'Wulf Carlevaro', 'Aaron Dreschner', 'Kumar Dahl', 'Eugenio Mataracı', 'Ferran Simen', 'Xavier Hayasaka', 'Luis Moray', 'Marcos Rudaski']
    for speaker in speakers:
        print(f"{speaker}:") 
        print() """

if __name__ == "__main__":
    speaker='Ana Florence'
    text = "This is text to speech model voice"
    tts.tts_to_file(text="Hello, my name is Manmay , how are you?",
                file_path="output.wav",
                voice_dir="path/to/tortoise/voices/dir/",
                speaker="lj",
                preset="ultra_fast")
    data, samplerate = sf.read(file_path="output.wav")  # Load audio file
    print('playing')
    sd.play(data,samplerate)
