// utility function to log data, adds a timestamp and a source to a given message
function log(message) {
    data = {"time": Date.now() / 1000, "user-id": userId, "source": "HAI Interface", "destination-index": destinationIndex, "study-stage": studyStage, "decision-state": decisionState, "vitals-state": vitalsState, "airspace-state": airspaceState,  "data": message}
    fetch("/log", {
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify(data)
      })
}

let pendingLogs = [];

function logAction(page = window.location.pathname, action) {
  const logData = {
    page: page,
    action: action,
    timestamp: Date.now()
  };

  sendLog(logData);
}

function sendLog(data) {
  fetch("/log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  }).then(res => {
    if (!res.ok) throw new Error("Failed to log");
  }).catch(err => {
    console.warn("Log failed, queuing for retry:", err);
    pendingLogs.push(data);
  });
}

// Retry logic every 15 seconds
setInterval(() => {
  if (pendingLogs.length > 0) {
    const retry = [...pendingLogs];
    pendingLogs = [];

    retry.forEach(item => sendLog(item));
  }
}, 15000);