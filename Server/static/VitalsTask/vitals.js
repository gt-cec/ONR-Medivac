
// resets the sensor log checklist
function resetChecklist() {
    // add the sensors and actions to the checklist variable, as FALSE
    sensors.forEach(sensor => {
        checklist[sensor] = {}
        actions.forEach(action => {
            checklist[sensor][action] = false
        })
    })
}

// checks whether all checklist items are checked
function checkChecklist() {
    // check if the checklist is complete, for the submit button
    for (let sensor in checklist) {
        for (let action in checklist[sensor]) {
            if (!checklist[sensor][action]) {
                return false
            }
        }
    }
    return true
}

// generates the numerical keypad
function generateKeypad() {
    let keypad = document.getElementById("keypad")

    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, "✓", 0, "DEL"]
    // create the 1-9

    for (let i in items) {
        let key = document.createElement("button")
        key.className = "keypad-key"
        key.id = "keypadkey-" + i
        key.innerHTML = items[i]
        if (items[i] == "✓") {
            key.style.backgroundColor = "#bbffb9"
            key.style.fontSize = "70pt" 
        }
        else if (items[i] == "DEL") {
            key.style.backgroundColor = "#ffb9bb"
            key.style.fontSize = "35pt" 
        }
        key.onclick = () => {
            processKeystroke(key)
        }
        keypad.appendChild(key)
    }
}

// show the keypad
function showKeypad() {
   logAction({"sensor": currentSensor, "action": "keypad open"})
    document.getElementById("keypad").style.display = "flex"
    document.getElementById("action-button-container").style.display = "none"
    displayInputValue(currentSensor)
    showingKeypad = true
}

// show the action buttons
function showActionButtons() {
   logAction({"sensor": currentSensor, "action": "show action buttons"})
    showingKeypad = false
    document.getElementById("keypad").style.display = "none"
    document.getElementById("action-button-container").style.display = "flex"
}

// support function, sets the DOM elements text and color for a given sensor
function resetSensorDOM() {
    // set the DOM elements text
    document.getElementById("action-sensor-text").innerHTML = "<b>" + currentSensor + "</b>"
    document.getElementById("action-capture-button-text").innerHTML = "<span style='float:left'>&nbsp;" + (checklist[currentSensor]["capture"] ? "☑" : "☐") + "</span>&ensp;Capture " + currentSensor.replace("O₂ ", "")
    document.getElementById("action-log-button-text").innerHTML = "<span style='float:left'>&nbsp;" + (checklist[currentSensor]["log"] ? "☑" : "☐") + "</span>&ensp;Log " + currentSensor.replace("O₂ ", "")
    document.getElementById("action-save-button-text").innerHTML = "<span style='float:left'>&nbsp;" + (checklist[currentSensor]["save"] ? "☑" : "☐") + "</span>&ensp;Save " + currentSensor.replace("O₂ ", "")
    
    document.getElementById("action-capture-button").style.backgroundColor = checklist[currentSensor]["capture"] ? "#deffb9" : "#b9deff"
    document.getElementById("action-log-button").style.backgroundColor = checklist[currentSensor]["log"] ? "#deffb9" : "#b9deff"
    document.getElementById("action-save-button").style.backgroundColor = checklist[currentSensor]["save"] ? "#deffb9" : "#b9deff"
    
    // set the DOM elements colors
    color = "black"
    colorLight = "grey"
    if (currentSensor == "Heart Rate") {
        color = heartRateButtonColor
        colorLight = heartRateBackgroundColor
    }
    if (currentSensor == "O₂ Saturation") {
        color = o2ButtonColor
        colorLight = o2BackgroundColor
    }
    if (currentSensor == "Blood Pressure") {
        color = bloodPressureButtonColor
        colorLight = bloodPressureBackgroundColor
    }

    document.getElementById("action-sensor-text").style.borderColor = color
    document.getElementById("action-pane").style.backgroundColor = colorLight

    // set the vitals amount to the current recorded value
    displayInputValue(currentSensor)

    // if all items are checked, we can ready the submit button
    readySubmitButton = checkChecklist()

    // set the submit info
    if (readySubmitButton) {
        document.getElementById("submit-button").style.backgroundColor = "#86ffbf"
    }
    else {
        document.getElementById("submit-button").style.backgroundColor = "gainsboro"
    }

}

// when the user presses a "Heart Rate", "O2 Saturation", or "Blood Pressure" button
function setSensor(sensor) {
    // if already running another item, cancel
    if (inProgress) {
       logAction({"sensor": currentSensor, "action": "open", "data": "a sensor action is in progress, cancelling"})
        return    
    }

    // if showing the keypad, ignore
    if (showingKeypad) {
       logAction({"sensor": currentSensor, "action": "open", "data": "user tried to change the sensor, but cancelled because the keypad is showing"})
        return
    }

    // log the event
   logAction({"sensor": sensor, "action": "opened sensor tab"})

    // set the global variable
    currentSensor = sensor

    // reset the sensor DOM
    resetSensorDOM()
}

