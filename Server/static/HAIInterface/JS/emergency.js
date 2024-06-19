function initEmergency() {
    let TargetIndex = 100
    // set the blink interval
    var blink = document.getElementById('blink')
    setInterval(() => {
        blink.style.opacity = 1 - blink.style.opacity
    }, 1000)

    // interval to trigger the emergency state, when needed
    setInterval(async () => {
        // only run on certain pages
        if (!["/hai-interface/location", "/hai-interface/inflight", "/hai-interface/change-destination", "/hai-interface/help"].includes(window.location.pathname)) {
            return
        }

        time_diff = (new Date()).getTime() / 1000 - flightStartTime

       /*  "21": {
          # Engine Failure and Fuel tank emergency trigger location
          "latitude": "33.772017",
          "longitude": "-84.544871",
      }, 
     */
        warning_lat = 33.776778 // new emergency location
        warning_long = -84.605523
        emergency_lat = 33.772017 // new emergency location
        emergency_long = -84.544871
        nominal_lat = 33.9098500
        nominal_long = -84.3557639

        //Calculating the distance between the current aircraft position and destination
        const R = 6371e3 // metres

        lat_diff = (nominal_lat - latitude) * Math.PI / 180  //radians
        long_diff = (nominal_long - longitude) * Math.PI / 180 //radians
        lat1 = nominal_lat

       //emergency location distance wrt to the current position of aircraft
        if (studyStage == '3' || studyStage == '4') {
            lat_diff = (emergency_lat - latitude) * Math.PI / 180  //radians
            long_diff = (emergency_long - longitude) * Math.PI / 180 //radians
            lat1 = emergency_lat
        }
        if (studyStage == '4') {
          warning_lat_diff = (warning_lat - latitude) * Math.PI / 180  //radians
          warning_long_diff = (warning_long - longitude) * Math.PI / 180 //radians
          Warning_lat1 = warning_lat
          warning_a = Math.sin(warning_lat_diff / 2) * Math.sin(warning_lat_diff / 2) +
            Math.cos(warning_lat1 * Math.PI / 180) * Math.cos(latitude * Math.PI / 180) *
            Math.sin(warning_long_diff / 2) * Math.sin(warning_long_diff / 2)
           warning_c = 2 * Math.atan2(Math.sqrt(warning_a), Math.sqrt(1 - warning_a))
          warning_dist = R * warning_c // metres
          console.log('warning_dist ', warning_dist)
      }


      

        a = Math.sin(lat_diff / 2) * Math.sin(lat_diff / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(latitude * Math.PI / 180) *
            Math.sin(long_diff / 2) * Math.sin(long_diff / 2)
        c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

        dist = R * c // metres
        console.log('dist ', dist)

        //declaring emergency
        if ((studyStage == '3') || (studyStage == '4')) {
            if (dist <= 500 || (Math.abs(time_diff - 161) <= 2.3) || (EmptyTank==1) || (EngineFailure==1))  {
                if((satisfied==false)|| (EngineFailure==1) || (EmptyTank==1)){
                    console.log("EMERGENCY LOCATION REACHED")
                    satisfied=true
                    //destinationIndex=-1
                    //await fetch("/var?destination-index=" + destinationIndex)
                    await fetch("/var?satisfied=" + satisfied)
                    console.log('emergency occured')
                    if (studyStage == '3') {
                        EmptyTank=1
                        await fetch("/var?empt-tank=" + EmptyTank)
                    }
                    if (studyStage == '4') {
                        // Engine failure scenario
                        EngineFailure = 1;
                        await fetch("/var?engine-failure=" + EngineFailure)
                    }
                }
            }
        }


        //Pressure Warning
        if (studyStage == '4') {
          if (warning_dist <= 500 || (Math.abs(time_diff - 100) <= 1.3) || (PressureWarning==1))  {
              if((warning_satisfied==false)|| (PressureWarning==1)){
                  console.log("WARNING LOCATION REACHED")
                  warning_satisfied=true
                  await fetch("/var?warning-satisfied=" + warning_satisfied)
                  console.log('showing pressure warning')
                  PressureWarning=0
                  await fetch("/var?pressure-warning=" + PressureWarning)
                  }
              }
          }

        // nominal condition landing
        if (dist <= 250 || timeToDestination<= 0.08) {
            console.log('dist', dist)
            console.log('time', timeToDestination)
            if (((studyStage == '1') || (studyStage == '2'))) {
                window.location.href = "/hai-interface/checklist?inflight=" + 1 + "&target-index=" + targetIndex
            }
        }

        // Landing for study stage 3 and 4
        if (studyStage == '3' || studyStage == '4') {
            //making FTY Heliport the nearest in emergency
            helipads[20].nearest=true

            //destination for higher workload scenario-southside hospital
            TargetIndex=11

            //checking when the destination index has changed
            if (TargetIndex != 16) {
                TargetIndex = destinationIndex
                console.log(TargetIndex)
                target_lat = helipads[TargetIndex].latitude
                target_long = helipads[TargetIndex].longitude
                lat_diff = (target_lat - latitude) * Math.PI / 180  //radians
                long_diff = (target_long - longitude) * Math.PI / 180 //radians
                lat1 = target_lat

                //calculating the distance between the current aircraft position and the set target
                a = Math.sin(lat_diff / 2) * Math.sin(lat_diff / 2) +
                    Math.cos(lat1) * Math.cos(latitude) *
                    Math.sin(long_diff / 2) * Math.sin(long_diff / 2)
                c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
                dist_to_target = R * c // metres
            
               
            }
            console.log(satisfied)
            //displaying the landing checklist when approaching the set destination
            if ((dist_to_target <= 300) || (timeToDestination<= 0.08)){
                console.log('emergency occured and approaching destination')
                window.location.href = "/hai-interface/checklist?inflight=" + 1 + "&target-index=" + targetIndex
            }

        }

        // to show Fuel tank empty alert 
        if (EmptyTank == 1) {
          log({"page": "emergency", "action": "show Fuel Tank Empty Alert , hide map"})
          hideMap()
          audio.play()
          audio.volume=0.05
          activateFuelAlert()
      }

        // to show pressure miscalibration warning 
        if (PressureWarning == 1) {
            log({"page": "emergency", "action": "show Pressure Miscalibrated Warning, hide map"})
            hideMap()
            audio.play()
            audio.volume=0.05
            activateWarningAlert()
        }

        // For Engine failure emergency
        if (EngineFailure == 1) {
          log({"page": "emergency", "action": "show Engine Failure Alert, hide map"})
          hideMap()
          audio.play()
          audio.volume=0.05
          activateEngineAlert()
        }

        console.log(satisfied, destinationIndex)
        if(satisfied ==true){
            console.log("satisfied")
        }
        console.log(destChanged)
        
        if(satisfied ==true && destChanged==false && studyStage == '4'){
            console.log('Engine Failure alert again')
            // Engine failure alert showed but destination hasn't been changed yet so emergency notification will come up again 
            setTimeout(async ()  => {
                emergencyState=1
                //Engine failure emergency
                EngineFailure = 1;
                await fetch("/var?engine-failure=" + EngineFailure)
              }, 5000);
        }

    }, 5000)

    // emergency acknowledge, onclick to move to inflight again
    document.getElementById("emergency-acknowledge-button").onclick = async () => {
        log({"page": "emergency", "action": "user acknowledged emergency"})
        document.getElementById('emergency').style.display = "none"
        //document.body.style.background = "peachpuff"
        document.getElementById("main").style.display = "flex"
        document.getElementById("topbar").style.display = "flex"
        emergencyState = 0;
        audio.pause()
        //updating the server
        await fetch("/var?airspace-state=" + emergencyState)
    }
}


function TimeToDestination() {
    setInterval(async () => {

        //Calculating the distance between the current aircraft position and destination
        const R = 6371e3 // metres

        TargetIndex = destinationIndex
        target_lat = helipads[TargetIndex].latitude
        target_long = helipads[TargetIndex].longitude
        lat_diff = (target_lat - latitude) * Math.PI / 180  //radians
        long_diff = (target_long - longitude) * Math.PI / 180 //radians
        lat1 = target_lat

        //calculating the distance between the current aircraft position and the set target
        a = Math.sin(lat_diff / 2) * Math.sin(lat_diff / 2) +
            Math.cos(lat1) * Math.cos(latitude) *
            Math.sin(long_diff / 2) * Math.sin(long_diff / 2)
        c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
        dist_to_target = R * c // metres
        timeToDestination=(dist_to_target/2784).toFixed(2);
        await fetch("/var?time-to-destination=" + timeToDestination)


}, 5000)
}



// Pressure Warning
// Function to activate the pressure warning alert
function activateWarningAlert() {
  console.log("PressureWarning activated")
  log({"page": "Inflight", "action": "Pressure Warning alert activated"}); 
    document.body.classList.add('dull-background');
    const pWoverlay = document.getElementById('pressureWarningalertOverlay');
    pWoverlay.style.visibility = 'visible';
    pWoverlay.style.opacity = '1';
  }

  // Function to show more information
  function showInfo() {
    log({"page": "Inflight", "action": "Pressure Warning- show info button pressed"}); 
    const pWalertBox = document.getElementById('pressureWarningalertBox');
    pWalertBox.classList.add('expanded');
    document.getElementById('pressureWarningalertExplanation').style.display = 'block';
    document.getElementById('pressureWarningmoreInfoButton').style.display = 'none';
    //document.getElementById('pressureWarningcloseButton').style.display = 'block';
    // Stop the flashing animation
    document.getElementById('warningText').style.animation = 'none';
  }

  // Function to submit pressure value
  function submitPressureValue() {
    log({"page": "Inflight", "action": "Pressure Warning submit button pressed"}); 
    const pressureValue = document.getElementById('pressureValue').value;
    const resultMessage = document.getElementById('resultMessage');
    const finalMessage = document.getElementById('finalMessage');
    const okButton = document.getElementById('okButton');
    const correctValue = "75"; // The correct pressure value

    if (pressureValue === correctValue) {
      document.getElementById('pressureWarningalertExplanation').style.display = 'none';
      resultMessage.style.display = 'none';
      finalMessage.innerHTML = "The primary sensor was miscalibrated but everything appears to be fine. You are enroute as planned.";
      finalMessage.style.color = "green";
      finalMessage.style.display = 'block';
      okButton.style.display = 'block';
      const pWalertBox = document.getElementById('pressureWarningalertBox');
      pWalertBox.classList.remove('expanded');
    } 
    else {
      resultMessage.innerHTML = "Wrong value, please submit the pressure value again.";
      resultMessage.style.color = "red";
      resultMessage.style.display = 'block';
      document.getElementById('pressureValue').value = '';
    }
  }

  // Function to close the warning alert
  async function closePressureAlert()  {
    console.log('pressed')
    log({"page": "Inflight", "action": "Pressure Warning alert close button pressed"}); 
    const pWoverlay = document.getElementById('pressureWarningalertOverlay');
    pWoverlay.style.opacity = '0';
    pWoverlay.addEventListener('transitionend', () => {
      pWoverlay.style.visibility = 'hidden';
      document.body.classList.remove('dull-background');
    }, { once: true });
    PressureWarning=0
    audio.pause()
    //updating the server
    await fetch("/var?pressure-warning=" + PressureWarning)
  }


//Engine Failure
// Function to activate the engine failure emergency alert
function activateEngineAlert() {
  log({"page": "Inflight", "action": "Engine failure emergency- show more info button pressed"}); 
  console.log(EngineFailure)
  const overlay = document.getElementById('alertOverlay');
  document.body.classList.add('dull-background');
  overlay.style.visibility = 'visible';
  overlay.style.opacity = '1';
  //document.getElementById('sirenSound').play();
}

  // Function to show more information about engine failure and stop the siren
  function showMoreInfo() {
    log({"page": "Inflight", "action": "Engine failure emergency- show more info button pressed"}); 
    const alertBox = document.getElementById('alertBox');
    alertBox.classList.add('expanded');
    document.getElementById('alertExplanation').style.display = 'block';
    document.getElementById('moreInfoButton').style.display = 'none';
    document.getElementById('CDButton').style.display = 'block';
    // document.getElementById('sirenSound').pause();
    // document.getElementById('sirenSound').currentTime = 0;
    document.getElementById("CDButton").onclick = async () => { closeAlert(); 
    log({"page": "Inflight", "action": "change destination button pressed"}); 
    EngineFailure=0
    console.log(EngineFailure); 
    setTimeout(() => {
    window.location.href = '/hai-interface/change-destination?inflight=' + 1;}, 1000); // delay in milliseconds for console
    //updating the server
    await fetch("/var?engine-failure=" + EngineFailure)
    }
  
  }

  // Function to close engine failure alert
  function closeAlert() {
    console.log("closing")
    const overlay = document.getElementById('alertOverlay');
    overlay.style.opacity = '0';
    overlay.addEventListener('transitionend', () => {
      overlay.style.visibility = 'hidden';
      document.body.classList.remove('dull-background');
      EngineFailure=0
    }, { once: true});  
  }


//Empty Fuel Tank 
// Function to activate the empty fuel tank emergency alert
function activateFuelAlert() {
  console.log(EmptyTank)
  log({"page": "Inflight", "action": "Fuel tank emergency alert"}); 
  const fAoverlay = document.getElementById('fuelAlertOverlay');
  document.body.classList.add('dull-background');
  fAoverlay.style.visibility = 'visible';
  fAoverlay.style.opacity = '1';
  //document.getElementById('sirenSound').play();
}

  // Function to show more information regarding fuel tank and stop the siren
  function showFuelInfo() {
    log({"page": "Inflight", "action": "Fuel tank emergency- show more info button pressed"}); 
    const fAalertBox = document.getElementById('fuelAlertBox');
    fAalertBox.classList.add('expanded');
    document.getElementById('fuelAlertExplanation').style.display = 'block';
    document.getElementById('fuelInfoButton').style.display = 'none';
    document.getElementById('okButtonFuel').style.display = 'block';
    //document.getElementById('sirenSound').pause();
    //document.getElementById('sirenSound').currentTime = 0;
    document.getElementById("okButtonFuel").onclick = async () => { closeFuelAlert(); 
      log({"page": "Inflight", "action": "Ok button on Fuel tank emergency pressed"}); 
      EmptyTank=0
      console.log(EmptyTank); 
      //updating the server
      await fetch("/var?empty-tank=" + EmptyTank)
    }
 }

  // Function to close the emergency alert
  function closeFuelAlert() {
    console.log("closing")
    const fAoverlay = document.getElementById('fuelAlertOverlay');
    fAoverlay.style.opacity = '0';
    fAoverlay.addEventListener('transitionend', () => {
      fAoverlay.style.visibility = 'hidden';
      document.body.classList.remove('dull-background');
      EmptyTank=0
    }, { once: true});  
  }





 // Activate the emergency alert for demo purposes

 //EngineFailure=1
 //window.onload = activateEngineAlert;

 //window.onload = activateWarningAlert;
 //EmptyTank=1
 //window.onload =activateFuelAlert;
