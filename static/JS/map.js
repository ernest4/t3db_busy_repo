'use strict';

function initMap(){
    var mapDiv = document.getElementById("map");
    var mapOptions = {
        center: new google.maps.LatLng(53.3498, -6.2603),
        zoom: 11
    };

    var map = new google.maps.Map(mapDiv, mapOptions);
}
