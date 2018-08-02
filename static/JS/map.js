'use strict';

var map;
var markers = []; //Create an array of markers for the marker cluster function
var Shopmarkers = []; // Arrays for each type of destination
var travelmarkers = [];
var activitiesmarkers = [];
var outdoorsmarkers = [];
var familymarkers = [];
var sightsmarkers = [];
// Create one object that contains all tourist markers
var markerslists = [travelmarkers, Shopmarkers , activitiesmarkers , sightsmarkers,  familymarkers, outdoorsmarkers ];
var userMarker; //User marker handle
var boxeschecked //global var to count number of boxes checked in explore

//Loads the map
function initMap(){
    var mapDiv = document.getElementById("map");
    var mapOptions = {
        center: new google.maps.LatLng(53.3498, -6.2603),
        zoom: 14
    };

    map = new google.maps.Map(mapDiv, mapOptions);
}



// From the picture you posted, it say it's disabled...
//
// Go to Developer Console -> APIs & auth -> APIs
//
// Search for Geocoding and click on Google Maps Geocoding API -> Enable API. Do the same thing for Geolocating
//




//Makes a marker for busstops and add onlick functionality
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

// Explorer map point indormation
var travel_links = [
       ['Dublin Airport', 53.4264513, -6.2521038],
       ['Europecar Dublin City', 53.3484939, -6.2400041],
       ['St Stephen\'s Green Luas', 53.3391899, -6.2635223],
       ['Dublin Connolly Station', 53.351829, -6.2517332],
       ['Aircoach O\'Connell Street', 53.3517839, -6.2633345]
   ];
var Shopping = [
       ['Grafton Street', 53.3421532, -6.2620394],
       ['Henry Street', 53.3493502, -6.2652141],
       ['Dundrum Shopping Centre', 53.2874809, -6.2438303],
       ['St Stephen\'s Green Shopping Centre', 53.3399155, -6.26479],
       ['Powerscourt Townhouse Centre', 53.3422148, -6.2639623],
       ['O\'Connell Street', 53.3512448, -6.2629729]
   ];

var Activities = [
       ['AdventureRooms Dublin', 53.3494134, -6.2721929],
       ['Incognito Escape Room', 53.3434981, -6.2833655],
       ['Escape Boats', 53.3413279, -6.2411257],
       ['Hop on Hop Off', 53.3505611, -6.2631577],
       ['GoQuest Indoor Challenge Zone', 53.4007191, -6.3176467]
   ];
var SightSeeing = [
       ['Trinity College Dublin', 53.3517996, -6.2699275],
       ['Guinness Storehouse', 53.3418772, -6.2889033],
       ['St. Patrick\'s Cathedral', 53.3395186, -6.2736707],
       ['Temple Bar', 53.3454388, -6.2690681],
       ['Dublin Castle', 53.3428893, -6/2696224],
       ['Christ Church Cathedral', 53.3435162, -6.2732542],
       ['St Stephen\'s Green', 53.3369012, -6.2619592],
       ['City Hall', 53.3438672, -6.269369]
   ];
var Family = [
       ['Dublin Zoo Phoenix Park', 53.3561967, -6.3074838],
       ['The Ark - Temple Bar', 53.3449479, -6.2672568],
       ['Viking Splash Tours', 53.3392812, -6.260881, 3],
       ['Imaginosity, Dublin Children\'s Museum', 53.2774382, -6.2187599],
       ['The Chocolate Warehouse, Dublin', 53.3148733, -6.3343803]
   ];
var Outdoors = [
       ['Phoenix Park', 53.3558855, -6.3320073],
       ['National Botanic Gardens', 53.3725525, -6.274101],
       ['Howth', 53.3776565, -6.200751],
       ['Graystones', 53.1450113, -6.150619],
       ['Sandymount Strand', 53.3305784, -6.2332952]
   ];


// Function to create explorer markers
function addExMarkers(latlong, attraction, type , icon, infowindow, infowindow_content){
  //create a marker

    var marker = new google.maps.Marker({
        position: latlong,
        title: attraction,
        draggable: false,
        map: map,
        icon: icon
    });
    // Keep track of the different groups of markers
    markerslists[type].push(marker);

    //Add the pop up box to marker for onclick
   google.maps.event.addListener(marker, 'click', function(content){
       infowindow.setContent(infowindow_content);
       infowindow.open(map, marker);
   });

}

