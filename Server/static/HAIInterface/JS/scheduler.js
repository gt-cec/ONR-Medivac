
let promptCycleStarted = false;

async function checkAndStartPromptCycle(stopCycle=false) {
    try {
        const res = await fetch("/var");
        const data = await res.json();
       /*  const takeoff = data["takeoff"];
        const approachClear = data["approach_clear"];
        const emergency = data["emergency"]; */
        

        if (!data["prompt-cycle-started"]) {
            console.log("Updating server")
            await fetch("/var?prompt-cycle-started=" + true)
            promptCycleStarted = true;
            startPromptScheduler(stopCycle);  // Begin the random scheduler
        } else {
            promptCycleStarted = true;
            startPromptScheduler(stopCycle);  // Continue across allowed pages
        }
    } catch (err) {
        console.error("Error checking prompt status:", err);
    }
}

/* if (["/hai-interface/inflight", "/hai-interface/change-destination", "/hai-interface/help", "/hai-interface/change-altitude"].includes(window.location.pathname)) {
    checkAndStartPromptCycle();
} */


let taskSequence = 0;
let isPromptRunning = false;
let radioPromptsLeft = 5;
let vitalsPromptsLeft = 5;
let emergency=0;

const totalPrompts = radioPromptsLeft + vitalsPromptsLeft;
let currentPromptCount = 0;

let taskScheduled = false;
let nextTask = Math.random() < 0.5 ? "radio" : "vitals"; // Random first task

function scheduleNextTask(first = false, emergency = 0, stopCycle) {
    if (taskScheduled || stopCycle || currentPromptCount >= totalPrompts) return;

    const minDelay = first ? 0 : 20000;
    const maxDelay = first ? 10000 : 90000;
    const randomDelay = Math.floor(Math.random() * (maxDelay - minDelay) + minDelay);

    taskScheduled = true;

    setTimeout(() => {
        if (stopCycle || currentPromptCount >= totalPrompts) {
            taskScheduled = false;
            return;
        }

        if (nextTask === "radio" && radioPromptsLeft > 0) {
            speakRadioPrompt();
            radioPromptsLeft--;
            logAction("radio_prompt");
            nextTask = "vitals";
        } else if (nextTask === "vitals" && vitalsPromptsLeft > 0) {
            showVitalsPrompt();
            vitalsPromptsLeft--;
            logAction("vitals_prompt");
            nextTask = "radio";
        } else if (emergency == 1 && vitalsPromptsLeft == 0)
        {
            showVitalsPrompt();
        }
         else {
            // fallback in case one task runs out
            nextTask = radioPromptsLeft > 0 ? "radio" : "vitals";
        }

        currentPromptCount++;
        taskScheduled = false;
        scheduleNextTask(); // Chain the next task
    }, randomDelay);
}

function startPromptScheduler(emergency, stopCycle) {
    if (isPromptRunning) return;
    isPromptRunning = true;

    // Start the first prompt with a 0-10s delay
    scheduleNextTask(true, emergency, stopCycle);
}


let vitalsShown = false;
var bell = document.getElementById("bell"); 
// radio prompt
function speakRadioPrompt() {
    const message = "N A S X G S, this is Ground Control asking for update on flight status, patient status and estimated time to destination.";
    speakGround(message)
    console.log('Radio update');
    logAction({ "page": "radio update", "action": `radio update asked` });
    //console.log(utterance.voice)
}

// Show vitals prompt visually
function showVitalsPrompt() {
    logAction({ "page": "inflight", "action": "displaying vitals prompt" })
    console.log('vitals logging prompt')
    logAction({ "page": "vitals prompt", "action": `log vitals prompted` });
    document.getElementById('vitals').style.display = "flex"
    bell.play()
    //setInterval(bell.play(), 300);  //delayimg sound
    bell.volume = 0.2;
    // Auto-remove after 15s
    setTimeout(() => {
        document.getElementById('vitals').style.display = "none"
        logAction({ "page": "vitals prompt", "action": `auto off vitals prompt` });
        bell.pause()
    }, 15000);
}

// Ground control 
function speakGround(message) {
    const voices = window.speechSynthesis.getVoices();
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.voice = voices[2];  //Firefox
    utterance.rate = 1.2;
    utterance.pitch = 1;
    utterance.volume = 0.8;  //between 0 and 1(highest)
    window.speechSynthesis.speak(utterance);
    console.log('Ground control speaking ');
    logAction({ "page": "Ground speaking", "action": message });
    //console.log(utterance.voice)
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

// Retry logic every 5 seconds
setInterval(() => {
    if (pendingLogs.length > 0) {
        const retry = [...pendingLogs];
        pendingLogs = [];

        retry.forEach(item => sendLog(item));
    }
}, 5000);

