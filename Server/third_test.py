import pyttsx3

#pyttsx3.speak("I will speak this text. Did you hear that?")
from  VoiceInterface import AudioToText
import logging
import webbrowser
import requests
import threading
import subprocess
from multiprocessing import Pipe


 # Keywords and corresponding routes
keywords_routes = {
    "help": "http://127.0.0.1:8080/hai-interface/help",
    "altitude": "http://127.0.0.1:8080/hai-interface/change-altitude",
    "height": "http://127.0.0.1:8080/hai-interface/change-altitude",
    "destination": "http://127.0.0.1:8080/hai-interface/change-destination",
    "emergency": "http://127.0.0.1:8080/hai-interface/change-destination"
     # add more keywords and routes 
}  

#engine_lock = threading.Lock()

def main(event):
    while True:
        def recording_started():
            #speak("Hello")
            print("Speak now...")
            # mark the event as  set
            event.set()
            # Send to Flask server
            requests.post('http://127.0.0.1:8080/ws', json={'type': "activate_assistant"})
            

        def recording_finished():
            print("Speech end detected... transcribing...")
            # mark the event as not set
            event.clear()
            # Send to Flask server
            requests.post('http://127.0.0.1:8080/ws', json={'type': "deactivate_assistant"}) 

        
        def speak(txt):
            #with engine_lock:
                engine = pyttsx3.init()
                engine.say(txt)
                engine.runAndWait()
                engine.stop()
                print('Engine stopped')

        # WebSocket server address
        WS_SERVER_ADDRESS = "ws://127.0.0.1:8080"

        # Open subroutes based on detected keywords
        def perform_action(user_text):
            user_text=user_text.lower()

            # Send audio input(user text) to Flask server
            #subprocess.run(["python", "/Users/sanyadoda/ONR-HAI/Server/server.py", user_text])
            requests.post('http://127.0.0.1:8080/ws', json={'type': "user_text", 'text': user_text})

            print("Looking")
            for keyword, route in keywords_routes.items():
                if keyword in user_text:
                    # Assistant's response
                    speak("Opening " + keyword)
                    # Open the route in the default browser
                    webbrowser.open(route)
                    break  # Exit loop after finding the first matching keyword
                else:
                    print("Sorry, didn't find" + user_text)
            


        with AudioToText(spinner=False, model="small.en", language="en", wake_words="jarvis", on_wakeword_detected=recording_started, on_recording_stop=recording_finished
        , wake_word_timeout=7.0 ) as recorder:
            print('Say "Jarvis" then speak.')
            #print(recorder.text())
            user_text=recorder.text().strip()
            print(user_text)
            user_audio=dict(text=user_text)
            requests.post('http://127.0.0.1:8080/ws', data=user_audio)
            
            print("Done. Now we should exit. Bye!")

        #speak(user_text)
        if(len(user_text)!= 0):
            perform_action(user_text)
        
 

if __name__ == '__main__':
    main(event)
 