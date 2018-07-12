
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
                  
                  
                  
function pred1(){
    
    
        var route_input = document.getElementById("route_number"); 
        $.getJSON( "/autocomp" + "?format=json&route="+to_input, function(route_data) {
            
           _.forEach(route_data.results, function(routeNames){
               
               routeOption = "option value=\"" + routeNames.route + "\"> 
               </option>;
             $('#route_list').append(routeOption);
                
            });
                 
        }).done(function(){
            console.log("got autosuggest route data");
        }).fail(function(){
            alert("failed route autosuggest");
        }).always(function(){
            //
        });
}
     
            
        
               
            
            
            
            
        }
    
    
    

}            

