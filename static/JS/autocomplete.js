
// FUNCTION TO PROVIDE AUTOFILL ON LOCATION SEARCHES

$( window ).on ("load", function () {});

function pred() {
        
        var to_input = document.getElementById("location"); 
        $.getJSON( "/autocomp" + "?format=json&stopname="+to_input, function(data) {
                
            _.forEach(data.results, function(busStops){
                
              stopOption = "<option value=\"" + busStops.stopid + "\">" + busStops.fullname + "</option>";
            $('#stop_list').append(stopOption);
                
            });
            
        }).done(function(){
            console.log("got autosuggest data");
        }).fail(function(){
            alert("failed autosuggest");
        }).always(function(){
            //
        });
}
                  
                  
                  
            

