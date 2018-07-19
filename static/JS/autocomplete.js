
// FUNCTION TO PROVIDE AUTOFILL ON LOCATION SEARCHES

$( window ).on ("load", function () {

    $( "#tags" ).autocomplete({
        source: function(request, response){
            var availableTags = [];

            var to_input = request.term; //This is the user input
            console.log(to_input); //DEBUGGING

            $.getJSON( "/autocomp" + "?format=json&operator=bac&stopname="+to_input, function(data) {

                _.forEach(data.results, function(busStops){
                    //availableTags.push(busStops.stopid+" "+busStops.fullname );
                    availableTags.push({ label: busStops.fullname+" "+busStops.stopid, value: busStops.stopid  });
                });

                console.log(availableTags); //DEBUGGING
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

var callCount = 0;
$('input#location_to').on('keyup', function() {
    console.log("Number of letters: "+this.value.length);
     //var to_input = document.getElementById("location");
    callCount++;
    console.log("Call count: "+callCount);
        
    var to_input = this.value;
    //console.log(to_input.length);
    if(to_input.length>3){
        
        console.log("Searching");
        
        var stopOptions = "";
        $.getJSON( "/autocomp" + "?format=json&operator=bac&stopname="+to_input, function(data) {

            _.forEach(data.results, function(busStops){
                stopOptions += "<option value=\"" + busStops.stopid + "\">" + busStops.fullname + "</option>";
            });

            $('#stop_list_to').append(stopOptions);

        }).done(function(){
            console.log("got autosuggest data");
        }).fail(function(){
            alert("failed autosuggest");
        }).always(function(){
            //
        });
    }
});
    
    
    function pred() {
        
            //var to_input = document.getElementById("location");
        
        var to_input = this.value;
            console.log(to_input.length);
            if(to_input.length>3){
                
                console.log("Searching");
                
                var frag = document.createDocumentFragment();
                var stopOptions = "";
                $.getJSON( "/autocomp" + "?format=json&stopname="+to_input, function(data) {

                    _.forEach(data.results, function(busStops){

                        var option = document.createElement("OPTION");
                        option.value = busStops.stopid;
                        option.textContent = busStops.fullname;
                        frag.appendChild(option);

                    //  stopOptions += "<option value=\"" + busStops.stopid + "\">" + busStops.fullname + "</option>";


                    });

                    $('#stop_list').append(frag);

                    // $('#stop_list').append(stopOptions);

                }).done(function(){
                    console.log("got autosuggest data");
                }).fail(function(){
                    alert("failed autosuggest");
                }).always(function(){
                    //
                });
            }
    }

                  
                  
    function pred1(){

            var routeOption = "";
            var route_input = document.getElementById("route_number"); 
            $.getJSON( "/autocomp" + "?format=json&route="+to_input, function(route_data) {

               _.forEach(route_data.results, function(routeNames){

                routeOption += "option value=\"" + routeNames.route + "\"></option>";


                });

                $('#route_list').append(routeOption);

            }).done(function(){
                console.log("got autosuggest route data");
            }).fail(function(){
                alert("failed route autosuggest");
            }).always(function(){
                //
            });
    }