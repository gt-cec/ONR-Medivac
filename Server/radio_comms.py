import threading
import time
import pyttsx3

# Engine initialization 
engine = pyttsx3.init()

speech_lock = threading.Lock()

def speak(text):
   with speech_lock:  # lock to ensure only one thread speaks at a time
       engine.say(text)
       engine.runAndWait()

# Function to mimic initial communication before takeoff
def pre_takeoff():
   speak("Control Tower: Flight and weather conditions look good. Ready for takeoff.")

# Function to simulate in-flight status checks
def inflight_status_check():
   while not emergency_event.is_set():
       time.sleep(10)  # Regular interval for status checks- Move to JS?
       with status_lock:  
           if not emergency_event.is_set():  # when no emergency 
               speak("Control Tower: Please report your flight status, patient status, and ETA.")
               if status_report_event.wait(30):  # Wait for user to report back
                   status_report_event.clear()
               else: 
                   speak("Control Tower: Awaiting your status report.")

# Function to provide emergency guidance
def administer():
   with status_lock:  
       speak("Control Tower: What are patient's current vitals?")
       if emergency_response_event.wait(30):  # Wait for user to respond
                   emergency_response_event.clear()
       else:
         speak("Control Tower: Awaiting patient's current status.")
         
       speak("Control Tower: Follow these steps:")
       speak("Control Tower: 1. Ensure the safety of all passengers.")
       speak("Control Tower: 2. Report the nature of the emergency.")
       speak("Control Tower: 3. Follow emergency landing protocols if necessary.")

# Function to handle emergencies- administering medication, fuel tank?
def emergency_guidance():
   while not emergency_event.is_set():
       time.sleep(1)
   administer()

# Function to respond to user's input
def user_input_activation():
   time.sleep(35) 
   emergency_event.set()


def main():
   # Start pre-takeoff communication
   pre_takeoff()

   #running as thread at all times but engine speaks only when event set

   # Start threads for in-flight status checks and emergency guidance
   threading.Thread(target=inflight_status_check, daemon=True).start()
   threading.Thread(target=emergency_guidance, daemon=True).start()

   # user input
   user_input_activation()

# Global events and locks
""" status_report_event = threading.Event()  #to be set when user says or should assume?
emergency_event = threading.Event()
emergency_response_event = threading.Event() #to be set when user responds with vitals"""
status_lock = threading.Lock()   


if __name__ == "__main__":
   main(status_report_event,emergency_event,emergency_response_event)
