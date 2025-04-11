import threading
import queue
import numpy as np
import time
import soundfile as sf
import os
import sounddevice as sd
from melo.api import TTS


class MelottsTTSManager:
    def __init__(self, sample_rate=24000):
        self.tts = TTS(language='EN_V2', device="cpu")
        self.sample_rate = sample_rate
        self.speaker_ids = self.tts.hps.data.spk2id
        self.audio_queue = queue.Queue()
        self.generator_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.player_thread = threading.Thread(target=self._play_audio, daemon=True)
        self.generator_thread.start()
        self.player_thread.start() 
        

    def add_text(self, text, emotion=None):
        self.audio_queue.put((text, emotion))

            

    def _process_queue(self):
        while True:
            text, emotion = self.audio_queue.get()
            if not text:
                continue

            # File output path
            timestamp = int(time.time() * 1000)
            filename = f"output.wav"

            # Generate audio file
            print(f"[Generator] Generating audio for: {text}")
            filepath = self.tts.tts_to_file(text, self.speaker_ids['EN-US'], filename, speed=1.0)
            print(filename)
            data, sr = sf.read(filename, dtype='float32')
            # sd.play(data, samplerate=sr)
            # sd.wait()

            # Put filepath in queue for playback
            self.audio_queue.task_done()
            self.audio_queue.put(filepath)

    def _play_audio(self):
        while True:
            item = self.audio_queue.get()
            if isinstance(item, str) and os.path.exists(item):
                print(f"[Player] Playing audio: {item}")
                data, sr = sf.read(item, dtype='float32')
                sd.play(data, samplerate=sr)
                sd.wait()
                os.remove(item)  # Clean up
                self.audio_queue.task_done()


""" if __name__ == "__main__":
    melotts=MelottsTTSManager()
    melotts.add_text(" this is a test. hi I am Jarvis ")
    melotts._process_queue() """
   