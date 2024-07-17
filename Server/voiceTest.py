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

global Jarvis


# Engine initialization 
engine = pyttsx3.init()
voices = engine.getProperty('voices')
#currentVoice = engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 170)


#Jarvis


# Flag to indicate if speech should be interrupted
interrupt_speech = False



def speak(text):
   global interrupt_speech
   print("Radio speaking")
   if engine.isBusy():
       #requests.post("http://127.0.0.1:8080/state", json={"event": "stop_engine", "action": "set"}) #clearing takeoff event
       #print('sent request to clear stop_engine')
       #logging.info('stop_engine set request sent')
       """   else:
       requests.post("http://127.0.0.1:8080/state", json={"event": "stop_engine", "action": "clear"}) #clearing takeoff event
       print('sent request to clear stop_engine') """
   with speech_lock:  # lock to ensure only one thread speaks at a time
        """      if engine._inLoop:
            engine.endLoop() #end loop if running
        # engine.say(text)
        # engine.runAndWait()   
        engine.startLoop(False)
        engine.say(text)
        engine.iterate() # Wait until speech is complete  """
        for word in text.split():
            if interrupt_speech:
                break
            engine.say(word)
            engine.runAndWait()
        interrupt_speech = False



def jarvis_speak(text):
   print("Jarvis speaking")
   jarvis_engine = pyttsx3.init()
   jarvis_voices = jarvis_engine.getProperty('voices')
   print(jarvis_voices)
   jarvis_engine.setProperty('voice', jarvis_voices[1].id)
   jarvis_engine.setProperty('rate', 170)

   #if jarvis_engine.isBusy():
       #requests.post("http://127.0.0.1:8080/state", json={"event": "stop_engine", "action": "set"}) #clearing takeoff event
       #print('sent request to clear stop_engine')
       #logging.info('stop_engine set request sent')
   """   else:
       requests.post("http://127.0.0.1:8080/state", json={"event": "stop_engine", "action": "clear"}) #clearing takeoff event
       print('sent request to clear stop_engine') """
       
   with speech_lock:  # lock to ensure only one thread speaks at a time
        if jarvis_engine._inLoop:
            jarvis_engine.endLoop() #end loop if running

        jarvis_engine.startLoop(False)
        jarvis_engine.say(text)
        jarvis_engine.iterate() # Wait until speech is complete 
        
def stop_engine():
   engine.stop()
   print("stopping engine")
   requests.post("http://127.0.0.1:8080/state", json={"event": "stop_engine", "action": "clear"}) #clearing takeoff event
   print('sent request to clear stop_engine')
   logging.info('stop_engine clear request sent')
    

async def delayForResponse(t):
    await asyncio.sleep(t)
    print('waiting for response')
    



if __name__ == "__main__":
   #main(inflight_event,status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event)
   speak('Control:Set the Callsign to N A S X G S and Radio channel to COMM 1 for transmitting updates')
   time.sleep(7)
   jarvis_speak("Hello, I am Jarvis how may I assist you?")
   time.sleep(5)