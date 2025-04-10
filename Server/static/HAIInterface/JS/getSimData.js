let compass;
let latitude;
let longitude;
let last_radio_update;


window.setInterval(function(){
    //making sure the data is available before executing the function
    getSimulatorData()   //.then(() =>  { 
        updateMap();
        schedulePrompt();
   // });
}, 2000);


function getSimulatorData() {
    fetch("/var").then(resp => resp.json()).then(data => {
        compass = data.MAGNETIC_COMPASS;
        latitude = data.LATITUDE;
        longitude = data.LONGITUDE;
        

    });
    return false;
}


function updateMap() {
    var pos = L.latLng(latitude, longitude);

    marker.slideTo(	pos, {
        duration: 1500,
    });
    marker.setRotationAngle(compass);

    map.panTo(pos);
}

