let ourText = ""
const synth = window.speechSynthesis;
 
 //check for browser compatibility 
//'speechSynthesis' in window ? console.log("Web Speech API supported") : console.log("Web Speech API not supported ")

//speak function
 function JarvisSpeak(ourText){
        const utterThis = new SpeechSynthesisUtterance(ourText)
        synth.speak(utterThis)
    }
    

 
 // Function to show assistant indicator
 function showAssistant() {
    console.log('showing')
    document.body.classList.add('assistant-dull-background', 'active');
    document.getElementById('assistant').style.display = 'block';
    document.getElementById('userTextBox').style.display = 'block';
    document.getElementById('userTextBox').innerHTML = "<b>Jarvis: </b>Hello, What can I help you with?<br><br>" +
    "You could say: <i>Change Destination</i>, <i>Emergency</i>, <i>Open Map</i>",  "<i>ETA</i> <br><br>";
    
}

// Function to hide assistant indicator
function hideAssistant() {
    console.log('hiding')
    hideTimeOut= setTimeout(() => {
        document.getElementById('assistant').style.display = 'none';
        document.body.classList.remove('assistant-dull-background', 'active');
        document.getElementById('userTextBox').style.display = 'none';
        clearTimeout(hideTimeOut)
    }, 20000)  // wait 20 seconds to hide
    
}

//Keywords and corresponding routes
const keywordsRoutes = {
    //"help": "http://127.0.0.1:8080/hai-interface/help",
    "altitude": "/hai-interface/change-altitude",
    "height": "/hai-interface/change-altitude",
    "change": "/hai-interface/change-destination",
    "destination": "/hai-interface/change-destination",
    "emergency": '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1 ,
    //"map": "/hai-interface/inflight"+ showMap,
    //"ETA": "hai-interface/map",
    //"radio":document.querySelector('.radiopanel').classList.toggle('open') +  document.querySelector('.radiopanel').classList.toggle('open'),     
    //add more keywords and routes 
}  

let currentRoute = window.location.pathname;

async function performAction(usertext) {
    usertext = usertext.toLowerCase();
    console.log("Looking");
    const userTextBox = document.getElementById('userTextBox');
    const newContent = document.createElement('div');

    for (let [keyword, route] of Object.entries(keywordsRoutes)) {
        if (usertext.includes(keyword)) {
            if (route !== currentRoute) {
                //send request to set acknowledge-Jarvis say acknowledge
				const Radioresponse = await fetch("/state", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json' 
                    },
                    body: JSON.stringify({ event: 'acknowledge', action: 'set'}), 
                });
                console.log('event to say aknowledge sent')

                txt = "Going to " + keyword;
                newContent.innerHTML = txt;
                userTextBox.appendChild(newContent);
                userTextBox.scrollTop = userTextBox.scrollHeight;
                
                currentRoute = route; // Update the current route
                routingTimeOut= setTimeout(() => {
                window.location.href = route;
                clearTimeout(routingTimeOut)
                 }, 1000)  // wait 1 before going to the location
                return;
            } else {
                console.log("Already on this page");
                return;
            }
        }
    }
    
    // If no keyword is found 
    console.log("Sorry, didn't find " + usertext);
    txt = "<b>Jarvis: </b> Sorry, didn't find " + usertext;
    newContent.innerHTML = txt;
    userTextBox.appendChild(newContent);
    userTextBox.scrollTop = userTextBox.scrollHeight;
}
        


// Function to handle user text
async function handleUserText(text) {
    console.log('text:', text)
    
    //document.getElementById('userTextBox').style.display = 'block';
    const userTextBox = document.getElementById('userTextBox');
    const newContent = document.createElement('div');
    newContent.innerHTML = "<b>Participant: </b> " + text;
    userTextBox.appendChild(newContent);
    userTextBox.scrollTop = userTextBox.scrollHeight; // Auto-scroll to the bottom
    console.log("showing user text")
    performAction(text)
    await fetch("/ws", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'  // Inform the server that the request body contains JSON data
        },
        body: JSON.stringify({ type: "user_text", text: ""}), // clearing user text in server
    });

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
                headers: {
                    'Content-Type': 'application/json'  // Inform the server that the request body contains JSON data
                },
                body: JSON.stringify({ type: 'status_check'}), // Dummy body to comply with POST others throws error 400
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }
    
            const json = await response.json();
            console.log("Parsed JSON:", json);

            // if (json.userText) {
            if (json.userText && json.userText !== prevTxt){
                console.log("Received new text:", json.userText);
                try {
                    if(json.userText!==prevTxt){
                        console.log("new text")
                        //showAssistant()
                        handleUserText(json.userText);
                        prevTxt = json.userText;
                } 
            } catch (error) {
                    console.error("Error in handleUserText:", error);
                }
            } 

            /* if (json.userText != "") {
                console.log("Received text")
                handleUserText(json.userText);
            } */

            if (json.assistantIsActive|| (json.userText && json.userText !== prevTxt)) {
                showAssistant();
            }
            else {
                 hideAssistant();
            }
        } catch (err) {
            console.error(`Fetch problem: ${err.message}`);
            if (err.name === 'TypeError') {
                console.error("This might be a network issue");
            }
        }
    }

    //console.log("Setting up interval for fetchData");
    setInterval(fetchData, 1500);

    //console.log("Performing initial fetchData call");
    //fetchData();
}