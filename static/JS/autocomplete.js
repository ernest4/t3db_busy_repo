
// FUNCTION TO PROVIDE AUTOFILL ON LOCATION SEARCHES

$( window ).on ("load", function () {

    //set the autocomplete callback for destination autosuggest powere by directions api
    $( "#destination" ).autocomplete({
        source: function(request, response){
            var availableTags = [];

            var to_input = request.term; //This is the user input
            //console.log(to_input); //DEBUGGING

            $.getJSON( "/autocomp" + "?format=json&operator=bac&stopname="+to_input, function(data) {

                _.forEach(data.results, function(busStops){
                    //availableTags.push(busStops.stopid+" "+busStops.fullname );
                    availableTags.push({ label: busStops.fullname+" "+busStops.stopid, value: busStops.latitude+","+busStops.longitude });
                });

                //console.log(availableTags); //DEBUGGING
                response(availableTags);

            }).done(function(){
                console.log("got autosuggest data");
            }).fail(function(){
                alert("failed autosuggest");
            }).always(function(){
                //
            });
        },
        minLength: 3 //Number of characters after which the autosuggest should start...
    });

    // Set the autocomplete for bus routes from GTFS routes file
    $( "#bus_number" ).autocomplete({
        source: function(request, response){
            var availableTags = [];

            var bus_num_input = request.term; //This is the user input
            // console.log(bus_num_input); //DEBUGGING

            $.getJSON( "/autocomp/routes", function(data) {

                _.forEach(data, function(busRoute){

                    // Only add busRoute as tag if it starts with input
                    if (busRoute.startsWith(bus_num_input)) {
                        availableTags.push({label: busRoute, value: busRoute});
                    }
                });

                // console.log(availableTags); //DEBUGGING
                response(availableTags);

            }).done(function(){
                // console.log("got autosuggest data");
            }).fail(function(){
                alert("failed autosuggest");
            }).always(function(){
                //
            });
        },
        minLength: 1 //Number of characters after which the autosuggest should start...
    });

    //set the autocomplete for start location form input
    $( "#location_from" ).autocomplete({
        source: function(request, response){
            var availableTags = [];

            var to_input = request.term; //This is the user input
            //console.log(to_input); //DEBUGGING

            $.getJSON( "/autocomp" + "?format=json&operator=bac&stopname="+to_input, function(data) {

                _.forEach(data.results, function(busStops){
                    //availableTags.push(busStops.stopid+" "+busStops.fullname );
                    availableTags.push({ label: busStops.fullname+" "+busStops.stopid, value: busStops.stopid });
                });

                //console.log(availableTags); //DEBUGGING
                response(availableTags);

            }).done(function(){
                console.log("got autosuggest data");
            }).fail(function(){
                alert("failed autosuggest");
            }).always(function(){
                //
            });
        },
        minLength: 3 //Number of characters after which the autosuggest should start...
    });

    //set the autocomplete for destination location form input
    $( "#location_to" ).autocomplete({
        source: function(request, response){
            var availableTags = [];

            var to_input = request.term; //This is the user input
            //console.log(to_input); //DEBUGGING

            $.getJSON( "/autocomp" + "?format=json&operator=bac&stopname="+to_input, function(data) {

                _.forEach(data.results, function(busStops){
                    //availableTags.push(busStops.stopid+" "+busStops.fullname );
                    availableTags.push({ label: busStops.fullname+" "+busStops.stopid, value: busStops.stopid });
                });

                //console.log(availableTags); //DEBUGGING
                response(availableTags);

            }).done(function(){
                console.log("got autosuggest data");
            }).fail(function(){
                alert("failed autosuggest");
            }).always(function(){
                //
            });
        },
        minLength: 3 //Number of characters after which the autosuggest should start...
    });

    

});