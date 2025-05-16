import os

# system state variables
study_participant_id = 0
sequence=0
study_stage = '1'  # 1= nominal 2=change altitude 3= empty fuel 4=pressure warninhg+ engine failure
destination_index = None  # will be overwritten, just giving a default value
departure_index = 21 # will be overwritten, just giving a default value(Miller Farm)
decision_state = 0  # 0=wait, 1=land
vitals_state = 0  # 0=normal, 1=emergency
airspace_emergency_state = 0  # 0=normal, 1=emergency
emergency_state = 0 # 0=no emergency, 1= atleast 1 emergency
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
prompt_cycle_started = False
selected_helipad= None


# Global variables
active_assistant = 'T'
user_text_audio = ""
prev_text=""
received_text=""
message = 'deactivate_assistant'
emergency = False
last_time_set=None

# Initialize TTS
os.environ['TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD'] = '1'

#radio variables
takeoffEvent=False
