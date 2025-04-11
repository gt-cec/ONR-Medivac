
let promptCycleStarted = false;

async function checkAndStartPromptCycle() {
    try {
        const res = await fetch("/var");
        const data = await res.json();

        if (!data["prompt-cycle-started"]) {
            await fetch("/var?prompt-cycle-started=" + true)
            promptCycleStarted = true;
            startPromptScheduler();  // Begin the random scheduler
        } else {
            promptCycleStarted = true;
            startPromptScheduler();  // Continue across allowed pages
        }
    } catch (err) {
        console.error("Error checking prompt status:", err);
    }
}

if (["/hai-interface/inflight", "/hai-interface/change-destination", "/hai-interface/help", "/hai-interface/change-altitude"].includes(window.location.pathname)) {
    checkAndStartPromptCycle();
}


let taskSequence = 0;
let isPromptRunning = false;
let nextTask = Math.random() < 0.5 ? "radio" : "vitals";


function startPromptScheduler() {
    if (isPromptRunning) return;
    isPromptRunning = true;

    scheduleNextPrompt();
}

function scheduleNextPrompt() {
    const delay = 30000 + Math.random() * 50000; // Between 30s and 80s

    setTimeout(() => {
        if (timeToDestination <= 0.5) return;

        if (nextTask === "radio") {
            speakRadioPrompt();
            logAction("radio_prompt", Date.now());
            nextTask = "vitals";
        } else {
            showVitalsPrompt();
            logAction("vitals_prompt", Date.now());
            nextTask = "radio";
        }

        taskSequence++;
        scheduleNextPrompt();
    }, delay);
}


let pendingLogs = [];

function logAction(action, timestamp) {
    const logData = {
        sequence: taskSequence,
        page: window.location.pathname,
        action: action,
        timestamp: timestamp
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