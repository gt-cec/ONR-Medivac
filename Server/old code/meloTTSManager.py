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

        self.text_queue = queue.Queue()
        self.audio_queue = queue.PriorityQueue()  # (order, filepath)

        self.counter = 0  # sequence counter
        self.lock = threading.Lock()

        """ self.generator_thread = threading.Thread(target=self._generate_audio_loop, daemon=True)
        self.player_thread = threading.Thread(target=self._play_audio_loop, daemon=True)

        self.generator_thread.start()
        self.player_thread.start() """

    def add_text(self, full_text):
        # First few words (prime)
        speed = 1.0
        chunks = self._split_text(full_text)
        for i, chunk in enumerate(chunks):
            with self.lock:
                order = self.counter
                self.counter += 1
            self.text_queue.put((order, chunk))
        
            timestamp = int(time.time() * 1000)
            filename = f"melotts_chunk_{timestamp}_{order}.wav"

            print(f"[Generator] ({order}) Generating: {full_text}")
            filepath = self.tts.tts_to_file(full_text, self.speaker_ids['EN-US'], filename, speed=speed)
            data, sr = sf.read(filename, dtype='float32')
            sd.play(data, samplerate=sr)
            sd.wait()
            os.remove(filepath)

    def _split_text(self, text, chunk_size=5):
        words = text.strip().split()
        return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    def _generate_audio_loop(self):
       

        while True:
            order, text = self.text_queue.get()
            if not text:
                continue

            timestamp = int(time.time() * 1000)
            filename = f"melotts_chunk_{timestamp}_{order}.wav"

            print(f"[Generator] ({order}) Generating: {text}")
            filepath = self.tts.tts_to_file(text, self.speaker_ids['EN-US'], filename, speed=1)
            data, sr = sf.read(filepath, dtype='float32')
            sd.play(data, samplerate=sr)
            sd.wait()
            os.remove(filepath)
            self.audio_queue.put((order, filepath))
            self.text_queue.task_done()

    def _play_audio_loop(self):
        next_to_play = 0
        buffer = {}

        while True:
            if not self.audio_queue.empty():
                order, filepath = self.audio_queue.get()
                buffer[order] = filepath
                self.audio_queue.task_done()

            if next_to_play in buffer:
                filepath = buffer.pop(next_to_play)
                print(f"[Player] Playing chunk {next_to_play}: {filepath}")
                data, sr = sf.read(filepath, dtype='float32')
                sd.play(data, samplerate=sr)
                sd.wait()
                os.remove(filepath)
                next_to_play += 1
            else:
                time.sleep(0.05)  # wait a bit before checking again