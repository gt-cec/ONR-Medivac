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
      if (!["/hai-interface/location", "/hai-interface/inflight", "/hai-interface/change-destination", "/hai-interface/help", "/hai-interface/change-altitude" ].includes(window.location.pathname)) {
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
      console.log(destinationIndex)
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
  

        if (studyStage == '1' || studyStage == '4') {
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


        //emergency declaration for scenario 1 (training)
        /* if (studyStage == '1') {
        // Altitude alert 
          if (warning_dist <= 350 || (Math.abs(time_diff - 180) <= 2.7)){
              console.log('Entered here')
              if(altitude_satisfied==false) {
                  console.log("ALTITUDE ALERT LOCATION REACHED")
                  altitude_satisfied=true
                  await fetch("/var?altitude-satisfied=" + altitude_satisfied)
                  console.log('altitude alert occured')
                  altitudeAlert = 1
                  await fetch("/var?altitude-alert=" + altitudeAlert)
              }
           }
          // weather emergency
          if (dist <= 500 || (Math.abs(time_diff - 300) <= 2.3))   {
            console.log('Entered here')
            if(weather_satisfied==false) {
                  console.log("EMERGENCY LOCATION REACHED")
                  weather_satisfied=true
                  await fetch("/var?weather-satisfied=" + weather_satisfied)
                  console.log('weather emergency occured')
                  weatherEmergency = 1
                  await fetch("/var?weather-emergency=" +  weatherEmergency)
              }
           }
        } */

        //declaring emergency
        if ((studyStage == '1')||(studyStage == '2') || (studyStage == '3') || (studyStage == '4')) {
            //if (dist <= 500 || (Math.abs(time_diff - 300) <= 2.3) || (EmptyTank==1) || (EngineFailure==1)|| (vitalsState==1) ){
              if (dist <= 500 || (Math.abs(time_diff - 300) <= 2.3)){
                console.log('Entered here')
                //if((satisfied==false) || ((EngineFailure==1) || (EmptyTank==1) || (vitalsState==1))){
                  if(satisfied==false) {
                    console.log("EMERGENCY LOCATION REACHED")
                    satisfied=true
                    await fetch("/var?satisfied=" + satisfied)
                    console.log('emergency occured')

                    if (studyStage == '2') {
                      vitalsState = 1
                      await fetch("/var?vitals-state=" + vitalsState)
                    }
                    else if (studyStage == '3') {
                        EmptyTank=1
                        await fetch("/var?empty-tank=" + EmptyTank)
                     }
                    else if (studyStage == '4') {
                        // Engine failure scenario and vitals
                        vitalsState = 1
                        await fetch("/var?vitals-state=" + vitalsState)
                        EngineFailure = 1;
                        await fetch("/var?engine-failure=" + EngineFailure)

                       /*  const emergencyTimeout=setTimeout(async() => {
                         
                          clearTimeout(emergencyTimeout)
                          console.log("showing engine failure")
                        }, 5000);  //calling the engine failure 5 seconds after vitals */
                       
                    }
                    else if (studyStage == '1') {
                      weatherEmergency = 1
                      await fetch("/var?weather-emergency=" + weatherEmergency)
                    }
                }
            }
        }


        //Pressure Warning
        if (studyStage == '1'||studyStage == '4') {
          console.log("checking")
          //if (warning_dist <= 350 || (Math.abs(time_diff - 180) <= 2.7) || (PressureWarning==1))  {
            if (warning_dist <= 350 || (Math.abs(time_diff - 180) <= 2.8))  {
              console.log("here")
              //if((warning_satisfied==false) || (PressureWarning==1)){
                if(studyStage == '4' && warning_satisfied==false) {
                  console.log("WARNING LOCATION REACHED")
                  warning_satisfied=true
                  PressureWarning=1
                  await fetch("/var?pressure-warning=" + PressureWarning)
                  console.log(PressureWarning)
                  console.log(typeof(PressureWarning))
                  await fetch("/var?pressure-warning=1")
                  await fetch("/var?warning-satisfied=" + warning_satisfied)
                  console.log('showing pressure warning')
                  }

                if(studyStage == '1' && altitude_satisfied==false) {
                  console.log("WARNING LOCATION REACHED")
                  altitude_satisfied=true
                  altitudeAlert=1
                  await fetch("/var?altitude-alert=1" + altitudeAlert)
                  await fetch("/var?altitude-satisfied=" + altitude_satisfied)
                  console.log('showing altiude warning')
                  
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
        if (studyStage == '4'||studyStage == '3'|| studyStage == '1' ) {
            //making FTY Heliport the nearest in emergency
            helipads[20].nearest=true

            //destination for higher workload scenario-Old Forth
            //destinationIndex=19

            //checking when the destination index has changed
            if (TargetIndex != 3) {
             logAction({"page": "emergency", "action": "trying to change destination to"+ TargetIndex })
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
                if(studyStage == '4'){
                  targetIndex=19 //goes to Old forth for scenario 4 b default
                }
                window.location.href = "/hai-interface/checklist?inflight=" + 1 + "&target-index=" + targetIndex
            }

        }

        // to show Fuel tank empty alert 
        //if (EmptyTank == 1 && satisfied==true) {
        if (EmptyTank == 1) {
         logAction({"page": "emergency", "action": "show Fuel Tank Empty Alert , hide map"})
          hideMap()
         /*  audio.play()
          audio.volume=0.05 */
          activateFuelAlert()
       }

        // to show pressure miscalibration warning 
       // if (PressureWarning == 1 && warning_satisfied==true) {
        if (PressureWarning == 1 ) {
           logAction({"page": "emergency", "action": "show Pressure Miscalibrated Warning, hide map"})
            hideMap()
            console.log('Activating warning alert')
            /* audio.play()
            audio.volume=0.05 */
            activateWarningAlert()
         } 

        // For Engine failure emergency
        //if (EngineFailure == 1 && satisfied==true) {
        if (EngineFailure == 1 ) {
         logAction({"page": "emergency", "action": "show Engine Failure Alert, hide map"})
          hideMap()
         /*    audio.play()
          audio.volume=0.05 */
          activateEngineAlert()
        }

        if (altitudeAlert == 1 ) {
          console.log('altitude alert')
         logAction({"page": "emergency", "action": "show Altitude Miscalibrated Warning, hide map"})
          hideMap()
          activateAltitudeAlert()
        }

      // For weather emergency
      if (weatherEmergency == 1 ) {
        console.log('Weather emergency')
       logAction({"page": "emergency", "action": "show Weather Emergency Alert, hide map"})
        hideMap()
        activateWeatherAlert()
       }
        console.log(satisfied, destinationIndex)
        if(satisfied ==true){
            console.log("satisfied")
        }
        console.log(destChanged)
        
      /*   if(satisfied ==true && destChanged==false && studyStage == '4'){
            console.log('Engine Failure  dest not set')
           logAction({"page": "emergency", "action": "Engine Failure- destination not changed"})
            // Engine failure alert showed but destination hasn't been changed yet then flying to Old forth
            setTimeout(async ()  => {
              destChanged==True 
              }, 5000);
        } */

    }, 5000)

    // emergency acknowledge, onclick to move to inflight again
    document.getElementById("emergency-acknowledge-button").onclick = async () => {
       logAction({"page": "emergency", "action": "user acknowledged emergency"})
        document.getElementById('sirenSound').pause();
        document.getElementById('emergency').style.display = "none"
        //document.body.style.background = "peachpuff"
        document.getElementById("main").style.display = "flex"
        document.getElementById("topbar").style.display = "flex"
        emergencyState = 0;
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
  document.getElementById('warningSound').play();

  setTimeout(() => {
    document.getElementById('warningSound').pause();
    document.getElementById('warningSound').currentTime = 0; // Reset to the beginning
  }, 2000); //  2 seconds

  
 logAction({"page": "Inflight", "action": "Pressure Warning alert activated"}); 
  document.body.classList.add('dull-background');
  const pWoverlay = document.getElementById('pressureWarningalertOverlay');
  pWoverlay.style.visibility = 'visible';
  pWoverlay.style.opacity = '1';
  }

  // Function to show more information
  function showInfo() {
   logAction({"page": "Inflight", "action": "Pressure Warning- show info button pressed"}); 
    document.getElementById('warningSound').pause();
    document.getElementById('warningSound').currenTime=0;
    const pWalertBox = document.getElementById('pressureWarningalertBox');
    pWalertBox.classList.add('expanded');
    document.getElementById('pressureWarningalertExplanation').style.display = 'block';
    document.getElementById('pressureWarningmoreInfoButton').style.display = 'none';
    //document.getElementById('pressureWarningcloseButton').style.display = 'block';
    // Stop the flashing animation
    document.getElementById('warningText').style.animation = 'none';
   /*  PressureWarning=0  
    //updating the server
    fetch("/var?pressure-warning=" + PressureWarning) */
  }

  // Function to submit pressure value
  async function submitPressureValue() {
    document.getElementById('warningSound').pause();
    document.getElementById('warningSound').currenTime=0;
    const pressureValue = document.getElementById('pressureValue').value;
    const resultMessage = document.getElementById('resultMessage');
    const finalMessage = document.getElementById('finalMessage');
    const okButton = document.getElementById('ok-Button');
   logAction({"page": "Inflight", "action": "Pressure Warning- submit button pressed with pressure value as:"+ pressureValue}); 
    const correctValue = "75"; // The correct pressure value

    if (pressureValue === correctValue) {
      document.getElementById('pressureWarningalertExplanation').style.display = 'none';
      resultMessage.style.display = 'none';
      finalMessage.innerHTML = "The primary sensor was miscalibrated but everything appears to be fine.<br><br> We are enroute as planned.<br> <br>Please inform Control";
      // finalMessage.style.color = "green";
      finalMessage.style.display = 'block';
      okButton.style.display = 'block';
      const pWalertBox = document.getElementById('pressureWarningalertBox');
      pWalertBox.classList.remove('expanded');
     logAction({"page": "Inflight", "action": "Pressure Warning- alert explaination"}); 
      PressureWarning=0  
      //updating the server
      await fetch("/var?pressure-warning=" + PressureWarning)
    } 
    else {
      resultMessage.innerHTML = "Wrong value, check and submit the pressure value again.";
      resultMessage.style.color = "yellow";
      resultMessage.style.display = 'block';
     logAction({"page": "Inflight", "action": "Pressure Warning- wrong pressure value entered"}); 
    }
  }

  // Function to close the warning alert
  async function closePressureAlert()  {
    console.log('pressed')
   logAction({"page": "Inflight", "action": "Pressure Warning alert close button pressed"}); 
    const pWoverlay = document.getElementById('pressureWarningalertOverlay');
    pWoverlay.style.opacity = '0';
    pWoverlay.addEventListener('transitionend', () => {
      pWoverlay.style.visibility = 'hidden';
      document.body.classList.remove('dull-background');
    }, { once: true });
   /*  PressureWarning=0  
    //updating the server
    await fetch("/var?pressure-warning=" + PressureWarning) */
  }


//Engine Failure
// Function to activate the engine failure emergency alert
function activateEngineAlert() {
 logAction({"page": "Inflight", "action": "Engine failure emergency- emergnecy propmt displayed"}); 
  console.log(EngineFailure)
  document.getElementById('sirenSound').play();

  setTimeout(() => {
    document.getElementById('sirenSound').pause();
    document.getElementById('sirenSound').currentTime = 0; // Reset to the beginning
  }, 2000); //  2 seconds

  const overlay = document.getElementById('alertOverlay');
  document.body.classList.add('dull-background');
  overlay.style.visibility = 'visible';
  overlay.style.opacity = '1';
  //updating the server
  fetch("/var?engine-failure=" + EngineFailure)
}

  // Function to show more information about engine failure and stop the siren
  function showMoreInfo() {
   logAction({"page": "Inflight", "action": "Engine failure emergency- show more info button pressed"}); 
    document.getElementById('sirenSound').pause();
    document.getElementById('sirenSound').currentTime = 0;
    const alertBox = document.getElementById('alertBox');
    alertBox.classList.add('expanded');
    EngineFailure=0
    console.log(EngineFailure); 
    //updating the server
    fetch("/var?engine-failure=" + EngineFailure)
    document.getElementById('alertExplanation').style.display = 'block';
    document.getElementById('moreInfoButton').style.display = 'none';
    document.getElementById('CDButton').style.display = 'block';
    document.getElementById("CDButton").onclick = () => { closeAlert(); 
   logAction({"page": "Inflight", "action": "change destination button pressed"}); 
    window.location.href = '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1
    }
  
  }

  // Function to close engine failure alert
  async function closeAlert() {
    console.log("closing")
   logAction({"page": "Inflight", "action": "Engine failure emergency- close button pressed"});
    document.getElementById('sirenSound').pause(); 
    document.getElementById('sirenSound').currentTime = 0;
    const overlay = document.getElementById('alertOverlay');
    overlay.style.opacity = '0';
    overlay.addEventListener('transitionend', () => {
      overlay.style.visibility = 'hidden';
      document.body.classList.remove('dull-background');
      EngineFailure=0
    },{ once: true });
    EngineFailure=0
    console.log(EngineFailure); 
    //updating the server
    await fetch("/var?engine-failure=" + EngineFailure)
  }


//Empty Fuel Tank 
// Function to activate the empty fuel tank emergency alert
function activateFuelAlert() {
  console.log("Fuel alert activated")
  console.log(EmptyTank)
  document.getElementById('emptytankSound').play();
 logAction({"page": "Inflight", "action": "Fuel tank emergency alert-displayed"}); 
  const fAoverlay = document.getElementById('fuelAlertOverlay');
  document.body.classList.add('dull-background');
  fAoverlay.style.visibility = 'visible';
  fAoverlay.style.opacity = '1';
  document.getElementById('okFuel-Button').style.display = 'block';
  document.getElementById("okFuel-Button").onclick = () => {
  closeFuelAlert();
 logAction({ "page": "Inflight", "action": "Continue button on Fuel tank emergency pressed" });
  document.getElementById('emptytankSound').pause();
}
}

  // Function to show more information regarding fuel tank and stop the siren
  function showFuelInfo() {
   logAction({"page": "Inflight", "action": "Fuel tank emergency- show more info button pressed"}); 
    document.getElementById('emptytankSound').pause();
    document.getElementById('emptytankSound').currentTime = 0;
    console.log("Fuel alert expanded")
    const fAalertBox = document.getElementById('fuelAlertBox');
    fAalertBox.classList.add('expanded');
    EmptyTank=0
    console.log(EmptyTank); 
    //updating the server
    fetch("/var?empty-tank=" + EmptyTank)
    document.getElementById('fuelAlertExplanation').style.display = 'block';
    document.getElementById('fuelInfoButton').style.display = 'none';
    document.getElementById('okFuel-Button').style.display = 'block';
    document.getElementById("okFuel-Button").onclick =  () => { closeFuelAlert(); 
   logAction({"page": "Inflight", "action": "Continue button on Fuel tank emergency pressed"}); 
    document.getElementById('emptytankSound').pause();
    }

    document.getElementById("elFuel-Button").onclick =  () => { closeFuelAlert(); 
     logAction({"page": "Inflight", "action": "Change destination button on Fuel tank emergency pressed"}); 
      document.getElementById('emptytankSound').pause();
      window.location.href = '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1 ;
    }

  
    document.getElementById("groundButtonFuel").onclick =  () => { closeFuelAlert(); 
     logAction({"page": "Inflight", "action": "Control button on Fuel tank emergency pressed"}); 
        console.log('opening radio panel')
        document.getElementById('emptytankSound').pause();
        document.querySelector('.radiopanel').classList.toggle('open');
    }

 }

  // Function to close the emergency alert
  async function closeFuelAlert() {
    console.log("closing")
   logAction({"page": "Inflight", "action": "Empty Tank emergency- close button "}); 
    document.getElementById('emptytankSound').pause();
    document.getElementById('emptytankSound').currentTime = 0;
    const fAoverlay = document.getElementById('fuelAlertOverlay');
    fAoverlay.style.opacity = '0';
    fAoverlay.addEventListener('transitionend', () => {
      fAoverlay.style.visibility = 'hidden';
      document.body.classList.remove('dull-background');
    }, { once: true });
    EmptyTank=0
    console.log(EmptyTank); 
    //updating the server
    await fetch("/var?empty-tank=" + EmptyTank)
  }


//training scenario
// Function to activate the altitude  alert
function activateAltitudeAlert() {
  console.log("Altitude alert activated")
  document.getElementById('altitudeSound').play();
 logAction({"page": "Inflight", "action": " Altitude alert activated"}); 
  const altitudeoverlay = document.getElementById('altitudealertOverlay');
  document.body.classList.add('dull-background');
  altitudeoverlay.style.visibility = 'visible';
  altitudeoverlay.style.opacity = '1';
  }

  // Function to show more information for altitude alert
  function showAltitudeInfo() {
   logAction({"page": "Inflight", "action": "Altitude alert- show more info button pressed"}); 
    document.getElementById('altitudeSound').pause();
    document.getElementById('altitudeSound').currenTime=0;
    const altitudealertBox = document.getElementById('altitudealertBox');
    altitudealertBox.classList.add('expanded');
    document.getElementById('altitudealertExplanation').style.display = 'block';
    document.getElementById('altitudemoreInfo-Button').style.display = 'none';
    //document.getElementById('pressureWarningcloseButton').style.display = 'block';
    // Stop the flashing animation
    document.getElementById('altitudeText').style.animation = 'none';
    altitudeAlert=0
     //updating the server
     fetch("/var?altitude-alert=" + altitudeAlert)

  }

  // Function to submit pressure value
  function submitAltitudeValue() {
    document.getElementById('altitudeSound').pause();
    document.getElementById('altitudeSound').currenTime=0;
    const altitudeValue = document.getElementById('altitudeValue').value;
    console.log(altitudeValue)
   logAction({"page": "Inflight", "action": "Altitude alert- submit button pressed with altitude value as:"+ altitudeValue}); 
    const dialog = document.createElement('dialog');
    dialog.innerHTML = `
    <p>Altitude successfully changed to ${altitudeValue} feet</p>
    <br>
    <centre><button onclick="this.closest('dialog').close()">OK</button></centre>
    `;
    document.body.appendChild(dialog);
    dialog.showModal();
  logAction({"page": "Inflight", "action": "Altitude alert- altitude submitted"});  
   closeAltitudeAlert()
  }

  // Function to close the altitude alert
  async function closeAltitudeAlert()  {
    console.log('pressed')
   logAction({"page": "Inflight", "action": "Altitude alert close button pressed"}); 
    const altitudeoverlay = document.getElementById('altitudealertOverlay');
    altitudeoverlay.style.opacity = '0';
    altitudeoverlay.addEventListener('transitionend', () => {
      altitudeoverlay.style.visibility = 'hidden';
      document.body.classList.remove('dull-background');
    }, { once: true });
    altitudeAlert=0  
    //updating the server
    await fetch("/var?altitude-alert=" + altitudeAlert)
  }

  //Weather Emergency
  // Function to activate the weather emergency alert
  function activateWeatherAlert() {
   logAction({"page": "Inflight", "action": "Weather emergency- emergnecy propmt displayed"}); 
    console.log("Weather Emergency",weatherEmergency)
    document.getElementById('weathersirenSound').play();
    const weatheroverlay = document.getElementById('weatheralertOverlay');
    document.body.classList.add('dull-background');
    weatheroverlay.style.visibility = 'visible';
    weatheroverlay.style.opacity = '1';
  }

    // Function to show more information about weather emergency and stop the siren
    function showMoreWeatherInfo() {
     logAction({"page": "Inflight", "action": "Weather emergency- show more info button pressed"}); 
      document.getElementById('weathersirenSound').pause();
      document.getElementById('weathersirenSound').currentTime = 0;
      const weatheralertBox = document.getElementById('weatheralertBox');
      weatheralertBox.classList.add('expanded');
      weatherEmergency=0
      console.log(weatherEmergency); 
      //updating the server
      fetch("/var?weather-emergency=" + weatherEmergency)
      document.getElementById('weatheralertExplanation').style.display = 'block';
      document.getElementById('weathermoreInfoButton').style.display = 'none'; 
      document.getElementById('weathercloseButton').style.display = 'block';
      document.getElementById('weathercloseButton').onclick = () => { closeWeatherAlert(); }
      /* document.getElementById('weatherCDButton').style.display = 'block';
      document.getElementById("weatherCDButton").onclick = () => { closeWeatherAlert(); 
     logAction({"page": "Inflight", "action": "change destination button pressed during weather emergency"}); 
      window.location.href = '/hai-interface/change-destination?inflight=' + 1 + '&emergency=' + 1
      } */
    
    }

    // Function to close weather emergency alert
    async function closeWeatherAlert() {
      console.log("closing")
     logAction({"page": "Inflight", "action": "Weather emergency- close button pressed"});
      document.getElementById('weathersirenSound').pause(); 
      document.getElementById('weathersirenSound').currentTime = 0;
      const weatheroverlay = document.getElementById('weatheralertOverlay');
      weatheroverlay.style.opacity = '0';
      weatheroverlay.addEventListener('transitionend', () => {
        weatheroverlay.style.visibility = 'hidden';
        document.body.classList.remove('dull-background');
      },{ once: true });
      weatherEmergency=0
      console.log(weatherEmergency); 
      //updating the server
      await fetch("/var?weather-emergency=" + weatherEmergency)
    }


let vitalsShown = false;

function schedulePrompt() {
  setInterval(async () => {
  // Only run on certain pages
  if (!["/hai-interface/inflight", "/hai-interface/change-destination", "/hai-interface/help", "/hai-interface/change-altitude"].includes(window.location.pathname)) {
    return;
  }
  console.log('last_radio_update', last_radio_update)
  console.log(new Date().getTime())

  // Speak the radio update prompt
  if (new Date().getTime() - last_radio_update > 105000) {
    console.log('asking radio update');
    speakRadioPrompt();
    last_radio_update = new Date().getTime() // Update the time the radio prompt was spoken
    console.log('Radio update asked');
    vitalsShown = false;  // Reset vitals flag for next cycle
    await fetch("/var?last_radio_update=" + last_radio_update)
  }
  else if (!vitalsShown && new Date().getTime() - last_radio_update > 60000) {
    if (timeToDestination > 0.5) {
      console.log("Showing vitals prompt");
      showVitalsPrompt();
      vitalsShown = true;
    }

  }
  // Schedule next radio prompt after 105s (1 minute + 45 seconds)
  //setTimeout(speakRadioPrompt, 105000);

}, 5000)
}



// Use browser speech synthesis for radio prompt
function speakRadioPrompt() {
  const message = "N A S X G S, this is Ground Control asking for update on flight status, patient status and estimated time to destination.";
  const voices = window.speechSynthesis.getVoices();
  const utterance = new SpeechSynthesisUtterance(message);
  utterance.voice = voices[18];
  utterance.rate = 1.05;
  utterance.pitch = 1;
  utterance.volume = 1;
  window.speechSynthesis.speak(utterance);
  console.log('Radio update');
  console.log(utterance.voice)
}

// Show vitals prompt visually
function showVitalsPrompt() {
  logAction({ "page": "inflight", "action": "displaying vitals prompt" })
  console.log('vitals logging prompt')
  document.getElementById('vitals').style.display = "flex"
  // Auto-remove after 10s
  setTimeout(() => {
    document.getElementById('vitals').style.display = "none"
  }, 10000);
}




 // Activate the emergency alert for demo purposes

 //EngineFailure=1
 //window.onload = activateEngineAlert;

 //window.onload = activateWarningAlert;
 //EmptyTank=1
 //window.onload =activateFuelAlert;
