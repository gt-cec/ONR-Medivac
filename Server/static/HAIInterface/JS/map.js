window.setInterval(async () => {
    getSimulatorData()

    // if resetting the user display, change page
    if (resetUserDisplay == "1") {
        await fetch("/var?reset-user-display=0")
        window.location.href = "/hai-interface"
    }

    updateMap()
    //time to destination 
    document.getElementById("dest-time").innerHTML="Time to Destination: " +timeToDestination +" mins"

    // select the item if there is no map selection
    if (typeof mapSelection === "undefined") {
        selectItem(departureIndex)
    }
}, 500)

function showMap() {
    log({ page: "map", action: "show map" })

    // if setting the destination, flash the instruction
    document.getElementById("flightmap-instruction").style.display =
        setDestination ? "flex" : "none"

    targetIndex = destinationIndex
    selectItem(departureIndex)

    document.getElementById("center").style.zIndex = -1
    document.getElementById("center").classList.add("fadeout")
    document.getElementById("center").classList.remove("fadein")

    document.getElementById("map-container").style.zIndex = 1
    document.getElementById("map-container").classList.add("fadein")
    document.getElementById("map-container").classList.remove("fadeout")
    
   

    // set the map tab as selected
    document.getElementById("map").classList.add("map-selected")
    document.getElementById("map").onclick = () => hideMap()

     // show the helipads
     if (!helipadsLoaded) {
        helipadsLoaded = true
        showHelipads(helipads)
    }
}




function selectItem(helipadIndex) {
    // make sure helipad index is defined
    if (typeof helipadIndex === "undefined" || helipadIndex == -1 ) {
        return
    }
    log({ page: "map", action: "selected helipad", value: helipadIndex })

    mapSelection = helipadIndex

    if (helipadIndex == 100) {
        document.getElementById("bottom-nav-name").innerHTML ="Select a helipad to see details."
        document.getElementById("bottom-nav-address").innerHTML =""
        document.getElementById("bottom-nav-type").innerHTML = ""     
    }

    // set the info
    else{
        document.getElementById("bottom-nav-name").innerHTML =
            helipads[helipadIndex].name
        document.getElementById("bottom-nav-address").innerHTML =
            helipads[helipadIndex].location
        document.getElementById("bottom-nav-type").innerHTML = helipads[helipadIndex]
            .hasHospital
            ? "Hospital"
            : "Commercial"
        document
            .getElementById("bottom-nav-indicator")
            .setAttribute(
                "src",
                "../static/HAIInterface/img/" +
                (helipads[helipadIndex].hasHospital
                    ? "hospital-icon.png"
                    : "commercial-icon.png")
            )
    }

    // show the "DESTINATION" if applicable
    if (helipadIndex == targetIndex) {
        document.getElementById("bottom-nav-current-destination").style.display =
            "flex"
        document.getElementById("bottom-nav").style.backgroundColor = "peachpuff"
    } else {
        document.getElementById("bottom-nav-current-destination").style.display =
            "none"
        document.getElementById("bottom-nav").style.backgroundColor = "#b9deff"
    }

    // show the "DEPARTURE HELIPORT" if applicable
    if (helipadIndex == departureIndex) {
        document.getElementById("bottom-nav-departure-heliport").style.display =
            "flex"
    } else {
        document.getElementById("bottom-nav-departure-heliport").style.display =
            "none"
    }

    // show the "NEAREST" if applicable
    if (helipads[helipadIndex].nearest) {
        document.getElementById("bottom-nav-nearest-heliport").style.display =
            "flex"
    } else {
        document.getElementById("bottom-nav-nearest-heliport").style.display =
            "none"
    }
    //let setDestination= true
    // set the destination box if applicable
    if (setDestination) {
        log({ page: "map", action: "set destination", value: targetIndex })
        fillDestinationBox(targetIndex)
    }
}

function hideMap() {
    log({ page: "map", action: "hide map" })
    document.getElementById("center").style.zIndex = 1
    document.getElementById("center").classList.add("fadein")
    document.getElementById("center").classList.remove("fadeout")

    document.getElementById("map-container").style.zIndex = -1
    document.getElementById("map-container").classList.add("fadeout")
    document.getElementById("map-container").classList.remove("fadein")

    // set the map tab as selected
    document.getElementById("map").classList.remove("map-selected")
    document.getElementById("map").onclick = () => showMap()
}

