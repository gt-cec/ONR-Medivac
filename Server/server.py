from flask import Flask, render_template, request, jsonify, make_response
import logging
import socket
import struct
import time
import re
import webbrowser
from flask_socketio import SocketIO
import json
from vars.helipads import data
from vars.help import HelpData
from vars.initialization import *
from vars.routes import keywords_routes
from vars.simconnect import position
from vars.threads import *
from utility import *

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading", logger=False, cors_allowed_origins="*")  # Ensure Flask remains non-blocking

# Set the logging level
app.logger.setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)

# Creating simconnection
try:
    sm = SimConnect()
    aq = AircraftRequests(sm, _time=10)
except:
    sm = None
    aq = None

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
    global takeoffEvent, engine_failure, pressure_warning, empty_tank, vitals_state, weather_emergency, altitude_alert,jarvis_event, emergency_state 
    
    if(airspace_emergency_state==1 or vitals_state==1 or engine_failure==1 or pressure_warning==1 or empty_tank==1 or weather_emergency==1 or altitude_alert==1):
        emergency_event.set()
        emergency_state=1
        print('Emergency event set')

    if(emergency_event.is_set() and airspace_emergency_state==0 and vitals_state==0 and engine_failure==0 and pressure_warning==0 and empty_tank==0 and weather_emergency==0 and altitude_alert==0):
        emergency_event.clear()
        emergency_state=0
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
    data = request.get_json()
    return utility.log(data, study_participant_id, study_stage, sequence)

# reset server parameters
@app.route("/reset", methods=["GET"])
def reset_params():
    global study_participant_id, sequence, study_stage, destination_index, departure_index, decision_state, dest_changed, vitals_state, airspace_emergency_state, emergency_state, satisfied, warning_satisfied, weather_satisfied, altitude_satisfied, flight_start_time, reset_user_display, reset_vitals_display, time_to_destination, pre_trial, post_trial, change_altitude,engine_failure, pressure_warning, empty_tank, weather_emergency, altitude_alert, emergency_page,rd_page,ca_page,cd_page,map_page, radio_page,transmit,receive, takeoff,approach_clear, user_text_audio, prev_text,received_text, prompt_cycle_started

    study_participant_id = 0
    sequence=0
    study_stage = 1
    destination_index = None # will be overwritten, just giving a default value
    departure_index = 21  # will be overwritten, just giving a default value
    decision_state = 0  # 0=normal, 1=wait
    vitals_state = 0  # 0=normal, 1=emergency
    airspace_emergency_state = 0  # 0=normal, 1=emergency
    emergency_state=0  # 0=normal, 1=emergency
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
    prompt_cycle_started = False

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

# set system variables
@app.route("/var", methods=["GET"])
def get_var():
    global study_participant_id,sequence,study_stage, destination_index, departure_index, decision_state, dest_changed, emergency_state, vitals_state, airspace_emergency_state, satisfied, warning_satisfied, weather_satisfied, altitude_satisfied, flight_start_time, reset_user_display, reset_vitals_display , aq, sm, time_to_destination, pre_trial, post_trial, change_altitude, engine_failure, pressure_warning, empty_tank, weather_emergency, altitude_alert, emergency_page, rd_page, ca_page, cd_page, map_page, radio_page, transmit, receive, takeoff, approach_clear, prompt_cycle_started
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
    if request.args.get("emergency-state"):
        emergency_state = clean(request.args.get(
            "emergency-state"))  # 0=no emergency, 1=atleast 1 emergency happening 
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
    if request.args.get("prompt-cycle-started"):  
        prompt_cycle_started = clean(request.args.get("prompt-cycle-started")) 

    if(airspace_emergency_state==1 or vitals_state==1 or engine_failure==1 or pressure_warning==1 or empty_tank==1 or weather_emergency==1 or altitude_alert==1):
        emergency_state=1
        print('Emergency event set')

    if( airspace_emergency_state==0 and vitals_state==0 and engine_failure==0 and pressure_warning==0 and empty_tank==0 and weather_emergency==0 and altitude_alert==0):
        emergency_state=0
        print('Emergency event cleared')
   
    return_dict = {"user-id": str(study_participant_id),
                   "sequence": sequence,
                   "study-stage": study_stage,
                   "destination-index": str(destination_index),
                   "departure-index": str(departure_index),
                   "decision-state": decision_state,
                   "vitals-state": vitals_state,
                   "airspace-state": airspace_emergency_state,
                   "emergency-state":emergency_state,
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
                   "prompt-cycle-started": prompt_cycle_started
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

@socketio.on("send_text")
def handle_send_text(data):
    # Load the received data (e.g., text message and stress_level)
    data = json.loads(data)
    text = data.get("text", "").strip()
    stress_level=data["stress_level"]
    print("Received Text", text)
    # Check if the text is empty after stripping
    if not text:
        return  # Do nothing if there's no valid text
    # Clean the text (remove non-alphanumeric characters except common punctuation)
    text = re.sub(r"[^a-zA-Z0-9.,'?! ]", "", text)

    # Send text to JS speech synthesizer
    socketio.emit("speak_text", {"text": text, "stress_level":stress_level})

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
    print(data)
    #Forwards control commands from the controller panel to the user's screen
    print(f"Control Command: {data}")
    if (action=="check"):
         socketio.emit("check_command", data)
    else:
        socketio.emit("execute_command", data)
   
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=False, log_output=False,allow_unsafe_werkzeug=True)
