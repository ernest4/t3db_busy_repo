'use strict';

var map;

//Loads the map
function initMap(){
    var mapDiv = document.getElementById("map");
    var mapOptions = {
        center: new google.maps.LatLng(53.3498, -6.2603),
        zoom: 11
    };

    map = new google.maps.Map(mapDiv, mapOptions);
}


var markers = [];

//Makes a marker for a stop and adds onlick functionality
function addMarkers(latlong, infowindow, stopid, fullname, routes){
    var marker = new google.maps.Marker({
        position: latlong,
        title: "Bus Stop No. "+stopid,
        draggable: false,
        map: map
    });

    google.maps.event.addListener(marker, 'click', function(content){
        infowindow.setContent("<b>Bus Stop No: </b>"+stopid
                            +"<br><br>"
                            +"<b>Name:</b> "+fullname
                            +"<br><br>"
                            +"<b>Routes serving this stop:</b>"
                            +"<br><br>"+routes
                            +"<br><br>"
                            +"<button type=\"button\" id=\"from_"+stopid+"\" onclick=\"fromButton(this)\">From "+stopid+"</button>"
                            +"<br><br>"
                            +"<button type=\"button\" id=\"to_"+stopid+"\" onclick=\"toButton(this)\">To "+stopid+"</button>");
        infowindow.open(map, marker);
    });

    markers.push(marker);
}

//Responds to onclick event when from button is clicked on a marker
function fromButton(element){
    console.log(element.id.slice(5));
    console.log(element.innerHTML);

    //$( "#from" ).html(element.id.slice(5));
    document.getElementById('from').value = element.id.slice(5);
}

//Responds to onclick event when to button is clicked on a marker
function toButton(element){
    console.log(element.id.slice(3));
    console.log(element.innerHTML);

    document.getElementById('to').value = element.id.slice(3);
}

//Populate the map with the markers
$( window ).on( "load", function() {
    console.log( "Page ready!!" );

    var infowindow = new google.maps.InfoWindow();
    //addMarkers(new google.maps.LatLng(53.3498, -6.2603), infowindow, 5, "testName", [5,6,7,8,8]);

    $.getJSON("/busstops", function(busData){
        _.forEach(busData.results, function(bus_stop){
            //console.log(bus_stop.operators[0].routes);
            addMarkers(new google.maps.LatLng(bus_stop.latitude, bus_stop.longitude),
                         infowindow,
                          bus_stop.stopid,
                           bus_stop.fullname,
                            bus_stop.operators[0].routes);
        });

    }).done(function() {

        console.log("Done!!"); //for DEBUGING
        var markerCluster = new MarkerClusterer(map, markers, {
            imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
        });

        //alert("Zoom in on the map to find your location and choose the closest bus stop. Click on the cluster markers to reveal more stops.");

    }).fail(function() {

        console.log("Failr"); //for DEBUGING
        alert("Warnign: map markers could not load...");

    }).always(function(){

        console.log("Always...!"); //for DEBUGING

    });

    //console.log(markers[0]);
});