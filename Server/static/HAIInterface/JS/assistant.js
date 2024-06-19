
 // Function to show assistant indicator
 function showAssistant() {
    console.log('showing')
    document.body.classList.add('assistant-dull-background', 'active');
    document.getElementById('assistant').style.display = 'block';
    
}

// Function to hide assistant indicator
function hideAssistant() {
    console.log('hiding')
    document.getElementById('assistant').style.display = 'none';
    document.body.classList.remove('assistant-dull-background', 'active');
    setTimeout(() => {
        document.getElementById('userTextBox').style.display = 'none';
    }, 5000)
}

// Function to handle user text
function handleUserText(text) {
    console.log('text')
    document.getElementById('userTextBox').style.display = 'block';
    document.getElementById('userTextBox').innerText = text;
}

function initAssistant()
{
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
    
            if (json.userText != "") {
                console.log("Received text")
                handleUserText(json.userText);
            }
            
            if (json.assistantIsActive) {
                showAssistant();
            }
            else {
                 hideAssistant();
            }
        } catch (err) {
            console.error(`Fetch problem: ${err.message}`);
        }
    }
    setInterval(fetchData, 2500);  

    // Initial fetch
    fetchData();  
}