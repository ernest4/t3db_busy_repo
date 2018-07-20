'use strict';

var map;
var markers = []; //Create an array of markers for the marker cluster function
var userMarker; //User marker handle

//Loads the map
function initMap(){
    var mapDiv = document.getElementById("map");
    var mapOptions = {
        center: new google.maps.LatLng(53.3498, -6.2603),
        zoom: 14
    };

    map = new google.maps.Map(mapDiv, mapOptions);
}


//Makes a marker for and add onlick functionality
function addMarkers(latlong, color = "red", infowindow, infowindow_content, stopid, isUser = false){
  //create a marker
    var marker = new google.maps.Marker({
        position: latlong,
        title: "Bus Stop No. " + stopid,
        draggable: false,
        map: map,
        icon: 'http://maps.google.com/mapfiles/ms/icons/' + color + '-dot.png'
    });

    //Add the pop up box to marker for onclick
    google.maps.event.addListener(marker, 'click', function(content){
        infowindow.setContent(infowindow_content);
        infowindow.open(map, marker);
    });

    //special cases
    if (isUser === false){
      markers.push(marker); //Create an array of markers for the marker cluster function
    } else {
      marker.title = stopid; //This will just display the isUser string "You Are Here" instead of bus stop number
      marker.setAnimation(google.maps.Animation.BOUNCE);
      userMarker = marker;
    }
}


//makes the markers invisible by calling this function like setMapForMarkers(some_marker_array, null);
function setMapForMarkers(markerArray, map){
  for (let i = 0; i < markerArray.length; i++){
    markerArray[i].setMap(map);
  }
}


//makes markers invisible and deletes them
function deleteMarkers(markerArray){
  setMapForMarkers(markerArray, null); //Hide all the markers first
  markerArray = [] //Remove references to the markers to delte them
}


//Responds to onclick event when from button is clicked on a marker
function fromButton(element){
    console.log(element.id.slice(5)); //Extract the bus number e.g. "from_623" -> "623"
    console.log(element.innerHTML);

    document.getElementById('from').value = element.id.slice(5); //Populate a form field
}


//Responds to onclick event when to button is clicked on a marker
function toButton(element){
    console.log(element.id.slice(3)); //Extract the bus number e.g. "to_623" -> "623"
    console.log(element.innerHTML);

    document.getElementById('to').value = element.id.slice(3); //Populate a form field
}


