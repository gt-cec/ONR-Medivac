import threading

# lock to protect the global variable
lock = threading.Lock()

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