import threading
import time
import pyttsx3
import requests
import logging
import asyncio


# Global events and locks
status_lock = threading.Lock()   
speech_lock = threading.Lock()
last_radio_update = 0
pressure_warning=0
engine_failure=0
empty_tank=0
PW=0
ET=0
EF=0
receive=0
transmit=0
study_stage=1

 # Engine initialization 
engine = pyttsx3.init()
voices = engine.getProperty('voices')
currentVoice = engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 170)


def speak(text):
   with speech_lock:  # lock to ensure only one thread speaks at a time
        if engine._inLoop:
            engine.endLoop() #end loop if running
        # engine.say(text)
        # engine.runAndWait()
            
        engine.startLoop(False)
        engine.say(text)
        engine.iterate() # Wait until speech is complete 

if __name__ == "__main__":
   #main(inflight_event,status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event)
   speak("Acknowledged")