//Populate the map with information & markers
$( window ).on( "load", function() { //When DOM & other resourses all loaded and ready...
    console.log( "Page ready!!" ); //FOR DEBUGGING

    var infowindow = new google.maps.InfoWindow(); //Common infowindow handle for all infowindows

    var errorMSG_1 = document.getElementById("error_message_1"); //FOR DEBUGGING
    var errorMSG_2 = document.getElementById("error_message_2"); //FOR DEBUGGING
    var userPosition = {lat: 53.3498, lng: -6.2603}; //Will be center of Dublin by default if no isUser position recieved later on...

    //Get the isUser location
    if (navigator && navigator.geolocation) {
      console.log("Got location");
      //errorMSG_1.innerHTML += "Got location";

      navigator.geolocation.getCurrentPosition(gotPosition, failedToGetPosition);
    } else { 
      console.log("Failed to get location, Geolocation unavailable");
      //errorMSG_2.innerHTML += "Geolocation is not supported by this browser. We could not find your location.";
    }


    function gotPosition(position) { //success
      userPosition = showUserPosition(position);
      //displayBusStopMarkersAtLocation(userPosition, 0.01); //0.01 is ~ 1km
      //displayDirectionMarkers(userPosition, {lat: 53.338331, lng: -6.2854988});
    }


    function failedToGetPosition(error){
      console.log("Error code:" + error.code + ", " + "Error message: " + error.message);

      displayBusStopMarkersAtLocation(userPosition, 0.01); //0.01 is ~ 1km
    }


    function showUserPosition(position){
      //Conversts isUser position from geolocation coords to {lat: xxx, lng: xxx}
      //and add the a marker to the map.
      //
      //returns converted isUser position
      let userPosition = {}
      userPosition.lat = position.coords.latitude;
      userPosition.lng = position.coords.longitude;

      let infowindow_content = "<b>You Are Here</b>";

      addMarkers(new google.maps.LatLng(userPosition.lat, userPosition.lng), "red", infowindow, infowindow_content, "You Are Here", true);
      map.panTo({lat: userPosition.lat, lng: userPosition.lng});

      //errorMSG_2.innerHTML += "Latitude: " + userPosition.lat + "<br>Longitude: " + userPosition.lng; //FOR DEBUGGING...

      return userPosition
    }


    function displayBusStopMarkersAtLocation(coords = {lat: 53.3498, lng: -6.2603}, radius = 0.01){
      //populate the markers around the isUser
      $.getJSON("/busstops", function(busData){

          _.forEach(busData.results, function(bus_stop){
              //console.log(bus_stop.operators[0].routes);

              if (bus_stop.latitude < (coords.lat + radius) && bus_stop.latitude > (coords.lat - radius)
              && bus_stop.longitude < (coords.lng + radius) && bus_stop.longitude > (coords.lng - radius)){
                let infowindow_content = "<b>Bus Stop No: </b>"+bus_stop.stopid
                                    +"<br><br>"
                                    +"<b>Name:</b> "+bus_stop.fullname
                                    +"<br><br>"
                                    +"<b>Routes serving this stop:</b>"
                                    +"<br><br>"+bus_stop.operators[0].routes
                                    +"<br><br>"
                                    +"<button type=\"button\" id=\"from_"+bus_stop.stopid+"\" onclick=\"fromButton(this)\">From "+bus_stop.stopid+"</button>"
                                    +"<br><br>"
                                    +"<button type=\"button\" id=\"to_"+bus_stop.stopid+"\" onclick=\"toButton(this)\">To "+bus_stop.stopid+"</button>";

                addMarkers(new google.maps.LatLng(bus_stop.latitude, bus_stop.longitude), "green", infowindow, infowindow_content, bus_stop.stopid);
              }
        });

      }).done(function() {

      console.log("Done!!"); //for DEBUGING

      //var markerCluster = new MarkerClusterer(map, markers, {
      //    imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
      //});

      }).fail(function() {

      console.log("Failed!!"); //for DEBUGING
      alert("Warnign: map markers could not load...");

      }).always(function(){

      console.log("Always...!"); //for DEBUGING

      });
    }


    function displayDirectionMarkers(from, to){
      //check if input is string or object and convert to string if needed
      let origin = typeof from === "string" ? from : from.lat+","+from.lng;
      let destination = typeof to === "string" ? to : to.lat+","+to.lng;

      $.getJSON("/directions" 
                + "?origin="+origin
                +"&destination="+destination
                +"&mode="+"transit"
                +"&transit_mode="+"bus", function(directionsData){

        //console.log(directionsData.routes[0].legs[0].steps);

        let index = 0; //keep track of which step along the route we are on...
        let markerColor = "blue"; //Blue is bus, Yellow is walking, Red is the user starting location.

        _.forEach(directionsData.routes[0].legs[0].steps, function(step){
          index++;

          console.log(step); //FOR DEBUGGING

          if (step.travel_mode === "TRANSIT") { //must be bus...
            markerColor = "blue";

            var infowindow_content = "<b>["+index+"]Take a: </b>"+step.html_instructions
                                    +"<br><br>"
                                    +"<b>Stop Name:</b> "+step.transit_details.departure_stop.name
                                    +"<br><br>"
                                    +"<b>Routes serving this stop:</b>"
                                    +"<br><br>"+step.transit_details.line.short_name
                                    +"<br><br>";
          } else { //must be walking...
            markerColor = "yellow";
            var infowindow_content = "<b>["+index+"]On foot: </b>"+step.html_instructions;
          }
          if (index == 1) { //First marker is the user starting location, make it red & remove the initial user marker...
            markerColor = "red";
            deleteMarkers([userMarker]);
            //addMarkers(new google.maps.LatLng(step.start_location), "red", infowindow, infowindow_content, step.html_instructions);
          } else { //2nd and further markers are directional waypoints - make them yellow...
            //addMarkers(new google.maps.LatLng(step.start_location), "yellow", infowindow, infowindow_content, step.html_instructions);
          }

          addMarkers(new google.maps.LatLng(step.start_location), markerColor, infowindow, infowindow_content, step.html_instructions);

        });

      }).done(function(){
        console.log("Got directions data...");
      }).fail(function(){
        console.log("Failed to get directions data...");
      }).always(function(){
        //...
      });
    }


    //set the directions button callback...
    $( '#directionsButton' ).click(function(){
      //displayDirectionMarkers(userPosition, {lat: 53.338331, lng: -6.2854988}); //53.338331,-6.2854988
      //console.log(typeof $('#destination').val());
      deleteMarkers(markers); //clear current direction markers

      let destination = $('#destination').val();
      displayDirectionMarkers(userPosition, destination); //show the new direction markers
    });
    
});