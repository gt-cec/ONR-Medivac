# launches the applicable windows and programs for the ONR HAI rotorcraft simulation platform

# launch the Vitals Task
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" 127.0.0.1:8080/vitals --new-window --force-app-mode

# launch the HAI Interface
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" 127.0.0.1:8080/hai-interface --new-window --force-app-mode

# launch the Patient Monitor
# TODO

# launch Microsoft Flight Simulator
# TODO

# launch the webserver
python3 Server/webserver.py
