import pyttsx3

#pyttsx3.speak("I will speak this text. Did you hear that?")
from  VoiceInterface import AudioToText
import logging


if __name__ == '__main__':
 while True:
    def recording_started():
        print("Speak now...")

    def recording_finished():
        print("Speech end detected... transcribing...")


    with AudioToText(spinner=False, model="small.en", language="en", wake_words="jarvis", on_wakeword_detected=recording_started, on_recording_stop=recording_finished
    , wake_word_timeout=7.0 ) as recorder:
        print('Say "Jarvis" then speak.')
        #print(recorder.text())
        user_text=recorder.text().strip()
        print(user_text)
        print("Done. Now we should exit. Bye!")

    engine = pyttsx3.init()
    engine.say("Hello!")
    assistant_response = 'I can hear you'
    txt='What can I help you with?'
    engine.say(assistant_response)
    #engine.say(user_text)
    engine.runAndWait()
    engine.stop()
    print('Engine stopped')