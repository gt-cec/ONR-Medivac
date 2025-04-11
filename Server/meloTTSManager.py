import threading
import queue
import numpy as np
import sounddevice as sd
from melo.api import TTS


class MelottsTTSManager:
    def __init__(self, model_name="en_male", sample_rate=24000):
        self.tts = TTS(model_name)
        self.sample_rate = sample_rate
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
            filename = f"output_{timestamp}.wav"

            # Generate audio file
            print(f"[Generator] Generating audio for: {text}")
            filepath = self.tts.tts_to_file(text, filename)

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
