from flask import Flask, render_template, request, jsonify, make_response
import os
import requests
import zipfile
import logging
import datetime
import threading
import socket
import struct
import time
import asyncio
import re
import webbrowser
from flask_socketio import SocketIO
import threading
import websockets
import json
from TTS.api import TTS
import multiprocessing
import sounddevice as sd
import soundfile as sf
import numpy as np

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading", logger=False, cors_allowed_origins="*")  # Ensure Flask remains non-blocking

# Initialize TTS
#tts = TTS("tts_models/multilingual/multi-dataset/your_tts", progress_bar=False).to("cpu")
os.environ['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False).to("cpu") 




# system state variables
study_participant_id = 0
sequence=0
study_stage = '1'  # 1= nominal 2=change altitude 3= empty fuel 4=pressure warninhg+ engine failure
destination_index = None  # will be overwritten, just giving a default value
departure_index = 21 # will be overwritten, just giving a default value(Miller Farm)
decision_state = 0  # 0=wait, 1=land
vitals_state = 0  # 0=normal, 1=emergency
airspace_emergency_state = 0  # 0=normal, 1=emergency
satisfied = False  # becomes true when emergency occured
warning_satisfied = False  # becomes true when pressure warning appears
weather_satisfied = False  # becomes true when weather emergency occurs
altitude_satisfied = False  # becomes true when altitude alert appears
dest_changed=False # becomes true when destination changed during emergency
flight_start_time = 0
reset_user_display = 0
reset_vitals_display=0
pre_trial=0
post_trial=0
time_to_destination=10
current_altitude=None
change_altitude=0
pressure_warning=0
engine_failure=0
empty_tank=0
weather_emergency=0
altitude_alert=0
emergency_page=0
rd_page=0
ca_page=0
cd_page=0
map_page=0
radio_page=0
transmit=0
receive=0
takeoff=0
approach_clear=0

# Global variables
active_assistant = 'T'
user_text_audio = ""
prev_text=""
received_text=""
message = 'deactivate_assistant'
emergency = False
last_radio_update = 0
last_time_set=None

#lock to protect the global variable
lock = threading.Lock()

# start Jarvis
# Jarvis.start_jarvis()

# create instances of event for voice assistant
jarvis_event = threading.Event()
jarvis_event.clear() #not set
 
#for radio comms
status_report_event = threading.Event()  #to be set when participant gives the radio update
status_report_event.clear()
administer_event = threading.Event()
administer_event.clear()
response_event = threading.Event() #to be set when user responds with vitals during vitals emergency or should assumes gives answer?
response_event.clear()
takeoff_event= threading.Event() #to be set when ready for takeoff
takeoff_event.clear()
tank_event = threading.Event() #to be set when user responds with vitals for sceanrio 2 altitude emergency
tank_event.clear()
engine_event = threading.Event() #to be set when engine failure 
engine_event.clear()
emergency_event= threading.Event() #to be set when any of the emergency occurs
emergency_event.clear()
inflight_event=threading.Event() #when inflight
inflight_event.clear()
radio_update_complete = threading.Event() # for ensuring regular radio updates and vitals don't overlap
radio_update_complete.clear()
sensor_event= threading.Event() # to be set when pressure waning (miscalbirated sensor) comes up
sensor_event.clear()
weather_event= threading.Event() # to be set when weather emergency occurs
weather_event.clear()
altitude_event= threading.Event() # to be set when altitude alert comes up
altitude_event.clear()
acknowledge= threading.Event()
acknowledge.clear()
jarvis_emergency= threading.Event()
jarvis_emergency.clear()
engine_failure_emergency= threading.Event()
engine_failure_emergency.clear()
empty_fuel_emergency= threading.Event()
empty_fuel_emergency.clear()
weather_emergency_event= threading.Event()
weather_emergency_event.clear()
altitude_warning_alert=threading.Event()
altitude_warning_alert.clear()
pressure_warning_alert= threading.Event()
pressure_warning_alert.clear()
stop_engine=threading.Event()
stop_engine.clear()

events = {
    'radioUpdateComplete': radio_update_complete,
    'status_report': status_report_event,
    'takeoff_event': takeoff_event,
    'response_event': response_event,
    'administer_event': administer_event,
    'engine_event': engine_event,
    'tank_event': tank_event,
    'emergency_event': emergency_event,
    'inflight_event': inflight_event,
    'sensor_event': sensor_event,
    'weather_event': weather_event,
    'altitude_event': altitude_event,
    "acknowledge":acknowledge,
    "jarvis_emergency":jarvis_emergency,
    "engine_failure_emergency":engine_failure_emergency,
    "empty_fuel_emergency":empty_fuel_emergency,
    "weather_emergency_event":weather_emergency_event,
    "altitude_warning_alert":altitude_warning_alert,
    "pressure_warning_alert":pressure_warning_alert,
    "stop_engine":stop_engine,
    "jarvis_event":jarvis_event
}

#radio variables
takeoffEvent=False

position = {
    "latitude": 33.7892717,
    "longitude": -84.3755556,
    "compass": 0,
    "altitude": 0.0
}



# Creating simconnection
try:
    sm = SimConnect()
    aq = AircraftRequests(sm, _time=10)
except:
    sm = None
    aq = None

request_location = [
    'ALTITUDE',
    'LATITUDE',
    'LONGITUDE',
    'KOHLSMAN',
]

request_airspeed = [
    'AIRSPEED_TRUE',
    'AIRSPEED_INDICATE',
    'AIRSPEED_TRUE CALIBRATE',
    'AIRSPEED_BARBER POLE',
    'AIRSPEED_MACH',
]

request_compass = [
    'WISKEY_COMPASS_INDICATION_DEGREES',
    'PARTIAL_PANEL_COMPASS',
    'ADF_CARD',  # ADF compass rose setting
    'MAGNETIC_COMPASS',  # Compass reading
    'INDUCTOR_COMPASS_PERCENT_DEVIATION',  # Inductor compass deviation reading
    'INDUCTOR_COMPASS_HEADING_REF',  # Inductor compass heading
]

request_vertical_speed = [
    'VELOCITY_BODY_Y',  # True vertical speed, relative to aircraft axis
    'RELATIVE_WIND_VELOCITY_BODY_Y',  # Vertical speed relative to wind
    'VERTICAL_SPEED',  # Vertical speed indication
    'GPS_WP_VERTICAL_SPEED',  # Vertical speed to waypoint
]

# Help button description
HelpData = {
    "1": {
        "desp": " This aircraft is flying to location indicated. Please click CONFIRM to confirm this is where you want the aircraft to fly. If this is not where you want to fly or would like to change the location, please click CANCEL. You will be directed to the page where you will be able to change the destination "
    },

    "2": {
        "desp": " This is a mandatory checklist for flying to ensure your and the baby's safety. Please check the boxes to indicate the completion of the task. Only after ALL the boxes are checked, a button to proceed will show up. If any of the checklists can't be completed or if you would like to abort the mission, please click on the ABORT button "
    },

    "3": {
        "desp": " This aircraft is now taking off. Please sit back and relax. If you would like to abort, please click ABORT "
    },

    "4": {
        "desp": " If you would like to change the destination please click CHANGE DESTINATION. You will be provided with a list of nearby hospitals. If you would like to fly back to Emory Clinic at Old Fourth Ward, please click RETURN TO DEPARTURE LOCATION. In case of emergency or to land to a nearby helipad, please click EMERGENCY LANDING. You will be provided with a list of nearby helipads"
    },

    "5": {
        "desp": " This page allows you to fly to a different hospital. The drop down menu provides a list of hospitals.  The nearest hospital is highlighted in green. Please select one and hit SUBMIT. If you are unsure and would like the AI to make a decision for you, please select AI chooses from the drop-down menu "
    },

    "6": {
        "desp": " This page allows you to change the destination. The drop down menu provides a list of helipads. The nearest helipad is highlighted in green. The helipads with hospital facilities have a red cross hospital icon along with the name. Please select one and hit SUBMIT. If you are unsure and would like the AI to make a decision for you, please select AI chooses from the drop-down menu"
    },

    "7": {
        "desp": " The aircraft has received confirmation to land on HELIPAD 1. Please check the boxes to indicat that you looked out of the window and can see HELIPAD. Only after the boxes are checked, you can proceed forward. If it is safe to land on the indicated helipad, please click SAFE TO LAND. To change the helipad, please select DIFFERENT HELIPAD. If you are ready to land, please click CONFIRM. If you are not ready or will like to chang the helipad or location, please click NO"
    },

    "8": {
        "desp": " This aircraft is now descending. Please sit back and relax. If you would like to abort, please click ABORT "
    },

    "9": {
        "desp": " This aircraft has landed. It is now safe to debuckle and deplane. Make sure to take the baby and your belongings "
    },
     "9": {
        "desp": "  This page allows you to request the AI pilot to change the altitude. If you would like to know the current altitude, look for the altitude gauge in the backup flight gauges panel. For changing the altitude, select the altitude you want to request from the drop down and hit SUBMIT. If you are unsure, contact Control for assistance "
    },
}

# Helipad data
data = {
    "-1": {
        "name": "St. Marys Health Care Systems Heliport",
        "location": "1230 BAXTER ST.ATHENS, GA 30606-3791",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Mary.png",
        "latitude": "33.9484611",
        "longitude": "-83.4070611",
    },
    "0": {
        "name": "St. Marys Health Care Systems Heliport",
        "location": "1230 BAXTER ST.ATHENS, GA 30606-3791",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Mary.png",
        "latitude": "33.9484611",
        "longitude": "-83.4070611",
    },
    # "1": {
    #     "name": "Grady Memorial Hospital",
    #     "id": "1GE8",
    #     "location": "80 JESSE HILL JR DR. ATLANTA, GA 30303",
    #     "hasHospital": True,
    #     "nearest": False,
    #     "nominal": False,
    #     "nominal_departure": False,
    #     "image1": "../static/HAIInterface/img/Mary1.png",
    #     "image2": "../static/HAIInterface/img/Ruffwood.png",
    #     "latitude": "33.7525500",
    #     "longitude": "-84.3820778",
    # }, 
    "2": {
        "name": "Ruffwood Heliport",
        "id": "73GA",
        "location": "1425 North Harris Ridge, Atlanta, GA 30327",
        "hasHospital": False,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Ruffwood.png",
        "latitude": "33.8825000",
        "longitude": "-84.4358333",
    },
    "3": {
        #Landing for all scenarios except 4 Medevac II
        "name": "Emory University Hospital Heliport",
        "id": "7GA8",
        "location": "1364 CLIFTON ROAD NE, ATLANTA, GA 30322",
        "hasHospital": True,
        "nearest": False,
        "nominal": True,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        # "latitude": "33.7919194", original
        # "longitude": "-84.3225861", original
        "latitude": "33.795954485398155", #offset for visibility to Chappell Park baseball fields
        "longitude": "-84.32677430346087", #offset to chappel Park baseball fields
    },
    # "4": {
    #     "name": "Emory University Hospital Midtown Heliport",
    #     "id": "GA64",
    #     "location": "550 PEACHTREE ST. N.E.,ATLANTA, GA 30308",
    #     "hasHospital": True,
    #     "nearest": False,
    #     "nominal": False,
    #     "nominal_departure": False,
    #     "image1": "../static/HAIInterface/img/Mary1.png",
    #     "image2": "../static/HAIInterface/img/Emory.png",
    #     "latitude": "33.7686667",
    #     "longitude": "-84.3868750",
    # }, 
    "5": {
         # Nearest for high workload scenario (AI suggestion)
        "name": "Hilton Garden Inn Downtown Heliport",
        "id": "7GA6",
        "location": "300 MARIETTA ST. NW, STE 304, ATLANTA, GA 30313",
        "hasHospital": False,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7619444",
        "longitude": "-84.3955556",
    },
    "6": {
        "name": "Childrens Health Care Atlanta at Scottish Rite Heliport",
        "id": "GA11",
        "location": "1001 JOHNSON FERRY RD NE, ATLANTA, GA 30342",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.9072222",
        "longitude": "-84.3541667",
    },
    "7": {
        "name": "Children's Healthcare of Atlanta-Egleston Heliport",
        "id": "60GA",
        "location": "1405 CLIFTON RD,ATLANTA, GA 30322",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7940833",
        "longitude": "-84.3192833",
    },
    "8": {
        "name": "Bridge Building Heliport",
        "id": "GA66",
        "location": "11968 PEACHTREE RD,ATLANTA, GA 30309",
        "hasHospital": False,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.8096694",
        "longitude": "-84.3951500",
    },
    "9": {
        "name": "WGCL-TV Heliport",
        "id": "31GA",
        "location": "425 14TH STREET NW ATLANTA, GA 30318",
        "hasHospital": False,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7873528",
        "longitude": "-84.4010528",
    },
    "10": {
        "name": "Interstate North Heliport",
        "id": "GA54",
        "location": "300 INTERSTATE N, SUITE 285 ATLANTA, GA 30339",
        "hasHospital": False,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.9008667",
        "longitude": "-84.4683361",

    },
    #  "11": {
    #     "name": "Southside Medical",
    #     "id": "GA85",
    #     "location": "1 MARTIN LUTHER KING DRIVE ATLANTA, GA 30334",
    #     "hasHospital": True,
    #     "nearest": False,
    #     "nominal": False,
    #     "nominal_departure": False,
    #     "image1": "../static/HAIInterface/img/Mary1.png",
    #     "image2": "../static/HAIInterface/img/Emory.png",
    #     "latitude": "33.7474278",
    #     "longitude": "-84.3882583",
    # }, 
    "11": {
        "name": "Rabbit Hole Heliport",
        "id": "52GA",
        "location": "2100 SUGAR CREEK TRAIL BUCKHEAD, GA 30625",
        "hasHospital": False,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.5380556",
        "longitude": "-84.4744444",
    },
    "12": {
        "name": "St Joseph's Hospital Heliport",
        "id": "GA52",
        "location": "11705 Mercy Blvd. Savannah, GA 31419",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.9083639",
        "longitude": "-84.3510194",
    },
    "14": {
        "name": "WSB-TV Heliport",
        "id": "7GA1",
        "location": "1601 W Peachtree St N.e. Atlanta, GA 30309",
        "hasHospital": False,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7992717",
        "longitude": "-84.3855556",
    },
    "15": {
        
        "name": "Northside Hospital Heliport",
        "id": "GA55",
        "location": "1000 JOHNSON FERRY RD NE ATLANTA, GA 30342",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.9098500",
        "longitude": "-84.3557639",
    },
    "16": {
        "name": "Piedmont Atlanta Hospital Heliport",
        "id": "2GA6",
        "location": "1968 PEACHTREE LANE ATLANTA, GA 30309",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.8080000",
        "longitude": "-84.3941389",
    },
    "17": {
        "name": "Legacy Medical Center Heliport",
        "id": "9GE8",
        "location": "501 FAIRBURN RD SW ATLANTA, GA 30331",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7409056",
        "longitude": "-84.5125472",
    },
    "18": {
        "name": "The Barclay Condos Heliport",
        "id": "2GE9",
        "location": "3530 PIEDMONT ROAD PH1 ATLANTA, GA 30305",
        "hasHospital": False,
        "nearest": False,  
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.8490944",  
        "longitude": "-84.3796944",  
    },
    "19": {
        # Landing helipad for high workload scenario
        "name": "Old Fourth Ward Children's Heliport ",
        "id": "GA4W",
        "location": "303 Parkway Dr NE, Atlanta, GA 30312",
        "hasHospital": True,
        "nearest": False,
        "nominal":False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        # "latitude": "33.7626693", original
        # "longitude": "-84.3739344", original
        "latitude": "33.76400330983825", # offset for visibility
        "longitude": "-84.37359282618218", #offset for visibility , 
    },
    "20": {
        "name": "Fulton County Executive Airport ",
        "id": "FTY",
        "location": "3977 Aviation Cir NW, Atlanta, GA 30336",
        "hasHospital": False,
        "nearest": False, #to be set as true for higher workload scenario
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7791264",
        "longitude": "-84.5213660",
    },
    "21": {
        # Departure Location
        "name": "Miller Farm, Airport ",
        "id": "25GA",
        "location": "5300 Leann Dr, Douglasville, GA 30135",
        "hasHospital": False,
        "nearest": False, #to be set as true for higher workload scenario
        "nominal": False,
        "nominal_departure": True,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.6595539", 
        "longitude": "-84.6629889",
    },
    "22": {
        #other scenarios- Emory University
        # Departure for all scenario 
        # 25GA Miller Farm, Dougsville  to old forth
        #https://www.google.com/maps/dir/Miller+Farm+Airport-25GA,+Leann+Dr,+Douglasville,+GA/Fulton+County+Airport+-+Brown+Field+(FTY),+Aviation+Circle+Northwest,+Atlanta,+GA/Old+Fourth+Ward,+Atlanta,+GA/@33.718646,-84.6019543,30007m/data=!3m3!1e3!4b1!5s0x88f5038ebeea134f:0x78787416707158e5!4m20!4m19!1m5!1m1!1s0x88f4df6cae05f855:0xfce85469926264b5!2m2!1d-84.6629511!2d33.6598811!1m5!1m1!1s0x88f51bfd379c09f7:0xdebb7dfce7c9c439!2m2!1d-84.5216729!2d33.7771801!1m5!1m1!1s0x88f50408dbf17f1f:0x60ccf34413430e69!2m2!1d-84.3719735!2d33.7639588!3e0?entry=ttu
        "name": "HCA Parkway Medical Center Heliport ",
        "id": "6GA3",
        "location": "999 Crestmark Blvd, Lithia Springs, GA 301223",
        "hasHospital": False,
        "nearest": False, 
        "nominal": False,
        "nominal_departure": False, 
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7780556",
        "longitude": "-84.6113889",	
    }
}

# UDP update for MATLAB
def matlab_destination_update():
    MATLAB_IP = '127.0.0.1'
    MATLAB_PORT_LAT_MIN = 8080
    MATLAB_PORT_LONG_MIN = 8088
    MATLAB_PORT_LAND = 8086
    MATLAB_PORT_TAKEOFF = 8090
    MATLAB_PORT_APPROACH_CLEAR=8092

    while True:
        time.sleep(1)
        if (destination_index is None):
            continue
        # parse the latitude and longitude
        latitude = float(data[str(destination_index)]["latitude"])
        longitude = float(data[str(destination_index)]["longitude"])
        # parse the decision state
        land_signal = int(decision_state)
        takeoff_signal = int(takeoff)
        approach_clear_signal = int(approach_clear)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # send the location
        s.sendto(struct.pack('>f', latitude), (MATLAB_IP, MATLAB_PORT_LAT_MIN))
        s.sendto(struct.pack('>f', longitude), (MATLAB_IP, MATLAB_PORT_LONG_MIN))
        # send the decision state
        s.sendto(struct.pack('>f', land_signal), (MATLAB_IP, MATLAB_PORT_LAND))
        s.sendto(struct.pack('>f', takeoff_signal), (MATLAB_IP, MATLAB_PORT_TAKEOFF))
        s.sendto(struct.pack('>f', approach_clear_signal), (MATLAB_IP, MATLAB_PORT_APPROACH_CLEAR))

# Keywords and corresponding routes
keywords_routes = {
    #"help": "http://127.0.0.1:8080/hai-interface/help",
    "altitude": "http://127.0.0.1:8080/hai-interface/change-altitude",
    "height": "http://127.0.0.1:8080/hai-interface/change-altitude",
    "destination": "http://127.0.0.1:8080/hai-interface/change-destination",
    "emergency": "http://127.0.0.1:8080/hai-interface/change-destination"
     # add more keywords and routes 
}

@app.route('/voice', methods=['POST'])
def voice():
    while True:
        def recording_started():
            print("Listening...")
            # mark the event as  set
            event.set()
            if request.method == 'POST':
                return jsonify({"type": "activate_assistant"}), 200 

        def recording_finished():
            print("Speech end detected... transcribing...")
            # mark the event as not set
            #event.clear()
            # socketio.emit("disconnect")
            # socketio.emit("type", {"type": "deactivate_assistant"})
            if request.method == 'POST':
                 return jsonify({"type": "deactivate_assistant"}), 200 

        # WebSocket server address
        WS_SERVER_ADDRESS = "ws://127.0.0.1:8080"
         # Open subroutes based on detected keywords
        def perform_action(user_text):
            user_text=user_text.lower()
            print("Looking")
            for keyword, route in keywords_routes.items():
                if keyword in user_text:
                    # Open the route in the default browser
                    webbrowser.open(route)
                    break  # Exit loop after finding the first matching keyword
            txt="Sorry, didn't find" + user_text
            print(txt)
            if request.method == 'POST':
                 return jsonify({"type": "user_text", "text": txt}), 200  

        with AudioToText(spinner=False, model="small.en", language="en", wake_words="jarvis", on_wakeword_detected=recording_started, on_recording_stop=recording_finished
        , wake_word_timeout=7.0 ) as recorder:
            print('Say "Jarvis" then speak.')
            #print(recorder.text())
            user_text=recorder.text().strip()
            print(user_text)
            if(user_text):
                 #socketio.emit("response", {"response": user_text})
                 perform_action(user_text)
            print("Done. Now we should exit. Bye!")

@app.route('/set_event', methods=['POST'])
def set_event():
    print("request received in /set_event: ", request.get_json())
    received_request= request.get_json()
    event_name = received_request["event"]
    if event_name == "reset":  # clear all events 
        for event in events:
          events[event].clear()
    elif event_name in events:
        action= received_request["action"]
        event = events[event_name]
        if action=="clear":
            event.clear()
        elif action=="set":
            event.set()
        elif action=="toggle":
            if event.is_set():
                event.clear()
                action = "cleared"
            else:
                event.set()
                action = "set"
        else:
            action= "action not found"
        print("message: Event", event_name ,action)
    else:
        print("error: Invalid event name")

    return ""

@app.route('/state', methods=['POST'])
def get_states():
    global takeoffEvent, engine_failure, pressure_warning, empty_tank, vitals_state, weather_emergency, altitude_alert,jarvis_event
    
    if(airspace_emergency_state==1 or vitals_state==1 or engine_failure==1 or pressure_warning==1 or empty_tank==1 or weather_emergency==1 or altitude_alert==1):
        emergency_event.set()
        print('Emergency event set')

    if(emergency_event.is_set() and airspace_emergency_state==0 and vitals_state==0 and engine_failure==0 and pressure_warning==0 and empty_tank==0 and weather_emergency==0 and altitude_alert==0):
        emergency_event.clear()
        print('Emergency event cleared')

    if request.is_json:
        received_request = request.get_json()
        print("request received in /state: ", received_request)
        event_name = received_request["event"]
        if event_name == "reset":  # clear all events 
            for event in events:
                events[event].clear()
        if event_name == "Radio-Update-status":  # for vitals logging
            response = {"radioUpdateComplete": radio_update_complete.is_set()}
            return jsonify(response),200
        elif event_name in events:
            action= received_request["action"]
            event = events[event_name]
            if action=="clear":
                event.clear()
            elif action=="set":
                event.set()
            elif action=="toggle":
                if event.is_set():
                    event.clear()
                    action = "cleared"
                else:
                    event.set()
                    action = "set"
            else:
                action= "action not found"
            print("message: Event", event_name ,action)
        else:
            print("error: Invalid event name")
        
    takeoffEvent=takeoff_event.is_set()
    response = {
        "radioUpdateComplete": radio_update_complete.is_set(),
        "status_report": status_report_event.is_set(),
        "takeoff_event": takeoff_event.is_set(),
        "response_event": response_event.is_set(),
        "administer_event": administer_event.is_set(),
        "engine_event": engine_event.is_set(),
        "tank_event": tank_event.is_set(),
        "emergency_event": emergency_event.is_set(),
        "inflight_event": inflight_event.is_set(),
        "sensor_event":sensor_event.is_set(),
        "weather_event":weather_event.is_set(),
        "altitude_event":altitude_event.is_set(),
        "acknowledge": acknowledge.is_set(),
        "jarvis_emergency":jarvis_emergency.is_set(),
        "engine_failure_emergency":engine_failure_emergency.is_set(),
        "empty_fuel_emergency":empty_fuel_emergency.is_set(),
        "weather_emergency_event":weather_emergency_event.is_set(),
        "altitude_warning_alert":altitude_warning_alert.is_set(),
        "pressure_warning_alert":pressure_warning_alert.is_set(),
        "stop_engine": stop_engine.is_set(),
        "jarvis_event":jarvis_event.is_set(),
    }
    return jsonify(response), 200

@app.route('/ws', methods=['POST'])
def ws():
    global user_text_audio, prev_text, jarvis_event
    #print("request received on /ws: ", request.get_json())
    received_request= request.get_json()
    
    if received_request["type"] == "activate_assistant":
        jarvis_event.set()

    if received_request["type"] == "deactivate_assistant":
        if (jarvis_event.is_set()):
            jarvis_event.clear()
    if received_request["type"] == "user_text":
       new_text = received_request["text"]
       if(str(received_request["text"])!= prev_text): #not same as prev text 
            user_text_audio = new_text
            prev_text = str(new_text)
            print("user text", user_text_audio)

    #print("user text", user_text_audio)
    response = {
        "assistantIsActive": jarvis_event.is_set(),
        "userText": user_text_audio,
    }
    return jsonify(response), 200

@app.route('/speak', methods=['POST'])
def get_text():
    global received_text
    if request.is_json:
        print("request received on speak: ", request.get_json())
        received_text_request= request.get_json()
        
        if received_text_request["type"] == "say_text":
           received_text = str(received_text_request["text"])
   
    response = {
        "received_text": received_text
    }
    return jsonify(response), 200

# index route
@app.route("/")
def index():
    return "The ONR-HAI webserver is running!"

# favicon
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

# data for MATLAB route
@app.route("/current-destination")
def current_destination():
    return jsonify({"destlatitude": data[str(destination_index)]["latitude"], "destlongitude": data[str(destination_index)]["longitude"]})

# logging route
@app.route("/log", methods=["POST"])
def log():
    log_string = f"{datetime.datetime.now().timestamp()},ID:{study_participant_id},STAGE:{study_stage},SEQUENCE:{sequence},DATA:{request.get_json()}"
    with open(f"../Logs/{study_participant_id}_{study_stage}.log", "a+") as f:
        f.write(log_string + "\n")
    return ""

# reset server parameters
@app.route("/reset", methods=["GET"])
def reset_params():
    global study_participant_id, sequence, study_stage, destination_index, departure_index, decision_state, dest_changed, vitals_state, airspace_emergency_state, satisfied, warning_satisfied, weather_satisfied, altitude_satisfied, flight_start_time, reset_user_display, reset_vitals_display, time_to_destination, pre_trial, post_trial, change_altitude,engine_failure, pressure_warning, empty_tank, weather_emergency, altitude_alert, emergency_page,rd_page,ca_page,cd_page,map_page, radio_page,transmit,receive, takeoff,approach_clear, user_text_audio, prev_text,received_text

    study_participant_id = 0
    sequence=0
    study_stage = 1
    destination_index = None # will be overwritten, just giving a default value
    departure_index = 21  # will be overwritten, just giving a default value
    decision_state = 0  # 0=normal, 1=wait
    vitals_state = 0  # 0=normal, 1=emergency
    airspace_emergency_state = 0  # 0=normal, 1=emergency
    satisfied=False
    warning_satisfied= False
    weather_satisfied=False
    altitude_satisfied= False
    dest_changed=False
    flight_start_time = 0
    reset_user_display = 1  # resets the user display
    reset_vitals_display = 1  # resets the vitals display
    time_to_destination=11.0
    pre_trial=0  #give pre-trial survey
    post_trial=0 #give post-trial survey
    change_altitude=0
    engine_failure=0
    pressure_warning=0
    empty_tank=0
    weather_emergency=0
    altitude_alert=0
    emergency_page=0
    rd_page=0
    ca_page=0
    cd_page=0
    map_page=0
    radio_page=0
    transmit=0
    receive=0
    takeoff=0
    approach_clear=0

    #clearing all events on reset 
    status_report_event.clear()
    takeoff_event.clear()
    response_event.clear()
    administer_event.clear()
    radio_update_complete.clear()
    engine_event.clear()
    tank_event.clear()
    emergency_event.clear()
    inflight_event.clear()
    sensor_event.clear()
    weather_event.clear()
    altitude_event.clear()
    jarvis_event.clear()
    acknowledge.clear()
    jarvis_emergency.clear()
    engine_failure_emergency.clear()
    empty_fuel_emergency.clear()
    weather_emergency_event.clear()
    altitude_warning_alert.clear()
    pressure_warning_alert.clear()
    stop_engine.clear()
    print('All events cleared',takeoff_event.is_set())
    
    # reseting other global variables
    user_text_audio=""
    prev_text=""
    received_text=""

    return "Reset all system parameters!"

# experimenter control page 
@app.route("/control", methods=["GET"])
def show_control():
    return render_template("ControlPanel/index.html", helipads=data)

# Wizard of Oz page
@app.route("/woz", methods=["GET"])
def show_woz():
    return render_template("ControlPanel/WizardOz.html")

@app.route("/voicecontrol", methods=["GET"])   
def voice_control():
    return render_template("ControlPanel/voiceControl.html")

def clean(s):
    return re.sub(r'[^A-Za-z0-9]+', '', s)

# set system variables
@app.route("/var", methods=["GET"])
def get_var():
    global study_participant_id,sequence,study_stage, destination_index, departure_index, decision_state, dest_changed, vitals_state, airspace_emergency_state, satisfied, warning_satisfied, weather_satisfied, altitude_satisfied, flight_start_time, reset_user_display, reset_vitals_display , aq, sm, time_to_destination, pre_trial, post_trial, change_altitude, engine_failure, pressure_warning, empty_tank, weather_emergency, altitude_alert, emergency_page, rd_page, ca_page, cd_page, map_page, radio_page, transmit, receive, takeoff, approach_clear
    if request.args.get("user-id"):
        study_participant_id = clean(request.args.get("user-id"))
    if request.args.get("study-stage"):
        study_stage = clean(request.args.get("study-stage"))
    if request.args.get("sequence"):
        sequence = clean(request.args.get("sequence"))
    if request.args.get("destination-index"):
        destination_index = clean(request.args.get("destination-index"))
    if request.args.get("departure-index"):
        departure_index = clean(request.args.get("departure-index"))
    if request.args.get("decision-state"):
        decision_state = clean(request.args.get(
            "decision-state"))  # 0=normal, 1=land
    if request.args.get("vitals-state"):
        vitals_state = clean(request.args.get(
            "vitals-state"))  # 0=normal, 1=emergency
    if request.args.get("airspace-state"):
        airspace_emergency_state = clean(request.args.get(
            "airspace-state"))  # 0=normal, 1=emergency    
    if request.args.get("satisfied"):
       satisfied = clean(request.args.get(
            "satisfied"))         
    if request.args.get("warning-satisfied"):
       warning_satisfied = clean(request.args.get(
            "warning-satisfied"))  
    if request.args.get("weather-satisfied"):
       weather_satisfied = clean(request.args.get(
            "weather-satisfied"))  
    if request.args.get("altitude-satisfied"):
       altitude_satisfied = clean(request.args.get(
            "altitude-satisfied"))  
    if request.args.get("dest-changed"):
       dest_changed = clean(request.args.get(
            "dest-changed"))    
    if request.args.get("empty-tank"):  # fuel tank empty emergency
        empty_tank = clean(request.args.get("empty-tank"))
    if request.args.get("weather-emergency"):  # weather emergencyy
        weather_emergency = clean(request.args.get("weather-emergency"))
    if request.args.get("altitude-alert"):  
        altitude_alert= clean(request.args.get("altitude-alert"))
    if request.args.get("pressure-warning"):  # pressure warninhg
        pressure_warning = clean(request.args.get("pressure-warning"))
    if request.args.get("engine-failure"):  # engine failure emergency
        engine_failure= clean(request.args.get("engine-failure"))
    if request.args.get("flight-start-time"):
        flight_start_time = request.args.get("flight-start-time")
    if request.args.get("reset-user-display"):
        reset_user_display = request.args.get("reset-user-display")
    if request.args.get("reset-vitals-display"):
        reset_vitals_display = request.args.get("reset-vitals-display")
    if request.args.get("time-to-destination"):
        time_to_destination = request.args.get("time-to-destination")
    if request.args.get("pre-trial"):
        pre_trial = request.args.get("pre-trial")
    if request.args.get("post-trial"):
        post_trial = request.args.get("post-trial")
    if request.args.get("change-altitude"):  #change altitude
        change_altitude = clean(request.args.get("change-altitude"))
    if request.args.get("emergency-page"):
        emergency_page =  clean(request.args.get("emergency-page"))
    if request.args.get("cd-page"):
        cd_page =  clean(request.args.get("cd-page"))
    if request.args.get("ca-page"):
        ca_page =  clean(request.args.get("ca-page"))
    if request.args.get("rd-page"):
        rd_page =  clean(request.args.get("rd-page"))
    if request.args.get("map-page"):
        map_page =  clean(request.args.get("map-page"))
    if request.args.get("radio-page"):
        radio_page =  clean(request.args.get("radio-page"))
    if request.args.get("receive"):  # receive from radiopanel-- for emergency guidance
        receive = clean(request.args.get("receive")) #1=receive pressed , 0=otherwise 
    if request.args.get("transmit"):  # transmit from radiopanel-- for radio updates
        transmit = clean(request.args.get("transmit")) #1=transmit pressed , 0=otherwise 
    if request.args.get("takeoff"):  # takeoff
        takeoff = clean(request.args.get("takeoff")) #1=tafeoff , 0=otherwise
    if request.args.get("approach-clear"):  
        approach_clear = clean(request.args.get("approach-clear")) #1=helipad is clear  , 0=otherwise
   
    return_dict = {"user-id": str(study_participant_id),
                   "sequence": sequence,
                   "study-stage": study_stage,
                   "destination-index": str(destination_index),
                   "departure-index": str(departure_index),
                   "decision-state": decision_state,
                   "vitals-state": vitals_state,
                   "airspace-state": airspace_emergency_state,
                   "satisfied":satisfied,
                   "warning-satisfied": warning_satisfied,
                   "weather-satisfied": weather_satisfied,
                   "altitude-satisfied": altitude_satisfied,
                   "dest-changed" :dest_changed,
                   "flight-start-time": flight_start_time,
                   "reset-user-display": reset_user_display,
                   "reset-vitals-display" :reset_vitals_display,
                   "time-to-destination":time_to_destination,
                   "pre-trial":pre_trial,
                   "post-trial":post_trial,
                   "change-altitude":change_altitude,
                   "engine-failure": engine_failure,
                   "pressure-warning": pressure_warning,
                   "empty-tank": empty_tank,
                   "altitude-alert": altitude_alert,
                   "weather-emergency": weather_emergency,
                   "emergency-page":emergency_page,
                   "cd-page":cd_page,
                   "ca-page":ca_page,
                   "rd-page":rd_page,
                   "map-page":map_page,
                   "radio-page":radio_page,
                   "receive":receive,
                   "transmit":transmit,
                   "takeoff":takeoff,
                   "approach-clear":approach_clear,
                   }

    # sometimes SimConnect breaks and throws an OS Error, so we are saving the current lat/long when it works (or sending the last one)
    try:
        lat = aq.get("PLANE_LATITUDE")
        long = aq.get("PLANE_LONGITUDE")
        compass = aq.get("MAGNETIC_COMPASS")
        alt = aq.get("PLANE_ALTITUDE")
        position["latitude"] = lat
        position["longitude"] = long
        position["compass"] = compass
        #position["altitude"] = alt
    except:
        logging.info("SimConnect Error in /var")
        try:
            sm = SimConnect()
            aq = AircraftRequests(sm, _time=10)
        except:
            pass
        pass

    return_dict["latitude"] = position["latitude"]
    return_dict["longitude"] = position["longitude"]
    return_dict["compass"] = position["compass"]
    #return_dict["altitude"] = position["altitude"]

    return jsonify(return_dict)

# Vitals Task
@app.route("/vitals/")
def vitals_index():
    return render_template("VitalsTask/index.html")

@app.route("/vitals/<string:subroute>",  methods=['GET'])
def vitals(subroute=None):
    if subroute is None or subroute == "":
        return render_template("VitalsTask/index.html")
    if subroute == "post-trial":
         return render_template("VitalsTask/post-trial.html")

# HAI Interface
@app.route("/hai-interface/")
def hai_interface_index():
    print("helipads", data)
    return render_template("HAIInterface/index.html", helipads=data)

@app.route("/hai-interface/<string:subroute>",  methods=['GET'])
def hai_interface(subroute=None):
    if subroute is None or subroute == "":
        resp = make_response(render_template("HAIInterface/index.html", helipads=data))
    elif subroute == "location":
        if(not inflight_event.is_set()): #so doesn't get set when landing
            takeoff_event.set()
            print("TOES",takeoff_event.is_set())
            print(takeoffEvent)
        resp = make_response(render_template("HAIInterface/location.html", helipads=data, data=HelpData))
    elif subroute == "checklist":
        resp = make_response(render_template("HAIInterface/checklist.html", helipads=data))
    elif subroute == "countdown":
        resp = make_response(render_template("HAIInterface/countdown.html", helipads=data))
    elif subroute == "takeoff":
        resp = make_response(render_template("HAIInterface/takeoff_gif.html", helipads=data))
    elif subroute == "inflight":
        inflight_event.set()
        print('inflight',inflight_event.is_set())
        resp = make_response(render_template("HAIInterface/inflight.html", helipads=data))
    elif subroute == "change-destination":
        resp = make_response(render_template("HAIInterface/change-destination.html", helipads=data))
    elif subroute == "landing-confirmation":
        resp = make_response(render_template("HAIInterface/landing-confirmation.html", helipads=data))
    elif subroute == "landing-countdown":
        resp = make_response(render_template("HAIInterface/landing-countdown.html", helipads=data))
    elif subroute == "landing-gif":
        resp = make_response(render_template("HAIInterface/landing-gif.html", helipads=data))
    elif subroute == "landed":
        inflight_event.clear() # clearing inflight event on landing
        print("Landed",inflight_event.is_set())
        resp = make_response(render_template("HAIInterface/landed.html", helipads=data))
    elif subroute == "help":
        num = request.args.get("num")
        resp = make_response(render_template("HAIInterface/help.html", helipads=data, data=HelpData[num]))
    elif subroute == "change-altitude":
        resp = make_response(render_template("HAIInterface/change-altitude.html", helipads=data)) # current_altitude= position["altitude"]
    else:
        resp = make_response("Route in HAI Interface not found!")
    return resp

# Global asyncio event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Function to start event loop in a separate thread
def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Start event loop in a background thread
threading.Thread(target=start_event_loop, args=(loop,), daemon=True).start()
""" 
# Shared flag to stop playback
stop_playback_flag = multiprocessing.Event()

def process_tts(text, stress_level):
    output_path = f"output_{text[:5]}.wav"
    tts.tts_to_file(text=text, file_path=output_path)
    return output_path

 #Plays audio and allow interruption using stop_flag.
def play_audio(file_path, stop_flag):
    data, samplerate = sf.read(file_path)  # Load audio file
    print('playing')
    sd.play(data,samplerate)

     # Handle mono vs stereo audio
    channels = 1 if len(data.shape) == 1 else data.shape[1]

    #Callback function to stream audio and check for stop
    def callback(outdata, frames, time, status):
        if status:
            print(status)
        if stop_flag.is_set():  # Stop playback if flag is set
            raise sd.CallbackStop
        outdata[:] = data[:frames].reshape(-1, channels)  # Fill buffer (resphaping to allow mono and stereo both)

    try:
        with sd.OutputStream(samplerate=samplerate, channels=channels, callback=callback):
            sd.sleep(int(len(data) / samplerate * 1000))  # Wait for playback to finish
        print("Playback finished.")
    except sd.CallbackStop:
        print("Playback interrupted.")

#Handle TTS request, generate audio, and plays it
def handle_request(text, stress_level):
    #output_path = process_tts(text, stress_level)  # Blocking TTS generation

    # Start playback in a separate process
    #play_process = multiprocessing.Process(target=play_audio, args=(output_path, stop_playback_flag))
    play_process = multiprocessing.Process(target=generate_audio, args=(text,stress_level))
    play_process.start()

    #return output_path, play_process

def stop_audio(play_process):
    stop_playback_flag.set()  # Signal to stop playback
    play_process.join()  # Ensure process stops
    stop_playback_flag.clear()  # Reset flag for next playback

 #Handle text received from WebSocket and play TTS audio
@socketio.on("send_text")
def handle_send_text(data):
    data = json.loads(data)
    text = data.get("text", "")
    stress_level = data.get("stress_level", "normal")

    print(f"Received text: {text}")

    # Process TTS & Start playback
    play_process = multiprocessing.Process(target=generate_audio, args=(text,stress_level))
    play_process.start()
    #output_file, playback_process = handle_request(text, stress_level)

    #return playback_process  # Return process handle in case you want to stop it later """


""" def generate_audio(text, stress_level):
    print(f"Speaking: {text}")
    
    if stress_level == "high":
        params = {"speed": 1.7, "pitch": 1.2, "emotion": "angry"}  # Emergency
    elif stress_level == "mild":
        params = {"speed": 1.5, "pitch": 1.1, "emotion": "serious"}  # Warning
    else:
        params = {"speed": 1.2, "pitch": 1.0, "emotion": "neutral"}  # Normal
    
    audio_output = tts.tts(text, pitch=1.4)
    audio_data = np.array(audio_output, dtype=np.float32)

    sd.play(audio_data, samplerate=22050)  # Play at 22.05 kHz
    while sd.get_stream().active:
         asyncio.sleep(0.1)  # Check every 100ms """


#Generate speech and play it asynchronously
async def generate_audio(text):
    audio_output = tts.tts(text)
    audio_data = np.array(audio_output, dtype=np.float32) 
    # Load audio and play asynchronously
    #data, samplerate = sf.read(audio_file, dtype="float32")

    # Play audio in a separate thread to avoid blocking
    def play_audio():
        #sd.play(data, samplerate)
        sd.play(audio_data, samplerate=22050)  # Play at 22.05 kHz
        sd.wait()

    audio_thread = threading.Thread(target=play_audio, daemon=True)
    audio_thread.start()

    # Cleanup temp file
    #os.remove(audio_file)

@socketio.on("send_text")
def handle_send_text(data):
    data = json.loads(data)
    text = data.get("text", "")
    stress_level = data.get("stress_level", "normal")

    print(f"Received text: {text}")
    if not text.strip():
        return
    else:
        text=text.strip()
        text=re.sub(r"[^a-zA-Z0-9.,'?! ]", "", text)
        
    future = asyncio.run_coroutine_threadsafe(generate_audio(text), loop)  # Run TTS in event loop
    try:
        future.result()  # Ensure execution
    except Exception as e:
        print(f"Error in TTS execution: {e}")

@socketio.on("change_altitude")
def handle_altitude(data):
    """Receive altitude change and update all clients"""
    altitude = data["altitude"]
    print(f"New altitude received: {altitude}")

    # Send update to ALL connected clients
    socketio.emit("update_altitude", {"altitude": altitude})


@socketio.on("change_destination")
def handle_destination(data):
    """Receive destination change and update all clients"""
    destination = data["destination"]
    print(f"New destination received: {destination}")
    
    # Send update to ALL connected clients
    socketio.emit("update_destination", {"destination": destination})



@socketio.on("change_variable")
def change_variable(data):
    """Receive a variable name and its changed value, and emit the update to all clients based on the variable."""
    # variable name and value from the data received
    var_name = data["variable"]
    var_value = data["value"]
    
    print(f"Received update: {var_name} = {var_value}")
    
    #  Send update to ALL connected clients based on the variable
    if var_name == "altitude":
        print(f"Altitude updated to: {var_value}")
        socketio.emit("update_altitude", {"altitude": var_value})
    
    elif var_name == "destination":
        print(f"Destination updated to: {var_value}")
        socketio.emit("update_destination", {"destination": var_value})
    
    elif var_name == "callsign":
        print(f"Callsign updated to: {var_value}")
        socketio.emit("update_callsign", {"callsign": var_value})
    
    elif var_name == "channel":
        print(f"Channel updated to: {var_value}")
        socketio.emit("update_channel", {"channel": var_value})
    
    elif var_name == "transmit":
        print(f"Transmit updated to: {var_value}")
        socketio.emit("update_transmit", {"transmit": var_value})
    
    else:
        print(f"Unknown variable: {var_name}")

@socketio.on("control_command")
def control_command(data):
    action=data['action']
    elementId=data['whichbtn']
    value=data['value']
    #Forwards control commands from the controller panel to the user's screen
    print(f"Control Command: {data}")
    if (action=="check"):
         socketio.emit("check_command", data)
    else:
        socketio.emit("execute_command", data)
   

    

if __name__ == "__main__":
    """   Jarvis.start_jarvis()  # Start listening before running Flask app
    socketio.run(app, host="0.0.0.0", port=8080) """
    socketio.run(app, host="0.0.0.0", port=8080, debug=False, log_output=False,allow_unsafe_werkzeug=True)
