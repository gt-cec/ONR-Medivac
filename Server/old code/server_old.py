from flask import Flask, render_template, request, jsonify, make_response
#from SimConnect import *
import logging
import datetime
import threading
import socket
import struct
import time
import re
import webbrowser


# system state variables
study_participant_id = 0
sequence=0
study_stage = '1'  # 1= nominal 2=helipad blocked 3=weather 4=vitals
destination_index = None  # will be overwritten, just giving a default value
departure_index = 19  # will be overwritten, just giving a default value
decision_state = 0  # 0=wait, 1=land
vitals_state = 0  # 0=normal, 1=emergency
airspace_emergency_state = 0  # 0=normal, 1=emergency
flight_start_time = 0
reset_user_display = 0
reset_vitals_display=0
pre_trial=0
time_to_destination=0


position = {
    "latitude": 33.7892717,
    "longitude": -84.3755556,
    "compass": 0
}

app = Flask(__name__)


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

}

# Helipad data
data = {
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
    "1": {
        "name": "Grady Memorial Hospital",
        "id": "1GE8",
        "location": "80 JESSE HILL JR DR. ATLANTA, GA 30303",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Ruffwood.png",
        "latitude": "33.7525500",
        "longitude": "-84.3820778",
    },
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
        "name": "Emory University Hospital Heliport",
        "id": "7GA8",
        "location": "1364 CLIFTON ROAD NEATLANTA, GA 30322",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7919194",
        "longitude": "-84.3225861",
    },
    "4": {
        "name": "Emory University Hospital Midtown Heliport",
        "id": "GA64",
        "location": "550 PEACHTREE ST. N.E.,ATLANTA, GA 30308",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7686667",
        "longitude": "-84.3868750",
    },
    "5": {
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
        # Nominal condition Destination
        "name": "Childrens Health Care Atlanta at Scottish Rite Heliport",
        "id": "GA11",
        "location": "1001 JOHNSON FERRY RD NE, ATLANTA, GA 30342",
        "hasHospital": True,
        "nearest": False,
        "nominal": True,
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
    "11": {
        "name": "State Capital Parking Lot Heliport",
        "id": "GA85",
        "location": "1 MARTIN LUTHER KING DRIVE ATLANTA, GA 30334",
        "hasHospital": False,
        "nearest": False,
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7474278",
        "longitude": "-84.3882583",
    },
    "12": {
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
    "13": {
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
        "nearest": False,  #set to true only in case of emergency (iteration 3 and 4)
        "nominal": False,
        "nominal_departure": False,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.8490944",  # CHANGE THIS TO THE ACCURATE ONE
        "longitude": "-84.3796944",  # CHANGE THIS TO THE ACCURATE ONE
    },
    "19": {
        # Departure Location
        "name": "Old Fourth Ward Children's Heliport ",
        "id": "GA4W",
        "location": "303 Parkway Dr NE, Atlanta, GA 30312",
        "hasHospital": True,
        "nearest": False,
        "nominal": False,
        "nominal_departure": True,
        "image1": "../static/HAIInterface/img/Mary1.png",
        "image2": "../static/HAIInterface/img/Emory.png",
        "latitude": "33.7626693",
        "longitude": "-84.3739344",
    }
}


# UDP update for MATLAB
def matlab_destination_update():
    MATLAB_IP = '127.0.0.1'
    MATLAB_PORT_LAT_MIN = 8082
    MATLAB_PORT_LONG_MIN = 8084
    MATLAB_PORT_LAND = 8086

    while True:
        time.sleep(1)

        if (destination_index is None):
            continue

        # parse the latitude and longitude
        latitude = float(data[str(destination_index)]["latitude"])
        longitude = float(data[str(destination_index)]["longitude"])
        # parse the decision state
        land = int(decision_state)
        # print("UPDATED MATLAB", latitude, longitude)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # send the location
        s.sendto(struct.pack('>f', latitude), (MATLAB_IP, MATLAB_PORT_LAT_MIN))
        s.sendto(struct.pack('>f', longitude),
                 (MATLAB_IP, MATLAB_PORT_LONG_MIN))
        # send the decision state
        s.sendto(struct.pack('>f', land), (MATLAB_IP, MATLAB_PORT_LAND))


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
    logging.info(str(datetime.datetime.now().timestamp()) + ",ID:" + str(study_participant_id) +
                 ",STAGE:" + str(study_stage) + ",SEQUENCE:" + str(sequence) + ",DATA:" + str(request.get_json()))
    return ""

# reset server parameters


@app.route("/reset", methods=["GET"])
def reset_params():
    global study_participant_id, sequence, study_stage, destination_index, departure_index, decision_state, vitals_state, airspace_emergency_state, flight_start_time, reset_user_display, reset_vitals_display, time_to_destination, pre_trial
    study_participant_id = 0
    sequence=0
    study_stage = 1
    destination_index = None # will be overwritten, just giving a default value
    departure_index = 19  # will be overwritten, just giving a default value
    decision_state = 0  # 0=normal, 1=wait
    vitals_state = 0  # 0=normal, 1=emergency
    airspace_emergency_state = 0  # 0=normal, 1=emergency
    flight_start_time = 0
    reset_user_display = 1  # resets the user display
    reset_vitals_display = 1  # resets the vitals display
    time_to_destination=10.0
    pre_trial=0  #give pre-trial survey

    return "Reset all system parameters!"

# experimenter control page


@app.route("/control", methods=["GET"])
def show_control():
    return render_template("ControlPanel/index.html", helipads=data)


def clean(s):
    return re.sub(r'[^A-Za-z0-9]+', '', s)

# set system variables


@app.route("/var", methods=["GET"])
def get_var():
    global study_participant_id,sequence,study_stage, destination_index, departure_index, decision_state, vitals_state, airspace_emergency_state, flight_start_time, reset_user_display, reset_vitals_display , aq, sm, time_to_destination, pre_trial
    if request.args.get("user-id"):
        study_participant_id = clean(request.args.get("user-id"))
        # Remove all handlers associated with the root logger object, from (https://stackoverflow.com/questions/12158048)
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # set up logging
        logging.basicConfig(filename='Logs\\' + str(study_participant_id) + '_' + str(
            study_stage) + '.log', level=logging.INFO)  # output logs to the logs file
    if request.args.get("study-stage"):
        study_stage = clean(request.args.get("study-stage"))
        # Remove all handlers associated with the root logger object, from (https://stackoverflow.com/questions/12158048)
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # set up logging
        logging.basicConfig(filename='Logs\\' + str(study_participant_id) + '_' + str(
            study_stage) + '.log', level=logging.INFO)  # output logs to the logs file
    if request.args.get("sequence"):
        sequence = clean(request.args.get("sequence"))
        # Remove all handlers associated with the root logger object, from (https://stackoverflow.com/questions/12158048)
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # set up logging
        logging.basicConfig(filename='Logs\\' + str(study_participant_id) + '_' + str(
            study_stage)+ '_' + str(sequence) + '.log', level=logging.INFO)  # output logs to the logs file
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
        

    return_dict = {"user-id": str(study_participant_id),
                   "sequence": sequence,
                   "study-stage": study_stage,
                   "destination-index": str(destination_index),
                   "departure-index": str(departure_index),
                   "decision-state": decision_state,
                   "vitals-state": vitals_state,
                   "airspace-state": airspace_emergency_state,
                   "flight-start-time": flight_start_time,
                   "reset-user-display": reset_user_display,
                   "reset-vitals-display" :reset_vitals_display,
                   "time-to-destination":time_to_destination,
                   "pre-trial":pre_trial
                   }

    # sometimes SimConnect breaks and throws an OS Error, so we are saving the current lat/long when it works (or sending the last one)
    try:
        lat = aq.get("PLANE_LATITUDE")
        long = aq.get("PLANE_LONGITUDE")
        compass = aq.get("MAGNETIC_COMPASS")
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
    return render_template("HAIInterface/index.html", helipads=data)


@app.route("/hai-interface/<string:subroute>",  methods=['GET'])
def hai_interface(subroute=None):
    if subroute is None or subroute == "":
        resp = make_response(render_template("HAIInterface/index.html", helipads=data))
    elif subroute == "location":
        resp = make_response(render_template("HAIInterface/location.html", helipads=data, data=HelpData))
    elif subroute == "checklist":
        resp = make_response(render_template("HAIInterface/checklist.html", helipads=data))
    elif subroute == "countdown":
        resp = make_response(render_template("HAIInterface/countdown.html", helipads=data))
    elif subroute == "takeoff":
        resp = make_response(render_template("HAIInterface/takeoff_gif.html", helipads=data))
    elif subroute == "inflight":
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
        resp = make_response(render_template("HAIInterface/landed.html", helipads=data))
    elif subroute == "help":
        num = request.args.get("num")
        resp = make_response(render_template("HAIInterface/help.html", helipads=data, data=HelpData[num]))
    else:
        resp = make_response("Route in HAI Interface not found!")

    return resp

# start the webserver
if __name__ == "__main__":
    # start the destination update (for Python->MATLAB interfacing)
    t = threading.Thread(target=matlab_destination_update)
    t.start()

    # start the flask server
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.disabled = True

    app.run(host="0.0.0.0", port=8080)