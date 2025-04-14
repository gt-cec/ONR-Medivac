
// === ASSISTANT VOICE INTERACTION LOGIC ===
const assistant = document.querySelector('.voice-assistant');
const feedback = document.querySelector('.voice-feedback');

const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = false;
recognition.maxAlternatives = 1;

const synth = window.speechSynthesis;

let isListening = false;

function startAssistant() {
  if (isListening) return;
  recognition.start();
  isListening = true;
  assistant.classList.remove('idle');
  assistant.classList.add('active');
  showFeedback('Listening...');
}

recognition.onresult = function(event) {
  const transcript = event.results[0][0].transcript;
  showFeedback(`You said: "${transcript}"`);
  console.log('Voice Input:', transcript);

  setTimeout(() => respondToCommand(transcript), 1500);
};

recognition.onend = function() {
  isListening = false;
  assistant.classList.remove('active');
  assistant.classList.add('idle');
};

function respondToCommand(command) {
  let response = '';
  if (/route|reroute|change.*destination/i.test(command)) {
    response = 'Routing to nearest heliport';
  } else if (/engine.*fire|failure/i.test(command)) {
    response = 'Engine failure detected. Initiating emergency protocol.';
    triggerCriticalAlert(response);
    return;
  } else {
    response = 'Command received.';
  }
  showFeedback(response);
  speak(response);
}

function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-US';
  synth.speak(utterance);
}

function showFeedback(text) {
  feedback.textContent = text;
  feedback.classList.add('visible');
  setTimeout(() => feedback.classList.remove('visible'), 4000);
}

// === EMERGENCY ALERT ===
function triggerCriticalAlert(message) {
  const alert = document.createElement('div');
  alert.className = 'critical-alert';
  alert.innerText = message;

  const ackBtn = document.createElement('button');
  ackBtn.innerText = 'Acknowledge';
  ackBtn.className = 'optional-btn';
  ackBtn.style.marginTop = '20px';
  ackBtn.onclick = () => alert.remove();
  alert.appendChild(ackBtn);

  document.body.appendChild(alert);
  speak(message);
}

// === Optional: trigger with button ===
document.getElementById('aiToggle')?.addEventListener('click', startAssistant);
