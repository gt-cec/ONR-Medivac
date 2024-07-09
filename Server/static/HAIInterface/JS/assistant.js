
 // Function to show assistant indicator
 function showAssistant() {
    console.log('showing')
    document.body.classList.add('assistant-dull-background', 'active');
    document.getElementById('assistant').style.display = 'block';
    document.getElementById('userTextBox').style.display = 'block';
    document.getElementById('userTextBox').innerHTML = "<b>Jarvis: </b>Hello, What can I help you with?<br><br>" +
    "You could say: <i>Change Destination</i>, <i>Emergency</i>, <i>Open Map</i>",  "<i>ETA</i>";
    
}

// Function to hide assistant indicator
function hideAssistant() {
    console.log('hiding')
    setTimeout(() => {
        document.getElementById('assistant').style.display = 'none';
        document.body.classList.remove('assistant-dull-background', 'active');
        document.getElementById('userTextBox').style.display = 'none';
    }, 1500)  // wait 3 seconds to hide
    
}

//Keywords and corresponding routes
const keywordsRoutes = {
    //"help": "http://127.0.0.1:8080/hai-interface/help",
    "altitude": "/hai-interface/change-altitude",
    "height": "/hai-interface/change-altitude",
    "change": "/hai-interface/change-destination",
    "destination": "/hai-interface/change-destination",
    "emergency": "/hai-interface/inflight",
    "map": "/hai-interface/inflight"+ showMap,
    "ETA": "hai-interface/map",
    "radio":document.querySelector('.radiopanel').classList.toggle('open') +  document.querySelector('.radiopanel').classList.toggle('open'),     
    //add more keywords and routes 
}  

function performAction(usertext){
    usertext = usertext.toLowerCase();
    console.log("Looking");

    for (let [keyword, route] of Object.entries(keywordsRoutes)) {
        if (usertext.includes(keyword)) {
            txt="Going to "+ keyword
            window.location.href = route
            exit()
            //return; // Exit function after finding the first matching keyword
        }
        else{
            // If no keyword is found 
            console.log("Sorry, didn't find " + usertext);
            txt = "<b>Jarvis: </b> Sorry, didn't find " + usertext;
            }  
    }
    const userTextBox = document.getElementById('userTextBox');
    const newContent = document.createElement('div');
    newContent.innerHTML = txt;
    userTextBox.appendChild(newContent);
    userTextBox.scrollTop = userTextBox.scrollHeight; // Auto-scroll to the bottom
    }


// Function to handle user text
function handleUserText(text) {
    console.log('text')
    //console.log("prevtext:",prevText)
    
    //document.getElementById('userTextBox').style.display = 'block';
    const userTextBox = document.getElementById('userTextBox');
    const newContent = document.createElement('div');
    newContent.innerHTML = "<b>Participant: </b> " + text;
    userTextBox.appendChild(newContent);
    //userTextBox.scrollTop = userTextBox.scrollHeight; // Auto-scroll to the bottom
    //performAction(text)
}

function initAssistant()
{  let prevTxt=""
    async function fetchData() {
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

            if (json.userText && json.userText !== prevText) {
                console.log("Received new text:", json.userText);
                try {
                    handleUserText(json.userText);
                    prevText = json.userText;
                } catch (error) {
                    console.error("Error in handleUserText:", error);
                }
            } 

            /* if (json.userText != "") {
                console.log("Received text")
                handleUserText(json.userText);
            } */

            if (json.assistantIsActive) {
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
    setInterval(fetchData, 2500);

    //console.log("Performing initial fetchData call");
    //fetchData();
}