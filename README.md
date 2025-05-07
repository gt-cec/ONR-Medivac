# ONR-Medivac

The  TTS engine being used (https://github.com/coqui-ai/TTS?tab=readme-ov-file) requires an older version of python, make sure to use that. 
Virtual environment is created in conda, activate before running
1.  conda activate TTSenv
2. Start running server.py
3. Open all the routes- /voicecontrol, ControlPanel/JarvisOz

## Activate Conda

`conda activate TTSenv`

## Start the Webserver

`cd Server`
`python server.py`

## Project Routes

### Main Computer Screen

Flight Panel (main computer):
`http://127.0.0.1:8080/hai-interface/`

### Vitals Logger Screen

Vitals:
`http://127.0.0.1:8080/vitals/`

### Experiment Controller Views:

Experimenter Control (system variables):
`http://127.0.0.1:8080/control`

Wizard of Oz (sending voice commands/responses):
`http://127.0.0.1:8080/woz`

Voice Control (radio state variables):
`http://127.0.0.1:8080/voicecontrol`


