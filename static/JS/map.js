'use strict';

var map;

function initMap(){
    var mapDiv = document.getElementById("map");
    var mapOptions = {
        center: new google.maps.LatLng(53.3498, -6.2603),
        zoom: 11
    };

    map = new google.maps.Map(mapDiv, mapOptions);
}

function addMarkers(latlong){
    var marker = new google.maps.Marker({
        position: latlong,
        title: 'test marker',
        draggable: false,
        map: map
    })
}

$( window ).on( "load", function() {
    console.log( "Page ready!!" );
    //addMarkers(new google.maps.LatLng(53.3498, -6.2603));

    $.getJSON("/busstops", function(busData){
        console.log(busData.results);
    });
});