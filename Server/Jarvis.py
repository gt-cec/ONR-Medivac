import subprocess

def speak(text, speaker):
    subprocess.call(["tts", "--text", '"' + text + '"', "--model_name", "tts_models/en/ljspeech/overflow", "--out_path", "./speech.wav"])
    subprocess.call(["afplay", "./speech.wav"])