// Fucntion to show groups of destinations at a time
function showDestinations(destinations, type, icon){
    // Set up info window for each type
    var infowindow = new google.maps.InfoWindow();
    for (var i = 0 ; i < destinations.length ; i++){
        var latlon = {lat: destinations[i][1], lng: destinations[i][2]};
        let infowindow_content = "<b>"+destinations[i][0]+"</b>";
        //Create markers
        addExMarkers(latlon, destinations[i][0], type, icon,infowindow, infowindow_content);

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
  markerArray = [] //Remove references to the markers to delete them
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

    var autocompleteFrom = new google.maps.places.Autocomplete(document.getElementById('location_from_ex'));
    var autocompleteTo = new google.maps.places.Autocomplete(document.getElementById('location_to_ex'));
    // This is ready to go but needs On the go input to change id name to destinationOnTheGo
    //var autocompleteOnTheGo = new google.maps.places.Autocomplete(document.getElementById('destinationOnTheGo'));


    autocompleteFrom.bindTo('bounds', map);
    autocompleteTo.bindTo('bounds', map);
    //autocompleteOnTheGo.bindTo('bounds', map);

    // autocompleteOnTheGo.addListener('place_changed', function() {
    //     var place = autocompleteOnTheGo.getPlace();
    //     console.log(place);
    // });

    autocompleteFrom.addListener('place_changed', function() {
        var place = autocompleteFrom.getPlace();
        console.log(place);
    });
    autocompleteTo.addListener('place_changed', function() {
        var place = autocompleteTo.getPlace();
        console.log(place);
    });

    //==================================================================================
    function calculateDirections(origin, destination, date_time) {

        console.log("Directions function "+date_time);

        var directionsService = new google.maps.DirectionsService;
        var directionsDisplay = new google.maps.DirectionsRenderer;

        var request = {
            origin: origin,
            destination: destination,
            travelMode: 'TRANSIT',

            transitOptions: {
                //departureTime: date_time,
                modes: ['BUS']
            }
        }

        directionsDisplay.setMap(map);
        directionsService.route(request, function (result, status) {
            console.log(status);
            console.log(result);
            console.log(origin);
            console.log(destination);

            if (status == 'OK') {
                directionsDisplay.setDirections(result);
                console.log(result);

            }
            else {
                console.log("Issue with directions request");
            }
        });
    }
//======================================================================


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

        console.log(directionsData.routes[0].legs[0].steps); //DEBUGGING

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

          //Add route markers
          addMarkers(new google.maps.LatLng(step.start_location), markerColor, infowindow, infowindow_content, step.html_instructions);

        });

        //Add the destination marker
        index++; //This is the number of the final step (i.e. destination)
        //Create and parse a latitude, longitude object for the marker
        let to_obj = {}
        to_obj.lat = parseFloat(to.split(',')[0]);
        to_obj.lng = parseFloat(to.split(',')[1]);
        //console.log(to_obj); //DEBUGGING
        markerColor = "red";
        var infowindow_content = "<b>["+index+"]Destination</b>";
        addMarkers(new google.maps.LatLng(to_obj), markerColor, infowindow, infowindow_content, "");

      }).done(function(){
        console.log("Got directions data...");
      }).fail(function(){
        console.log("Failed to get directions data...");
      }).always(function(){
        //...
      });
    }

    //set the directions button callback...
    $( '#directionsButtonEX' ).click(function(){
      //displayDirectionMarkers(userPosition, {lat: 53.338331, lng: -6.2854988}); //53.338331,-6.2854988
      //console.log(typeof $('#destination').val());
      //deleteMarkers(markers); //clear current direction markers

       //var originex = {lat: 53.3435162, lng:-6.2732542};
       //var destination = {lat: 53.3369012, lng:-6.2619592};


        let origin = $('#location_from').val();
        let destination = $('#location_to').val();

        let date = $('#datepicker_ex').val();
        let time = $('#clockpicker').val();
        // Convert time to seconds
        console.log(date);
        var a = time.split(':');
        var seconds = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);

        //date = date.getTime()/1000;
        var date_time = date + seconds;

        console.log(date_time);

        calculateDirections(origin, destination, date_time); //show the new direction marker//
        // displayDirectionMarkers(originex, destination); //show the new direction markers
    });



    //set the directions button callback...
    $( '#directionsButton' ).click(function(){
      //displayDirectionMarkers(userPosition, {lat: 53.338331, lng: -6.2854988}); //53.338331,-6.2854988
      //console.log(typeof $('#destination').val());
      deleteMarkers(markers); //clear current direction markers

      let destination = $('#destination').val();
      displayDirectionMarkers(userPosition, destination); //show the new direction markers
    });


    // Functions to add explorer icons based on checkboxes
    $( '#ShoppingCheck' ).click(function(){
        var icon = 'http://maps.google.com/mapfiles/ms/micons/shopping.png';

        if (document.getElementById("ShoppingCheck").checked) {
            showDestinations(Shopping, 1, icon);
        }
        else {
            deleteMarkers(markerslists[1]);
        }
        });

    $( '#TravelLinksCheck' ).click(function(){
        var icon = 'http://maps.google.com/mapfiles/ms/micons/bus.png';

        if (document.getElementById("TravelLinksCheck").checked) {
            showDestinations(travel_links, 0, icon);
        }
        else {
            deleteMarkers(markerslists[0]);
        }
        });

    $( '#ActivitiesCheck' ).click(function(){
        var icon = 'http://maps.google.com/mapfiles/kml/pal2/icon14.png';

        if (document.getElementById("ActivitiesCheck").checked) {
            showDestinations(Activities, 2, icon);
        }
        else {
            deleteMarkers(markerslists[2]);
        }
        });

    $( '#SightsCheck' ).click(function(){
        var icon = 'http://maps.google.com/mapfiles/kml/pal2/icon2.png';

        if (document.getElementById("SightsCheck").checked) {
            showDestinations(SightSeeing, 3, icon);
        }
        else {
            deleteMarkers(markerslists[3]);
        }
        });

     $( '#FamilyCheck' ).click(function(){
         var icon = 'http://maps.google.com/mapfiles/ms/micons/hiker.png';

        if (document.getElementById("FamilyCheck").checked) {
            showDestinations(Family, 4, icon);
        }
        else {
            deleteMarkers(markerslists[4]);
        }
        });

    $( '#OutdoorsCheck' ).click(function(){
        var icon = 'http://maps.google.com/mapfiles/kml/pal2/icon4.png';

        if (document.getElementById("OutdoorsCheck").checked) {
            showDestinations(Outdoors, 5, icon);
        }
        else {
            deleteMarkers(markerslists[5]);
        }
        });

});
