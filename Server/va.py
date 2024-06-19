import pyttsx3
import logging
from  VoiceInterface import AudioToText
import time
import webbrowser
import requests
import asyncio
import websockets
import socketIO_client
#from socketIO_client import SocketIO
from flask_socketio import SocketIO, emit


""" 
# Initialize the TTS engine
engine = pyttsx3.init()

# Set Engine Parameters:
voices = engine.getProperty('voices') #getting details of current voice
engine.setProperty('rate', 175)
engine.setProperty('pitch', 1.5)
engine.setProperty('voice', voices[7].id)   #changing index to change voice 

# Keywords and corresponding routes
keywords_routes = {
    "help": "/hai-interface/help",
    "altitude": "/hai-interface/altitude",
    "height": "/hai-interface/altitude",
    "destination": "/hai-interface/change-destination",
    "emergency": "/hai-interface/change-destination"
     # add more keywords and routes 
}

# WebSocket server address
WS_SERVER_ADDRESS = "ws://127.0.0.1:8080"

# Variable to track assistant activation
assistant_active = False;

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

async def connect_to_server():
   async with websockets.connect(WS_SERVER_ADDRESS) as websocket:
    #async with SocketIO(WS_SERVER_ADDRESS) as sio:
        global assistant_active
        print('Connected to server!')
        while True:
            # Capture audio input
            user_text = capture_audio()
            # If wake word detected and assistant is not active, activate it
            if user_text and not assistant_active:
                assistant_active = True
                await websocket.send("activate_assistant")
                #await sio.emit("activate_assistant")
            # Send user text if assistant is active
            elif assistant_active:
                await websocket.send(user_text)
                #await sio.emit(user_text)
            # If no wake word and assistant is active, deactivate it
            elif assistant_active:
                assistant_active = False
                await websocket.send("deactivate_assistant")
                #await sio.emit("deactivate_assistant") 



# Open subroutes based on detected keywords
def perform_action(user_text):
    for keyword, route in keywords_routes.items():
        if keyword in user_text:
            speak("You need help with " + keyword + "?")
            response = input("Yes or No: ")
            if response.lower() == "yes":
                speak("Opening " + keyword)
                   # Open the route in the default browser
                    webbrowser.open(route)
                    break  # Exit loop after finding the first matching keyword
           return True
             
                
            

# Capture audio input and send it to the server
def capture_audio():
    def jarvis_detected():
        print("Wakeup word 'Jarvis' detected.")
        speak("Hello")
        send_message("active")
        return True
        engine.say("Hello")
        engine.runAndWait()
        global assistant_active
        assistant_active = True
        # Send to Flask server
        #requests.post('http://127.0.0.1:8080/ws', json={'type': "activate_assistant"})

    def jarvis_timeout():
        print("No speech detected.. deactivating.")
        global assistant_active
        assistant_active = False
         # Send to Flask server
        #requests.post('http://127.0.0.1:8080/ws', json={'type': "deactivate_assistant"})
        

    recorder = AudioToText(spinner=False, level=logging.DEBUG, model="small.en", language="en", wake_words="jarvis", wake_word_timeout=7 on_wakeword_detected=jarvis_detected, on_wakeword_timeout=jarvis_timeout)
    print('Say "Jarvis" then speak.')
    user_text = recorder.text().strip()
    if (user_text):
        # Send audio input(user text) to Flask server
        #requests.post('http://127.0.0.1:8080/ws', json={'type': "user_text", 'text': user_text})
        print(user_text)
        perform_action(user_text)
        return user_text
    
    return "ok"

    

# Function to run the voice assistant
def voice_assistant():
    while True:
        # Capture audio input and send it to the server
        capture_audio()

# Entry point for running the voice assistant
if __name__ == '__main__':
    #asyncio.run(voi())
    voice_assistant() 
"""



# Define Jarvis wake word and keywords
WAKE_WORD = "Jarvis"
KEYWORDS = ["play music", "open weather", "show news"]

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to speak text
def speak(text):
   engine.say(text)
   engine.runAndWait()


# Keywords and corresponding routes
keywords_routes = {
    "help": "/hai-interface/help",
    "altitude": "/hai-interface/altitude",
    "height": "/hai-interface/altitude",
    "destination": "/hai-interface/change-destination",
    "emergency": "/hai-interface/change-destination"
     # add more keywords and routes 
}


# Open subroutes based on detected keywords
def perform_action(user_text):
    for keyword, route in keywords_routes.items():
        if keyword in user_text:
            speak("You need help with " + keyword + "?")
            # response = input("Yes or No: ")
            # if response.lower() == "yes":
            speak("Opening " + keyword)
            # Open the route in the default browser
            webbrowser.open(route)
            break  # Exit loop after finding the first matching keyword
    return True

# Function to send message to server
def send_message(message):
   # Replace with your server URL and message format
   #requests.post("http://your-server.com/message", data={"message": message})
   print('sent')

def listen_for_audio():
   # Create RealTimeSTT instance with desired language and wait time
   stt = AudioToText(spinner=False, model="small.en", wake_words="jarvis", language="en", wake_word_timeout=7, on_wakeword_detected=handle_wake_word, on_wakeword_timeout=handle_timeout)
   print("Listening...")
   user_text = stt.text().strip()
   return user_text

""" def handle_audio(audio):
   text = ""
   for chunk in audio:
       user_text = recorder.text().strip()
   return user_text.lower() """

def handle_wake_word():
    print('Heard Jarvis')
    speak("Activated")
    send_message("active")


def handle_timeout():
    print('No audio detected')
    speak("Inactive")
    send_message("inactive")
    #time.sleep(1)

def handle_keywords(text):
   for keyword in KEYWORDS:
       if keyword in text:
           speak("You need help with " + keyword + "?")
           response = input("Yes or No: ")
           if response.lower() == "yes":
               # Replace with your keyword URLs
               if keyword == "play music":
                   url = "http://your-music-service.com"
               elif keyword == "open weather":
                   url = "http://your-weather-website.com"
               elif keyword == "show news":
                   url = "http://your-news-website.com"
               speak("Opening " + keyword)
               # Open URL in web browser (assuming OS library is available)
               # import webbrowser
               # webbrowser.open(url)
           return True
   return False

def main():
    while True:
        text = listen_for_audio()
        #text = handle_audio(audio)
        if text:
            print(text)
            if perform_action(text):
                break
            else:
                speak("Inactive")
                send_message("inactive")
                break
       

if __name__ == "__main__":
   main()