// when the user presses a "Capture", "Log", or "Save" action
function recordVital(action) {
    // log the event
   logAction({"sensor": currentSensor, "action": action, "data": "action button pressed"})

    // if already running another item, cancel
    if (inProgress) {
       logAction({"sensor": currentSensor, "action": action, "data": "a sensor action is in progress, cancelling"})
        return    
    }

    // if the sensor is already checked, cancel
    if (checklist[currentSensor][action]) {
       logAction({"sensor": currentSensor, "action": action, "data": "sensor item has already been completed, cancelling"})
        return
    }

    // if the previous actions have not been checked, cancel
    for (let a in checklist[currentSensor]) {
        // end at this action
        if (action == a) {
            break
        }
        // end at a false action
        if (!checklist[currentSensor][a]) {
           logAction({"sensor": currentSensor, "action": action, "data": "sensor item needs preceeding checks, cancelling"})
            return
        }
    }

   logAction({"sensor": currentSensor, "action": action, "data": "starting sensor action"})
    
    // set the in progress flag
    inProgress = true

    // load the loading
    let progressDuration = 1  // sec: duration of sensor log progress
    let loader = document.getElementById("action-" + action + "-button-loading-bar")
 
    let width = 1
    let progressStartTime = Date.now()
    let id = setInterval(() => {
        if (width >= 100) {
            clearInterval(id)

            loader.style.width = "0%"

            // clear the in progress flag
            inProgress = false

            // set the action in the checklist
            checklist[currentSensor][action] = true
            
           logAction({"sensor": currentSensor, "action": action, "data": "sensor action complete"})

            // if the capture vital, open the keypad
            if (action == "capture") {
                showKeypad()
            }

            // reset the sensor DOM to update the visual
            resetSensorDOM()
        }
        else {
            width = 100 * (Date.now() - progressStartTime) / (progressDuration * 1000)
            loader.style.width = width + "%"
        }
    }, 10)
    
}

// when the user presses "Submit"
function submit() {
    // log the event
   logAction({"sensor": "submit", "action": "submit"})

    // if not all check boxes filled, cancel
    if (!checkChecklist()) {
       logAction({"sensor": "submit", "action": "submit", "data": "submit failed incomplete vitals checklist"})
        return
    }
    else {
       logAction({"sensor": "submit", "action": "submit", "data": "submit succeeded"})
    }

    // reset the checklist
    resetChecklist()

    // reset the vitals log
    resetVitalsLog()

    // reset the sensor DOM
    resetSensorDOM()

    // reset the timer
    resetCountupTimer()
}

// utility function to log data, adds a timestamp and a source to a given message
function log(message) {
    data = {"time": Date.now() / 1000, "source": "VitalsTask", "timer": (Date.now() - countupTimerStart) / 1000, "data": message}
    fetch("/log", {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(data)
      })
}

// format the countup timer
function formatCountupTimer(time) {
    minutes = Number.parseInt(time / 60)
    seconds = Number.parseInt(time % 60)
    format = minutes + ":" + (seconds >= 10 ? "" : "0") + seconds
    return format
}

// countup timer
function startCountupTimer() {
    window.setInterval(() => {
        let seconds = (Date.now() - countupTimerStart) / 1000
        
        // set the timer text
        document.getElementById("submit-timer").innerHTML = formatCountupTimer(seconds)
        document.getElementById("submit-timer").style.color = "black"
        //document.getElementById("submit-timer").style.backgroundColor = "rgba(255, 0, 0, " + .5 * ((seconds - countupTimerWarningStart) / (countupTimerWarningRed - countupTimerWarningStart)) + ")"
        
        // visual formatting
       /*  if (seconds > countupTimerWarningRed) {
            document.getElementById("submit-timer").style.color = "darkred"
            document.getElementById("submit-timer").style.fontWeight = 600
        }
        else {
            document.getElementById("submit-timer").style.color = "black"
            document.getElementById("submit-timer").style.backgroundColor = "rgba(255, 0, 0, " + .5 * ((seconds - countupTimerWarningStart) / (countupTimerWarningRed - countupTimerWarningStart)) + ")"
        } */
    }, 50)
}

// reset timer
function resetCountupTimer() {
    countupTimerStart = Date.now()
}

// reset the vitals log values
function resetVitalsLog() {
    vitalsLog["Heart Rate"] = 0
    vitalsLog["O₂ Saturation"] = 0
    vitalsLog["Blood Pressure"] = 0
}

// process a keystroke
function processKeystroke(obj) {
    idx = parseInt(obj.id.substr(obj.id.indexOf("-") + 1)) + 1
    // submit
    if (idx == 10) {
        showActionButtons()
    }
    else if (idx == 12) {
        vitalsLog[currentSensor] = parseInt(vitalsLog[currentSensor] / 10)
    }
    else {
        vitalsLog[currentSensor] *= 10
        vitalsLog[currentSensor] += idx == 11 ? 0 : idx
    }
    displayInputValue(currentSensor)
   logAction({"sensor": currentSensor, "action": "keypad press", "key": idx, "value": vitalsLog[currentSensor]})
}


function displayInputValue(currentSensor) {
    // for the blood pressure, show a / after the 3rd digit
    if (currentSensor == "Blood Pressure") {
        if (vitalsLog[currentSensor] >= 100) {
            document.getElementById("keypad-value").innerHTML = vitalsLog[currentSensor].toString().substr(0, 3) + "&nbsp;/&nbsp;" + vitalsLog[currentSensor].toString().substr(3)
        }
        else {
            document.getElementById("keypad-value").innerHTML = vitalsLog[currentSensor] + "<span style='color:grey'>&nbsp;/&nbsp;</span>"
        }
    }
    // for other sensors, just show the value
    else {
        document.getElementById("keypad-value").innerHTML = vitalsLog[currentSensor]
    }
}