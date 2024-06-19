// utility function to log data, adds a timestamp and a source to a given message
function log(message) {
    data = {"time": Date.now() / 1000, "user-id": userId, "source": "HAI Interface", "destination-index": destinationIndex, "study-stage": studyStage, "decision-state": decisionState, "vitals-state": vitalsState, "airspace-state": airspaceState,  "data": message}
    fetch("/log", {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(data)
      })
}
