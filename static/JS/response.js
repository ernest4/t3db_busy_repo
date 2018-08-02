$( window ).on( "load", function() {


    //_________________________________________ONTHEGO
    $( "#onthego_form" ).on('submit', function(event){
        event.preventDefault();
        console.log("onthego_form: submitted!"); //DEBUGGING

        createResponseOnTheGo();
    });

    function createResponseOnTheGo(){
        console.log("onthego_form: requesting response from back end..."); //DEBUGGING

        $.ajax({
            url: "/onthego/formdata",
            type: "GET",
            data: { busnum_var : $('#bus_number').val(),
                    from_var : $('#location_from').val(),
                    to_var : $('#location_to').val() },

            success: function(response) {
                console.log("onthego_form: submission responded with success..."); //DEBUGGING

                document.getElementById('response').innerHTML = response; //more efficient than using jQuery equivalent...
                document.getElementById('response').scrollIntoView();
            },

            error: function(xhr, errmsg, err) {
                console.log("onthego_form: submission responded with error..."); //DEBUGGING
                console.log("onthego_form: "+ xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
                console.log("onthego_form: Error msg: "+errmsg); // provide a bit more info about the error to the console
            }
        });
    }

    //_________________________________________PLANNER

    $( "#planner_form" ).on('submit', function(event){
        event.preventDefault();
        console.log("planner_form: submitted!"); //DEBUGGING

        createResponsePlanner();
    });

    function createResponsePlanner(){
        console.log("planner_form: requesting response from back end..."); //DEBUGGING

        $.ajax({
            url: "/planner/formdata",
            type: "GET",
            data: { busnum_var : $('#bus_number').val(),
                    from_var : $('#location_from').val(),
                    to_var : $('#location_to').val(),
                    date_var : $('#datepicker').val(),
                    time_var : $('#clockpicker').val() },

            success: function(response) {
                console.log("planner_form: submission responded with success..."); //DEBUGGING

                document.getElementById('response').innerHTML = response; //more efficient than using jQuery equivalent...
                document.getElementById('response').scrollIntoView();
            },

            error: function(xhr, errmsg, err) {
                console.log("planner_form: submission responded with error..."); //DEBUGGING
                console.log("planner_form: "+ xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
                console.log("planner_form: Error msg: "+errmsg); // provide a bit more info about the error to the console
            }
        });
    }

    //_________________________________________EXPLORER

    $( "#explorer_form" ).on('submit', function(event){
        event.preventDefault();
        console.log("explorer_form: submitted!"); //DEBUGGING

        createResponsePlanner();
    });

    function createResponsePlanner(){
        console.log("explorer_form: requesting response from back end..."); //DEBUGGING

        $.ajax({
            url: "/tourist/formdata",
            type: "GET",
            data: { busnum_var : $('#bus_number').val(),
                    from_var : $('#location_from').val(),
                    to_var : $('#location_to').val(),
                    date_var : $('#datepicker').val(),
                    time_var : $('#clockpicker').val() },

            success: function(response) {
                console.log("explorer_form: submission responded with success..."); //DEBUGGING

                document.getElementById('response').innerHTML = response; //more efficient than using jQuery equivalent...
                document.getElementById('response').scrollIntoView();
            },

            error: function(xhr, errmsg, err) {
                console.log("explorer_form: submission responded with error..."); //DEBUGGING
                console.log("explorer_form: "+ xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
                console.log("explorer_form: Error msg: "+errmsg); // provide a bit more info about the error to the console
            }
        });
    }

});