async function getSimulatorData() {
    await fetch("/var")
        .then((resp) => {
        // Check if the request was successful
        if (!resp.ok) {
            throw new Error('Network response was not ok');
        }
        // Parse the response as JSON
        return resp.json();
        })
        .then((data) => {
            console.log("loaded")
            compass = data.compass
            latitude = parseFloat(data.latitude)
            longitude = parseFloat(data.longitude)
            altitude=parseFloat(data.altitude)
            departureIndex = data["departure-index"]
            destinationIndex = data["destination-index"]
            userId = data["user-id"]
            studyStage = data["study-stage"]
            decisionState = data["decision-state"]
            vitalsState = data["vitals-state"]
            airspaceState = data["airspace-state"]
            satisfied = data["satisfied"]
            destChanged = data["dest-changed"]
            flightStartTime = data["flight-start-time"]
            resetUserDisplay = data["reset-user-display"]
            resetVitalsDisplay = data["reset-vitals-display"]
            timeToDestination=data["time-to-destination"]
            changeAltitude = data["change-altitude"]

            if ((urlParams.get("emergency") == "1") && (studyStage == '3' || studyStage == '4')) {
                //making FTY Heliport the nearest in emergency
                helipads[20].nearest=true
            }
            // show the helipads
            if (!helipadsLoaded) {
                helipadsLoaded = true
                showHelipads(helipads)
            }
    })
        .catch(error =>{
            console.error('Fetch error:', error);
                })
    return false
}

function showHelipads(helipads) {
    // Icon options
    var helipadIconOptions = {
        iconUrl: "/static/HAIInterface/img/blue-helipad-icon.png",
        iconSize: [35, 35],
    }

    var hospitalIconOptions = {
        iconUrl: "/static/HAIInterface/img/red-hospital-icon.png",
        iconSize: [35, 35],
    }

    var nearestIconOptions = {
        iconUrl: "/static/HAIInterface/img/green-helipad-icon.png",
        iconSize: [35, 35],
    }

    var destinationIconOptions = {
        iconUrl: "/static/HAIInterface/img/arrival.png",
        iconSize: [50, 50],
    }

    var  departureIconOptions = {
        iconUrl: "/static/HAIInterface/img/departure.png",
        iconSize: [50, 50],
    }

    var selectedlIconOptions = {
        iconUrl: "/static/HAIInterface/img/orange-helipad-icon.png",
        iconSize: [45, 45],
    }

    // Creating Marker Options
    var markerOptions = {
        clickable: true,
        draggable: false,
        rotationAngle: 0,
        rotationOrigin: "center",
        zIndexOffset: 1,
        iconSize:     [38, 95], // size of the icon
        iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
        popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
    }


    // create a marker for each hospital
    for (i in helipads) {
        let options = markerOptions
        options.icon = L.icon(
            i == destinationIndex
                ? destinationIconOptions
                : helipads[i].nominal
                    ? destinationIconOptions
                    : helipads[i].nominal_departure
                        ? departureIconOptions
                        : helipads[i].nearest
                            ? nearestIconOptions
                            : helipads[i].hasHospital
                                ? hospitalIconOptions
                                : helipadIconOptions
        )
        let marker = L.marker(
            [helipads[i].latitude, helipads[i].longitude],
            options
        )
        let helipadIndex = i

        
        if(helipadIndex==targetIndex){
            let newDestination= markerOptions
            newDestination.icon = L.icon(destinationIconOptions)
                let  newDestinationmarker = L.marker(
                    [helipads[targetIndex].latitude, helipads[targetIndex].longitude],
                    newDestination)
                newDestinationmarker.addTo(map)

        }
        marker.on("click", function (ev) {

            //remove the marker from the previous
           
            selectItem(helipadIndex)
            let selected= markerOptions
            selected.icon = L.icon(selectedlIconOptions)
            let selectedmarker = L.marker(
                [helipads[helipadIndex].latitude, helipads[helipadIndex].longitude],
                selected)
            selectedmarker.addTo(map)

            /* if (setDestination) {
                selectedmarker.bindPopup("Set Destination", autoClose=false).addTo(map)
            }
            else {
            selectedmarker.addTo(map)
            } */

            selectedmarker.on("mouseout", function (ev) {
                console.log('out')
                map.removeLayer( selectedmarker)
                if(helipadIndex!=targetIndex){
                    selectItem(100)
                }
        })
    })
        marker.addTo(map)
        if (setDestination) {
            console.log('set destination')
            fillDestinationBox(helipadIndex)
            //marker.bindPopup(popup).openPopup();
            /*  marker.bindPopup('<b>Marker Info</b><br><button class="popup-button" onclick="setAsDestination(helipadIndex)">Set as destination</button>').on('click', function(e) {
                
        }); */
      }
  }
}

