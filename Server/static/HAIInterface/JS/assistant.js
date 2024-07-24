let assistantActive = false;
let activationTimer = null;
let forceDeactivate = false;


let currentRoute = window.location.pathname;

//Keywords and corresponding routes
const keywordsRoutes = {
    //"help": "http://127.0.0.1:8080/hai-interface/help",
    "altitude": "/hai-interface/change-altitude",
    "height": "/hai-interface/change-altitude",
    "change": '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1 ,
    "destination": '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1 ,
    "emergency": '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1,
    //"map": window.location.pathname,
    //"map": () => window.dispatchEvent(new CustomEvent('mapClicked')),
     //"map": document.getElementById("map").click()
    //"map": "/hai-interface/inflight"+  document.getElementById("map").click(),
    //"ETA": "hai-interface/map",
    //"radio":document.querySelector('.radiopanel').classList.toggle('open'),     
    //add more keywords and routes 
}  

function showAssistant() {
    console.log('showing assistant');
    const activeSound = new Audio('"../static/HAIInterface/img/active.mp3');
    activeSound.loop = false;
    activeSound.play();
    document.body.classList.add('assistant-dull-background', 'active');
    document.getElementById('assistant').style.display = 'block';
    document.getElementById('userTextBox').style.display = 'block';
    document.getElementById('userTextBox').innerHTML = "<b>Jarvis: </b>Hello, What can I help you with?<br><br>" +
    "You could say: <i>Change Destination</i>, <i>Emergency</i>, <i>Open Map</i>, <i>ETA</i> <br><br>";
}

async function hideAssistant() {
    console.log('hiding assistant');
    console.log('showing assistant');
    const inactiveSound = new Audio('"../static/HAIInterface/img/inactive.mp3');
    inactiveSound.loop = false;
    inactiveSound.play();
    document.getElementById('assistant').style.display = 'none';
    document.body.classList.remove('assistant-dull-background', 'active');
    document.getElementById('userTextBox').style.display = 'none';
    await fetch("/ws", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: "deactivate_assistant" }),
    });
    // Wait for animations or transitions to complete
    await new Promise(resolve => setTimeout(resolve, 1000));
    return;
}

async function handleUserText(text) {
    console.log('Handling user text:', text);
    const userTextBox = document.getElementById('userTextBox');
    const newContent = document.createElement('div');
    newContent.innerHTML = "<b>Operator: </b> " + text;
    userTextBox.appendChild(newContent);
    userTextBox.scrollTop = userTextBox.scrollHeight;
    const actionResult = await performAction(text);
    await fetch("/ws", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'  // Inform the server that the request body contains JSON data
        },
        body: JSON.stringify({ type: "user_text", text: ""}), // clearing user text in server
    });

    // Deactivate assistant and redirect if a keyword was found
    if (actionResult.keywordFound) {
        setTimeout(() => {
            hideAssistant();
            assistantActive = false;
            window.location.href = actionResult.route;
        }, 2000);  // 2-second delay before redirecting
    } else {
        // If no keyword was found, schedule deactivation after 2 seconds
        setTimeout(() => {
            if (assistantActive) {
                hideAssistant();
                assistantActive = false;
            }
        }, 2000);
    }
    return;
}

