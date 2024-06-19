# Instructions

This page contains instructions for starting the ONR-HAI system.

ONR-HAI contains several independent modules that communicate with each other. Most modules run on a central Windows computer (Windows needed for Microsoft Flight Simulator) for ease of access.

We have a script, `startup.bat`, that launches the windows and programs needed to start the system. It effectively just runs everything in this document.

## Webserver (HAI Interface, Vitals Task)

The webserver has three core functions:

1. Serving dynamic webpages for many of the UI modules in the system.
2. Centralized logging "sink" for all modules to submit logs and information too via simple web requests.
3. Centralized information "source" for all modules to receive and update system state information (e.g., the participant ID, the current task stage, the online status of each module).

The webserver is made in Python using the Flask library. For organization, the webserver makes use of "simlinks" that point to other directories in the code base, so it is easier to structure modules. Each module using the webserver should have a `templates` folder with the HTML files, and a `static` folder with the JavaScript, CSS, images, and other non-HTML files used by the webpages. 

The webserver allows web browsers (on any internet-connected device) to receive interactive UI content through defined "routes". Routes are the suffix of a URL, for example, the URL `https://gatech.edu/vitals` uses the `/vitals` route. Our webserver has separate routes for each interface it serves, to be accessed by, for example, `https://(webserver address)/hai-interface`.

The webserver is also a centralized logging system. All modules -- UI components and otherwise -- can easily send logs to the webserver, and the webserver can organize logs by participant. Logs through the webserver are threadsafe, meaning race conditions like two modules sending logs at the same time will not break the logs.

To start the webserver:

1. Open Command Prompt, this may require administrator priviledges, right-clicking Command Prompt, and clicking "Open as Administrator".

2. Navigate to the ONR-HAI folder. Use `dir` to see the contents of the current directory, `cd` to change directory relatively, and `..` to go up a directory.

3. Start the webserver using `python Server/server.py`.

4. You can now open the webserver's modules by opening a web browser and navigating to the webserver's IP address (`http://127.0.0.1`, or `http://localhost`)

The following routes have been implemented:

HAI Interface: `http://localhost/hai-interface`

Vitals Task: `http://localhost/vitals-task`
