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

function addMarkers(latlong, infowindow, stopid, fullname, routes){
    var marker = new google.maps.Marker({
        position: latlong,
        title: 'test marker',
        draggable: false,
        map: map
    });

    google.maps.event.addListener(marker, 'click', function(content){
        infowindow.setContent("<b>Bus Stop No. "+stopid+"</b><br><br>Name: "+fullname+"<br><br><b>Routes serving this stop:</b><br><br>"+routes);
        infowindow.open(map, marker);
    });
}

$( window ).on( "load", function() {
    console.log( "Page ready!!" );

    var infowindow = new google.maps.InfoWindow();
    //addMarkers(new google.maps.LatLng(53.3498, -6.2603), infowindow);

    $.getJSON("/busstops", function(busData){
        console.log(busData.results[0].stopid);

        _.forEach(busData.results, function(bus_stop){
            //console.log(value.operators[0].routes);
            //console.log(value.longitude);
            addMarkers(new google.maps.LatLng(bus_stop.latitude, bus_stop.longitude), infowindow, bus_stop.stopid, bus_stop.fullname, bus_stop.operators[0].routes);
        });
    });
});