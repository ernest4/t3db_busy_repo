
// FUNCTION TO PROVIDE AUTOFILL ON LOCATION SEARCHES

function pred() {

                    var to_input = document.getElementById("location"); 
                    var xmlHttp = new XMLHttpRequest();
                    xmlHttp.open( "GET", "/autocomp"+"?format=json&stopname="+to_input+"&stopid="+to_input, false ); // false for synchronous request
                    xmlHttp.setRequestHeader("Content-Type", "application/json");
                    xmlHttp.send();
                    var response = xmlHttp.responseText;
                    var stop_list=[];
                    response.foreach(function(element){
                    stop_list.push(element.shortname+ ", " + element.stopid);


                    });

                    stop_list.foreach(function(element){

                        stopOption = "<option value=\"" + this + "\">" + this + "</option>";
                        $('#stop_list').append(stopOption);


                });

                }