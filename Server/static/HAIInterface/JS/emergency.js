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

        time_diff = (new Date()).getTime() / 1000 - flightStartTime  //flightStartTime starts when countdown begins (countdown page) 
        console.log(time_diff)

       /*  "21": {
          # Engine Failure and Fuel tank emergency trigger location
          "latitude": "33.772017",
          "longitude": "-84.544871",
      }, 
     */
        warning_lat = 33.691383       // new warning location : 33.691383, -84.612864
        warning_long = -84.612864 
        emergency_lat = 33.766148     // new emergency location: 33.741798, -84.562125
        emergency_long = -84.527984
        nominal_lat =33.7919194 //  Emory University Hospital: ,
        nominal_long = -84.3225861
        // Emergency Location for engine failure 33.766148, -84.527984
        // Pressure Warning location before engine failure 33.741060, -84.566249
        //https://www.google.com/maps/dir/Miller+Farm+Airport-25GA,+Leann+Dr,+Douglasville,+GA/33.741060,+-84.566249/33.766148,+-84.527984/Fulton+County+Airport+-+Brown+Field+(FTY),+Aviation+Circle+Northwest,+Atlanta,+GA/Old+Fourth+Ward,+Atlanta,+GA/@33.718646,-84.6019543,30007m/data=!3m3!1e3!4b1!5s0x88f5038ebeea134f:0x78787416707158e5!4m28!4m27!1m5!1m1!1s0x88f4df6cae05f855:0xfce85469926264b5!2m2!1d-84.6629511!2d33.6598811!1m3!2m2!1d-84.566249!2d33.74106!1m3!2m2!1d-84.527984!2d33.766148!1m5!1m1!1s0x88f51bfd379c09f7:0xdebb7dfce7c9c439!2m2!1d-84.5216729!2d33.7771801!1m5!1m1!1s0x88f50408dbf17f1f:0x60ccf34413430e69!2m2!1d-84.3719735!2d33.7639588!3e0?entry=ttu



        //Calculating the distance between the current aircraft position and destination
        const R = 6371e3 // metres

        lat_diff = (nominal_lat - latitude) * Math.PI / 180  //radians
        long_diff = (nominal_long - longitude) * Math.PI / 180 //radians
        lat1 = nominal_lat

       //emergency location distance wrt to the current position of aircraft
        lat_diff = (emergency_lat - latitude) * Math.PI / 180  //radians
        long_diff = (emergency_long - longitude) * Math.PI / 180 //radians
        lat1 = emergency_lat

        //Time to destination
        dest_lat = helipads[destinationIndex].latitude
        dest_long = helipads[destinationIndex].longitude
        lat_diff = (dest_lat - latitude) * Math.PI / 180  //radians
        long_diff = (dest_long - longitude) * Math.PI / 180 //radians
        lat1 = dest_lat

        //calculating the distance between the current aircraft position and the destination
        a = Math.sin(lat_diff / 2) * Math.sin(lat_diff / 2) +
            Math.cos(lat1) * Math.cos(latitude) *
            Math.sin(long_diff / 2) * Math.sin(long_diff / 2)
        c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
        dist_to_dest = R * c // metres
        timeToDestination=(dist_to_dest/2784).toFixed(2);
        await fetch("/var?time-to-destination=" + timeToDestination)
  

        if (studyStage == '4') {
          warning_lat_diff = (warning_lat - latitude) * Math.PI / 180  //radians
          warning_long_diff = (warning_long - longitude) * Math.PI / 180 //radians
          warning_lat1 = warning_lat
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
        if ((studyStage == '2') || (studyStage == '3') || (studyStage == '4')) {
            if (dist <= 500 || (Math.abs(time_diff - 300) <= 2.3) || (EmptyTank==1) || (EngineFailure==1))  {
                console.log('Entered here')
                if((satisfied==false)|| (EngineFailure==1) || (EmptyTank==1)){
                    console.log("EMERGENCY LOCATION REACHED")
                    satisfied=true
                    await fetch("/var?satisfied=" + satisfied)
                    console.log('emergency occured')

                    if (studyStage == '2') {
                      vitalsState = 1
                      await fetch("/var?vitals-state=" + vitalsState)
                  }
                    if (studyStage == '3') {
                        EmptyTank=1
                        await fetch("/var?empty-tank=" + EmptyTank)
                    }
                    if (studyStage == '4') {
                        // Engine failure scenario and vitals
                        EngineFailure = 1;
                        await fetch("/var?engine-failure=" + EngineFailure)
                        vitalsState = 1
                        await fetch("/var?vitals-state=" + vitalsState)
                    }
                }
            }
        }


        //Pressure Warning
        if (studyStage == '4') {
          console.log("checking")
          if (warning_dist <= 350 || (Math.abs(time_diff - 180) <= 2.7) || (PressureWarning==1))  {
              console.log("here")
              if((warning_satisfied==false)|| (PressureWarning==1)){
                  console.log("WARNING LOCATION REACHED")
                  warning_satisfied=true
                  PressureWarning=1
                  await fetch("/var?warning-satisfied=" + warning_satisfied)
                  console.log('showing pressure warning')
                  await fetch("/var?pressure-warning=" + PressureWarning)
                  }
              }
          }

        // nominal condition landing
        if (dist_to_dest <= 300 || timeToDestination<= 0.25) {
            console.log('dist', dist)
            console.log('time', timeToDestination)
            if (((studyStage == '1') || (studyStage == '2') || (studyStage == '3'))) {
                window.location.href = "/hai-interface/checklist?inflight=" + 1 + "&target-index=" + targetIndex
            }
        }

        // Landing for study stage 4
        if (studyStage == '4') {
            //making FTY Heliport the nearest in emergency
            helipads[20].nearest=true

            //destination for higher workload scenario-Old Forth
            //destinationIndex=19

            //checking when the destination index has changed
            if (TargetIndex != 3) {
              log({"page": "emergency", "action": "trying to change destination to"+ TargetIndex })
                TargetIndex = 19 //destination for higher workload scenario-Old Forth
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
            if ((dist_to_target <= 300) || (timeToDestination<= 0.25)){
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
            console.log('Engine Failure  dest not set')
            log({"page": "emergency", "action": "Engine Failure- destination not changed"})
            // Engine failure alert showed but destination hasn't been changed yet then flying to Old forth
            setTimeout(async ()  => {
              destChanged==True 
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
        document.getElementById('sirenSound').pause();
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
    const pressureValue = document.getElementById('pressureValue').value;
    const resultMessage = document.getElementById('resultMessage');
    const finalMessage = document.getElementById('finalMessage');
    const okButton = document.getElementById('okButton');
    log({"page": "Inflight", "action": "Pressure Warning- submit button pressed with pressure value as:"+ pressureValue}); 
    const correctValue = "75"; // The correct pressure value

    if (pressureValue === correctValue) {
      document.getElementById('pressureWarningalertExplanation').style.display = 'none';
      resultMessage.style.display = 'none';
      finalMessage.innerHTML = "The primary sensor was miscalibrated but everything appears to be fine.<br><br> We are enroute as planned.<br> <br>Please inform ground";
      // finalMessage.style.color = "green";
      finalMessage.style.display = 'block';
      okButton.style.display = 'block';
      const pWalertBox = document.getElementById('pressureWarningalertBox');
      pWalertBox.classList.remove('expanded');
      log({"page": "Inflight", "action": "Pressure Warning- alert explaination"}); 
    } 
    else {
      resultMessage.innerHTML = "Wrong value, check and submit the pressure value again.";
      resultMessage.style.color = "yellow";
      resultMessage.style.display = 'block';
      log({"page": "Inflight", "action": "Pressure Warning- wrong pressure value entered"}); 
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
    document.getElementById('sirenSound').pause();
    //updating the server
    await fetch("/var?pressure-warning=" + PressureWarning)
  }


//Engine Failure
// Function to activate the engine failure emergency alert
function activateEngineAlert() {
  log({"page": "Inflight", "action": "Engine failure emergency- emergnecy propmt displayed"}); 
  console.log(EngineFailure)
  const overlay = document.getElementById('alertOverlay');
  document.body.classList.add('dull-background');
  overlay.style.visibility = 'visible';
  overlay.style.opacity = '1';
  document.getElementById('sirenSound').play();
}

  // Function to show more information about engine failure and stop the siren
  function showMoreInfo() {
    log({"page": "Inflight", "action": "Engine failure emergency- show more info button pressed"}); 
    const alertBox = document.getElementById('alertBox');
    alertBox.classList.add('expanded');
    document.getElementById('alertExplanation').style.display = 'block';
    document.getElementById('moreInfoButton').style.display = 'none';
    document.getElementById('CDButton').style.display = 'block';
    document.getElementById('sirenSound').pause();
    document.getElementById('sirenSound').currentTime = 0;
    document.getElementById("CDButton").onclick = async () => { closeAlert(); 
    log({"page": "Inflight", "action": "change destination button pressed"}); 
    EngineFailure=0
    console.log(EngineFailure); 
    //updating the server
    await fetch("/var?engine-failure=" + EngineFailure)
    window.location.href = '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1
    }
  
  }

  // Function to close engine failure alert
  function closeAlert() {
    console.log("closing")
    document.getElementById('sirenSound').pause();
    log({"page": "Inflight", "action": "Engine failure emergency- close button pressed"}); 
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
  document.getElementById('sirenSound').play();
  log({"page": "Inflight", "action": "Fuel tank emergency alert-displayed"}); 
  const fAoverlay = document.getElementById('fuelAlertOverlay');
  document.body.classList.add('dull-background');
  fAoverlay.style.visibility = 'visible';
  fAoverlay.style.opacity = '1';
  document.getElementById('sirenSound').play();
}

  // Function to show more information regarding fuel tank and stop the siren
  function showFuelInfo() {
    log({"page": "Inflight", "action": "Fuel tank emergency- show more info button pressed"}); 
    document.getElementById('sirenSound').pause();
    const fAalertBox = document.getElementById('fuelAlertBox');
    fAalertBox.classList.add('expanded');
    document.getElementById('fuelAlertExplanation').style.display = 'block';
    document.getElementById('fuelInfoButton').style.display = 'none';
    document.getElementById('okButtonFuel').style.display = 'block';
    document.getElementById('sirenSound').pause();
    document.getElementById('sirenSound').currentTime = 0;
    document.getElementById("okButtonFuel").onclick = async () => { closeFuelAlert(); 
      log({"page": "Inflight", "action": "Continue button on Fuel tank emergency pressed"}); 
    }

    document.getElementById("elButtonFuel").onclick = async () => { closeFuelAlert(); 
      log({"page": "Inflight", "action": "Change destination button on Fuel tank emergency pressed"}); 
      window.location.href = '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1 ;
    }

  
    document.getElementById("groundButtonFuel").onclick = async () => { closeFuelAlert(); 
      log({"page": "Inflight", "action": "Ground button on Fuel tank emergency pressed"}); 
        console.log('opening radio panel')
        document.querySelector('.radiopanel').classList.toggle('open');
    }
      EmptyTank=0
      console.log(EmptyTank); 
      //updating the server
      fetch("/var?empty-tank=" + EmptyTank)
    
 }

  // Function to close the emergency alert
  function closeFuelAlert() {
    console.log("closing")
    log({"page": "Inflight", "action": "Empty Tank emergency- close button "}); 
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