function setAsDestination(helipadIndex) {
    if (!setDestination) {
        alert('Cannot select destination.');
        return;
    }
    
    //var selectedMarker = button.closest('.leaflet-popup')._source; // Access the marker from the popup context
    
    // Condition to check if the destination is favorable
    var isFavorable = helipadIndex== 11; 
    
    if (isFavorable) {
        alert('Success! Rerouting to ' + helipads[helipadIndex].name);
    } else {
        alert("Sorry, Unfavorable conditions, can't reroute to " + helipads[helipadIndex].name);
    }
    
    map.closePopup(); // Close the popup after making a decision
}

// function for filling the destination information
function fillDestinationBox(helipadIndex) {
    // make sure helipad index is defined
    if (typeof helipadIndex === "undefined") {
        return
    }

    if (helipadIndex == -1) {
        document.getElementById("destination-box-name").innerHTML =
            "Select a helipad to see details."
        return
    }

    // set the info
    document
        .getElementById("destination-box-indicator")
        .setAttribute(
            "src",
            "../static/HAIInterface/img/" +
            (helipads[helipadIndex].hasHospital
                ? "hospital-icon.png"
                : "commercial-icon.png")
        )
    document.getElementById("destination-box-name").innerHTML =
        helipads[helipadIndex].name
    document.getElementById("destination-box-address").innerHTML =
        helipads[helipadIndex].location
    document.getElementById("destination-box-type").innerHTML = helipads[
        helipadIndex
    ].hasHospital
        ? "Hospital"
        : "Commercial"
    // show the "DESTINATION" if applicable
    if (helipadIndex == destinationIndex) {
        document.getElementById(
            "destination-box-current-destination"
        ).style.display = "flex"
    } else {
        document.getElementById(
            "destination-box-current-destination"
        ).style.display = "none"
    }

    // show the "DEPARTURE HELIPORT" if applicable
    if (helipadIndex == departureIndex) {
        document.getElementById(
            "destination-box-departure-heliport"
        ).style.display = "flex"
    } else {
        document.getElementById(
            "destination-box-departure-heliport"
        ).style.display = "none"
    }

    // show the "NEAREST" if applicable
    if (helipads[helipadIndex].nearest) {
        document.getElementById("destination-box-nearest-heliport").style.display =
            "flex"
    } else {
        document.getElementById("destination-box-nearest-heliport").style.display =
            "none"
    }

    //document.getElementById("set_dest").onclick= ()
  }


function updateMap() {
    var pos = L.latLng(latitude, longitude)
    planeMarker.slideTo(pos, {
        duration: 1500,
    })
    planeMarker.setRotationAngle(compass)

    map.panTo(pos)
}

function initMap() {
    // Create map options
    var mapOptions = {
        center: [33.7992717, -84.3855556],
        zoom: 13,
        dragging: false,
        zoomControl: true,
        boxZoom: false,
        doubleClickZoom: false,
        keyboard: false,
        attributionControl: false,
        scrollWheelZoom: false,
    }

    // Creating a map object
    map = new L.map("flightmap", mapOptions)

    // Creating a Layer object
    var simple = new L.tileLayer.provider("CartoDB.Voyager")
    var basic = new L.tileLayer.provider("Jawg.Terrain", {
        variant: "",
        accessToken:
            "CQVU4GpEMHf6XeTxVy2x2zRCDJpr6zFX61tYzcs27Jeus4kfc9XBUNfz3mhPakJZ",
    })

    // Adding layers to the map
    map.addLayer(basic)

    // Icon options
    var iconOptions = {
        iconUrl: "/static/HAIInterface/leaflet/plane.png",
        iconSize: [35, 35],
    }

    // Creating a custom icon
    var customIcon = L.icon(iconOptions)

    // Creating Marker Options
    var markerOptions = {
        clickable: true,
        draggable: false,
        icon: customIcon,
        rotationAngle: 0,
        rotationOrigin: "center",
        zIndexOffset: 2,
    }

    // Creating a Marker
    planeMarker = L.marker([latitude, longitude], markerOptions)

    // Adding marker to the map
    planeMarker.addTo(map)

    // create the flightmap onclick
    // var targLink    = document.getElementById ("flightmap");
    // var clickEvent  = document.createEvent ('MouseEvents');
    // clickEvent = new Event('dblclick', true, true);
    // targLink.dispatchEvent (clickEvent);
    // document.getElementById("flightmap").ondblclick = () => {
    //     if (!setDestination || typeof mapSelection === "undefined") {
    //         return
    //     }

    //     targetIndex = mapSelection
    //     selectItem(mapSelection) // reload the bottom bar for the selected item
    // }

    document.getElementById("flightmap").addEventListener("dblclick", () => {
        if (!setDestination || typeof mapSelection === "undefined") {
            return
        }
        targetIndex = mapSelection
        selectItem(mapSelection) // reload the bottom bar for the selected item
        //showHelipads(helipads)
       
    })
}
