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
         engine.say(text)
         engine.runAndWait()
         """ engine.startLoop(False)
         engine.say(text)
         engine.iterate() # Wait until speech is complete
         engine.endLoop()# Stop the event loop
 """
      #   engine.say(text)
      #   engine.runAndWait()

# Function to mimic initial communication before takeoff
def pre_takeoff(takeoff_event):
   print('Received')
   print(takeoff_event.is_set())
   if(takeoff_event.is_set()):
      print('Speaking!')
      speak("Control Tower: Callsign NASXGS, radio COMM1 ")
   speak("Control Tower: Flight and weather conditions look good. Ready for takeoff.")
   speak('Set the Callsign NASXGS and Radio to COMM1')
   takeoff_event.clear()

# Function to simulate in-flight status checks
def inflight_status_check(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event):
   while not emergency_event.is_set():
       time.sleep(10)  # Regular interval for status checks
       with status_lock:  
           if not emergency_event.is_set():  # when no emergency 
               speak("Control Tower: Please report your flight status, patient status, and ETA.")
               if status_report_event.wait(30):  # Wait for user to report back
                   status_report_event.clear()
               else: 
                   speak("Control Tower: Awaiting your status report.")

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

def flyOldForth():
   with status_lock:  
      speak("Control Tower: Reroute to Old Forth Hospital")

   

# Function to handle emergencies- administering medication, empty fuel tank, engine failure
def emergency_guidance(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event):
   
   if((administer_event.is_set() or tank_event.is_set() or engine_event.is_set()) and (not emergency_event.is_set())):
      emergency_event.set() # setting emergency event when other emergency happens
   
   while not emergency_event.is_set():
      time.sleep(60)
      print("status", takeoff_event.is_set(), status_report_event.is_set() )
   if(administer_event.is_set()):
      administer(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event)
   if(tank_event.is_set()):
      continueEmory()
   if(engine_event.is_set()):
      flyOldForth()

# Function to respond to user's input
def user_input_activation(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event):
   time.sleep(35) 
   administer_event.set(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event)


def main(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event):
   # Start pre-takeoff communication
   pre_takeoff(takeoff_event)

   #running as thread at all times but engine speaks only when event set

   # Start threads for in-flight status checks and emergency guidance
   threading.Thread(target=inflight_status_check,args={status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event}, daemon=True).start()
   threading.Thread(target=emergency_guidance, args={status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event}, daemon=True).start()

   # user input- when transmit through radio
   #user_input_activation(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event)

# Global events and locks
""" status_report_event = threading.Event()  #to be set when user says or should assume?
administer_event = threading.Event()
response_event = threading.Event() #to be set when user responds with vitals"""
status_lock = threading.Lock()   


if __name__ == "__main__":
   main(status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event)