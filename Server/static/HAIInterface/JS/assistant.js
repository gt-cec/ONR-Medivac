
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
    }, 1500)  // wait 1.5 seconds before hide
    
}

//Keywords and corresponding routes
const keywordsRoutes = {
    //"help": "http://127.0.0.1:8080/hai-interface/help",
    "altitude": "/hai-interface/change-altitude",
    "height": "/hai-interface/change-altitude",
    "change": "/hai-interface/change-destination",
    "destination": "/hai-interface/change-destination",
    "emergency": "/hai-interface/inflight",
    "map": "/hai-interface/inflight"+ showMap(),
    "ETA": "hai-interface/map",
    "radio":document.querySelector('.radiopanel').classList.toggle('open') +  document.querySelector('.radiopanel').classList.toggle('open'),     
    //add more keywords and routes 
}  

function performAction(usertext) {
    usertext = usertext.toLowerCase();
    console.log("Looking");

    for (let [keyword, route] of Object.entries(keywordsRoutes)) {
        if (usertext.includes(keyword)) {
            txt = "Going to " + keyword;
            // Display the message
            newContent.innerHTML = txt;
            userTextBox.appendChild(newContent);
            userTextBox.scrollTop = userTextBox.scrollHeight;
            console.log('found')
            
            // Delay the redirect
            setTimeout(() => {
                window.location.href = route;
            }, 1500); // 1.5 second delay
            return; // Exit function after finding the first matching keyword
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
    userTextBox.scrollTop = userTextBox.scrollHeight;
}
    
   


let prevText= ""
// Function to handle user text
function handleUserText(text) {
    console.log('text')
    //console.log("prevtext:",prevText)
    
    //document.getElementById('userTextBox').style.display = 'block';
    const userTextBox = document.getElementById('userTextBox');
    const newContent = document.createElement('div');
    newContent.innerHTML = "<b>Participant: </b> " + text;
    userTextBox.appendChild(newContent);
    userTextBox.scrollTop = userTextBox.scrollHeight; // Auto-scroll to the bottom
    performAction(text)
    prevText=text
    
}



function initAssistant() {
    let prevText = "";
    console.log("initAssistant function started");

    async function fetchData() {
        try {
            const response = await fetch("/ws", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: 'status_check' })
            });

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            console.log("Fetch successful, parsing JSON");
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
                console.log("Showing assistant");
                showAssistant();
            } else {
                console.log("Hiding assistant");
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