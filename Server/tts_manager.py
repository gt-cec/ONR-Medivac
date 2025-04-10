import threading
import queue
import numpy as np
import sounddevice as sd
from TTS.api import TTS

class TTSManager:
    def __init__(self, tts_model_name):
        self.tts = TTS(tts_model_name, gpu=False)  # CPU only
        self.text_queue = queue.Queue()
        self.audio_chunks = {}
        self.lock = threading.Lock()
        self.next_index = 0
        self.next_to_play = 0
        self.playback_event = threading.Event()

        # Start background threads
        threading.Thread(target=self._generate_audio, daemon=True).start()
        threading.Thread(target=self._play_audio, daemon=True).start()

    def add_text(self, text, emotion=None):
        with self.lock:
            self.text_queue.put((self.next_index, text, emotion))
            self.next_index += 1

    def _generate_audio(self):
        while True:
            idx, text, emotion = self.text_queue.get()
            print(f"[TTS] Synthesizing #{idx} | Emotion: {emotion}")
            # Simulate emotion by adjusting pitch/speed
            if emotion == "panic":
                audio = self.tts.tts(
                    text, 
                    speaker_idx=0,  # Use female if available
                    speed=1.4,       # faster for urgency
                    pitch=1.4        # higher pitch for panic
                )
            else:
                audio = self.tts.tts(text, speaker_idx=0)

            audio = np.array(audio, dtype=np.float32)

            with self.lock:
                self.audio_chunks[idx] = audio
                self.playback_event.set()

    def _play_audio(self):
        while True:
            self.playback_event.wait()
            with self.lock:
                while self.next_to_play in self.audio_chunks:
                    audio = self.audio_chunks.pop(self.next_to_play)
                    print(f"[Playback] Playing #{self.next_to_play}")
                    self.next_to_play += 1
                    sd.play(audio, samplerate=22050)
                    sd.wait()

            if not any(k >= self.next_to_play for k in self.audio_chunks):
                self.playback_event.clear()
