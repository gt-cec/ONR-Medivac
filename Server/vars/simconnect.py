position = {
    "latitude": 33.7892717,
    "longitude": -84.3755556,
    "compass": 0,
    "altitude": 0.0
}

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