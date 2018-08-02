$( window ).on( "load", function() {

    $( "#onthego_form" ).on('submit', function(event){
        event.preventDefault();
        console.log("Form submitted!"); //DEBUGGING

        createResponse();
    });

    function createResponse(){
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
            },

            error: function(xhr, errmsg, err) {
                console.log("onthego_form: submission responded with error..."); //DEBUGGING
                console.log("onthego_form: "+ xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
                console.log("onthego_form: Error msg: "+errmsg); // provide a bit more info about the error to the console
            }
        });
    }

});