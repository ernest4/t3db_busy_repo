
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

    //set the autocomplete for bus routes
    $( "#bus_number" ).autocomplete({
        source: function(request, response){
            var availableTags = [];

            var bus_num_input = request.term; //This is the user input
            //console.log(bus_num_input); //DEBUGGING

            $.getJSON( "/autocomp/routes" + "?format=json&operator=bac", function(data) {

                _.forEach(data.results, function(busRoute){
                    //availableTags.push(busStops.stopid+" "+busStops.fullname );
                    if (busRoute.route.includes(bus_num_input)) { //Manual pruning of results as RTPI does not offer search of bus route based on partial ID...
                        availableTags.push({ label: busRoute.route, value: busRoute.route });
                    }
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