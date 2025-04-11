
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
let radioPromptsLeft = 5;
let vitalsPromptsLeft = 5;

const totalPrompts = radioPromptsLeft + vitalsPromptsLeft;
let currentPromptCount = 0;

let taskScheduled = false;
let nextTask = Math.random() < 0.5 ? "radio" : "vitals"; // Random first task

function scheduleNextTask() {
    if (taskScheduled || timeToDestination <= 0.5 || currentPromptCount >= totalPrompts) return;

    const minDelay = 30000;  //30s
    const maxDelay = 105000; //105s
    const randomDelay = Math.floor(Math.random() * (maxDelay - minDelay) + minDelay);

    taskScheduled = true;

    setTimeout(() => {
        if (timeToDestination <= 0.5 || currentPromptCount >= totalPrompts) {
            taskScheduled = false;
            return;
        }

        if (nextTask === "radio" && radioPromptsLeft > 0) {
            speakRadioPrompt();
            radioPromptsLeft--;
            logAction("radio_prompt", Date.now());
            nextTask = "vitals";
        } else if (nextTask === "vitals" && vitalsPromptsLeft > 0) {
            showVitalsPrompt();
            vitalsPromptsLeft--;
            logAction("vitals_prompt", Date.now());
            nextTask = "radio";
        } else {
            // If one type is exhausted, fallback to the other
            nextTask = radioPromptsLeft > 0 ? "radio" : "vitals";
        }

        currentPromptCount++;
        taskScheduled = false;

        scheduleNextTask(); // schedule next after current
    }, randomDelay);
}



function startPromptScheduler() {
    if (isPromptRunning) return;
    isPromptRunning = true;

    scheduleNextTask();
}



let pendingLogs = [];

function logAction(action, timestamp) {
    const logData = {
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