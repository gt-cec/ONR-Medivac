import threading
import time
import pyttsx3
import requests


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
#currentVoice = engine.setProperty('voice', voices[2].id)
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

def delay(t):
     while t>0:
        t=t-1
        #print("t=",t)
 

def fetch_states():
    try:
        response = requests.post("http://127.0.0.1:8080/state")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching states: {e}")
    return None

def fetch_var():
    try:
        response = requests.get("http://127.0.0.1:8080/var")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching states: {e}")
    return None

# Function to mimic initial communication before takeoff
def pre_takeoff():
   print('Received')
   with status_lock:  
        print('Speaking!')
   speak("Control Tower: Callsign N A S X G  S, radio C O M M 1 ")
   delay(10)
   print('speaking line 2')
   speak("Control Tower: Flight and weather conditions look good. Ready for takeoff.")
   print('speaking line 3')
   #speak('Set the Callsign NASXGS and Radio to COMM1')
   requests.post("http://127.0.0.1:8080/state", json={"event": "takeoff_event", "action": "clear"}) #clearing takeoff event
   print('sent request to clear takeoff event')
      

# Function to simulate in-flight status checks
def inflight_status_check(states):
    global last_radio_update 
      #print('Inflight radio updates ', states)
      #while not states["emergency_event"]:
         #print('radio updates')
    current_time = time.time()
    #print("last update", (current_time -last_radio_update))
    #speak("Inflight")
    if not states["emergency_event"] and (current_time - last_radio_update >90):  # when no emergency and last radio update >90s ago (assuming 30s gap + 30s vitals + 30s gap)
        print("here")
        with status_lock:  
            print("Asking for radio updates")
            speak("Control Tower: Please report your flight status, patient status, and ETA.")
            if states["response_event"]: #user reported back
                print('Transmit button pressed')
                requests.post("http://127.0.0.1:8080/state", json={"event": "response_event", "action":"clear"})
                print('sent request to clear response event')
            else:
                delay(55) # Wait for user to report back? --> set with transmit button?
        last_radio_update = time.time()
        #radio_update_complete.set()
        requests.post("http://127.0.0.1:8080/state", json={"event": "radioUpdateComplete", "action":"set"})
        print('sent request to set radio update complete')
    delay(100)

# Function to provide medicine administration guidance
def administer():
   print('administering medication')
   with status_lock:  
       speak("Control Tower: The patient has a history of altitude sickness")
       #time.sleep(45) # Wait for user to report back
       speak("Follow these steps:")
       speak("1. Verify patient's identity and medication orders")
       speak("2. Prepare the medication and IV equipment")
       speak("3. Administer the dexamethasone via IV push")
       speak("4. Monitor patient's vital signs and response to the medication")
       speak("5. Inform the pilot to change the altitude to 1000 feet")
       requests.post("http://127.0.0.1:8080/state", json={"event": "administer_event", "action":"clear"}) #clearing adminster event
       print('sent request to clear administer event')
       

def continueEmory():
   print('Continue to Emory')
   with status_lock:  
      speak("Control Tower: Continue flying to Emory University Hospital")
      requests.post("http://127.0.0.1:8080/state", json={"event": "tank_event", "action":"clear"}) #clearing tank event
      print('sent request to clear tank_event')

def flyOldForth():
   print('reroute to Oldforth')
   with status_lock:  
      speak("Control Tower: Reroute to Old Forth Hospital")
      requests.post("http://127.0.0.1:8080/state", json={"event": "engine_event", "action":"clear"}) #clearing engine event
      print('sent request to clear engine_event')

def set_radio_update():  
    print("Radio Update completed")
   
def set_response_event():
    print("Emergency situation detected")
    

def handle_emergency():
    print("Emergency situation detected")

#giving reference to the function that needs to be called depending to event set, not calling the function 
event_handlers = {
   #"radioUpdateComplete": set_radio_update,
    #"inflight_event":inflight_status_check, 
    "takeoff_event": pre_takeoff,
    #"response_event": set_response_event,
    "administer_event": administer,
    "engine_event": flyOldForth,
    "tank_event": continueEmory,
    #"status_response_event": set_status_response_event,
    #"emergency_event": handle_emergency

}

def main():
    global PW,  ET, EF,receive,transmit,study_stage 
    while True:
        states = fetch_states()
        data= fetch_var()

        if data:
            PW=int(data["pressure-warning"])
            EF=int(data["engine-failure"])
            ET=int(data["empty-tank"])
            receive=int(data["receive"])
            transmit=data["transmit"] 
            study_stage=int(data["study-stage"])

        print("receive:",receive)
        print("study_stage:",study_stage)
        if (receive==1 and study_stage==2):
            administer()  
        elif(receive==1 and study_stage==3):
            print('Satisfied calling func')
            continueEmory()
        elif(receive==1 and study_stage==4):
            flyOldForth()

        if states:
           if (PW==1 or EF==1 or ET==1):
                states["emergency_event"]=True
                requests.post("http://127.0.0.1:8080/state", json={"event": "emergency_event", "action":"set"}) #clearing engine event
                print('sent request to set emergency_event')
           if transmit==1:
                states["response_event"]=True      
           if states["inflight_event"] and not states["emergency_event"]:
                inflight_status_check(states)
           else:
                for event, is_set in states.items():    # W3school
                    if is_set and event in event_handlers:  
                        event_handlers[event]()
            
        time.sleep(1)  # Wait for 1 second before next fetch

if __name__ == "__main__":
   #main(inflight_event,status_report_event,emergency_event,administer_event,response_event,takeoff_event,tank_event, engine_event)
   main()