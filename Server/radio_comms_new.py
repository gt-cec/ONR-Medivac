import threading
import time
import pyttsx3

# Engine initialization 
engine = pyttsx3.init()

speech_lock = threading.Lock()

def speak(text):
   with speech_lock:  # lock to ensure only one thread speaks at a time
       if engine._inLoop:
         engine.endLoop() #end loop is running
       else:
         engine.startLoop(False)
         engine.say(text)
         engine.iterate() # Wait until speech is complete
         engine.endLoop()# Stop the event loop

   

# Function to mimic initial communication before takeoff
def pre_takeoff(takeoff_event):
   print('event set receieved')
   speak("Control Tower: Callsign NASXGS, radio COMM1 ")
   time.sleep(2)  # Wait for 2 seconds
   speak("Control Tower: Flight and weather conditions look good. Ready for takeoff.")
   time.sleep(2)
   speak('Set the Callsign NASXGS and Radio to COMM1')
   time.sleep(2)
   takeoff_event.clear()


# Function to simulate in-flight status checks
def inflight_status_check(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event, radio_update_complete, inflight_event):
      while inflight_event.is_set() and not emergency_event.is_set():
         with status_lock:  
            current_time = time.time()
            if not emergency_event.is_set() and (current_time - last_radio_update >90):  # when no emergency and last radio update >90s ago (assuming 30s gap + 30s vitals + 30s gap)
               speak("Control Tower: Please report your flight status, patient status, and ETA.")
               if status_report_event.wait(45):  # Wait for user to report back  --> set with transmit button?
                  status_report_event.clear()
               last_radio_update = time.time()
               radio_update_complete.set()
         time.sleep(1)

# Function to provide medicine administeration guidance
def administer(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event):
   with status_lock:  
       speak("Control Tower: What are patient's current vitals?")
       if response_event.wait(30):  # Wait for user to respond --> transmit button radio
         response_event.clear()
       else:
         speak("Control Tower: Awaiting patient's current status.")
         
       speak("Control Tower: Follow these steps:")
       speak("1. Verify patient's identity and medication orders")
       speak("2. Prepare the medication and IV equipment")
       speak("3. Administer the dexamethasone via IV push")
       speak("4. Monitor patient's vital signs and response to the medication")
       speak("5. Inform the pilot to change the altitude to 1000 feet")

def continueEmory():
   with status_lock:  
      speak("Control Tower: Continue flying to Emory University Hospital")

def flyoldForth():
   with status_lock:  
      speak("Control Tower: Reroute to Southside Medical Center")


def main(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event, radio_update_complete, inflight_event):
   print('Radio Comms thread started')

   if(takeoff_event.is_set()):
      pre_takeoff(takeoff_event) # Start pre-takeoff communication
   
   if((administer_event.is_set() or tank_event.is_set() or engine_event.is_set()) and (not emergency_event.is_set())):
        emergency_event.set() # setting emergency event when other emergency happens
   
   # Start threads for in-flight status checks and emergency guidance-->running as thread at all times but engine speaks only when event set
   threading.Thread(target=inflight_status_check,args={status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event, radio_update_complete, inflight_event}, daemon=True).start()
   
   if administer_event.is_set():
        administer(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event)
   if tank_event.is_set():
        continueEmory()
   if engine_event.is_set() :
        flyoldForth()
   #radio comms already running as thread in server what if not run inflight and emergence guidance as thread?

# Global lock
status_lock = threading.Lock()   


if __name__ == "__main__":
   main(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event, radio_update_complete, inflight_event)