async function performAction(usertext) {
     //send request to set acknowledge-Jarvis say acknowledge
     await fetch("/speak", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'  // Inform the server that the request body contains JSON data
        },
        body: JSON.stringify({ type: "say_text", text: "Acknowledge"}), 
    });
    usertext = usertext.toLowerCase();
    console.log("Looking for action for:", usertext);
    const userTextBox = document.getElementById('userTextBox');
    const newContent = document.createElement('div');

    if (usertext.includes("deactivate") || usertext.includes("turn off")) {
        forceDeactivate = true;
        console.log("deactivating")
        /* newContent.innerHTML = "<b>Jarvis: </b> Understood. Deactivating now.";
        userTextBox.appendChild(newContent);
        userTextBox.scrollTop = userTextBox.scrollHeight; */
        return { keywordFound: true, route: null };
    }

    for (let [keyword, route] of Object.entries(keywordsRoutes)) {
        if (usertext.includes(keyword)) {
          if (route !== currentRoute) {
            await fetch("/speak", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'  // Inform the server that the request body contains JSON data
                },
                body: JSON.stringify({ type: "say_text", text: "Processing your request"}), 
            });
                
            console.log('event to say aknowledge sent')
            newContent.innerHTML = "Going to " + keyword;
            userTextBox.appendChild(newContent);
            userTextBox.scrollTop = userTextBox.scrollHeight;

            // Simulate some processing time
            //await new Promise(resolve => setTimeout(resolve, 2000));
            console.log(`Action performed: Navigating to ${route}`);
            currentRoute = route; // Update the current route
            /* routingTimeOut= setTimeout(() => {
            window.location.href = route;
            clearTimeout(routingTimeOut)
                }, 1000)  // wait 1 before going to the location */
            return { keywordFound: true, route: route };
        }else {
            console.log("Already on this page");
            return { keywordFound: false, route: null };
        }
    }
  }

    if (usertext.includes("help")) {
        await fetch("/speak", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'  // Inform the server that the request body contains JSON data
            },
            body: JSON.stringify({ type: "say_text", text: "what can I help you with"}), 
        });    
    }
   else {
    console.log("No action found for:", usertext);
    newContent.innerHTML = "<b>Jarvis: </b> Sorry, I didn't understand that.";
    userTextBox.appendChild(newContent);
    userTextBox.scrollTop = userTextBox.scrollHeight;
    await fetch("/speak", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'  // Inform the server that the request body contains JSON data
        },
        body: JSON.stringify({ type: "say_text", text: "Unable to process your request"}), 
    });
    return { keywordFound: false, route: null };
   }
    // Simulate some processing time
   // await new Promise(resolve => setTimeout(resolve, 2000));
 }

function startActivationTimer() {
    clearActivationTimer();
    activationTimer = setTimeout(async () => {
        if (assistantActive) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            await hideAssistant();
            assistantActive = false;
        }
    }, 5000);
}

function clearActivationTimer() {
    if (activationTimer) {
        clearTimeout(activationTimer);
        activationTimer = null;
    }
}

let prevTxt=""
function initAssistant()
{  
async function fetchData() {

    // Update currentRoute if it has changed
    if (currentRoute !== window.location.pathname) {
        currentRoute = window.location.pathname;
    }
    
        try {
            const response = await fetch("/ws", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'status_check' }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const json = await response.json();
            console.log("Parsed JSON:", json);

            if (json.assistantIsActive && !assistantActive) {
                showAssistant();
                assistantActive = true;
                startActivationTimer();
            } else if (!json.assistantIsActive|| forceDeactivate) {
                if (assistantActive) {
                     hideAssistant();
                    assistantActive = false;
                    //clearActivationTimer();
                    forceDeactivate = false;
                }
            }
            /* else if (!json.assistantIsActive && ! forceDeactivate) {
                    
                    activationTimer = setTimeout(async () => {
                        if (assistantActive) {
                            await hideAssistant();
                            assistantActive = false;
                            clearActivationTimer();
                        }
                    }, 1000);
                    assistantActive = false;
                    //clearActivationTimer();
                    forceDeactivate = false;
                } */
     

            if (json.userText && json.userText !== prevTxt) {
                clearActivationTimer();
                await handleUserText(json.userText);
                startActivationTimer();
                /*if (!json.assistantIsActive || forceDeactivate) {
                    await hideAssistant();
                    assistantActive = false;
                    forceDeactivate = false;
                }*/
            }

        } catch (err) {
            console.error(`Fetch problem: ${err.message}`);
        }

        // Wait for 1.5 seconds before the next fetch
        //await new Promise(resolve => setTimeout(resolve, 1500));
    }
    setInterval(fetchData, 1500);
}
