import asyncio
import sounddevice as sd
import numpy as np
import websockets
import json
from TTS.api import TTS

# Initialize TTS
tts = TTS("tts_models/multilingual/multi-dataset/your_tts", progress_bar=False).to("cpu")

# Global flag for stopping speech
current_speech_task = None

async def generate_audio(text, speaker_name):
    """Generate and play speech"""
    global current_speech_task

    # speaker index for Jarvis and Radio (default)
    speaker_idx = tts.speakers[3] if speaker_name.lower() == "jarvis" else tts.speakers[0]

    print(f"Speaking: {text} (Speaker: {speaker_name} -> {speaker_idx})")
    audio_output = tts.tts(text, speaker=speaker_idx, language="en", speed=0.7)

    audio_data = np.array(audio_output, dtype=np.float32)
    
    sd.play(audio_data, samplerate=22050)  # Play speech at 22.05 kHz
    
    while sd.get_stream().active:
        await asyncio.sleep(0.1)  # Check every 100ms if interrupted

async def listen_for_text():
    """WebSocket Server to receive text from server.py"""
    global current_speech_task
    async with websockets.serve(handler, "localhost", 8080):
        await asyncio.Future()  # Keep server running

async def handler(websocket, path):
    """Handle incoming messages"""
    global current_speech_task
    async for message in websocket:
        data = json.loads(message)
        text = data.get("text")
        speaker_name = data.get("speaker", "default")

        # Stop current speech if ongoing
        if current_speech_task:
            current_speech_task.cancel()

        # Start new speech task
        current_speech_task = asyncio.create_task(generate_audio(text, speaker_name))

# Start WebSocket listener
asyncio.run(listen_for_text())
