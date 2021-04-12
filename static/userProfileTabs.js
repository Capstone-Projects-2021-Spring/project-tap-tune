$(document).on("click", "a", function() {
    var currentId = $(this).attr('id')

    let idType = currentId.substring(0, currentId.length -1);

    //If the a element is for the add to Spotify feature
    if (idType === "songLogLink") {

        let idIndex = currentId.slice(-1);
        
        let currentTitle = document.getElementById("songLogTitle" + idIndex).innerText;
        let currentArtist = document.getElementById("songLogArtist" + idIndex).innerText;
        let currentIcon = document.getElementById("songLogIcon" + idIndex)
        let songId = $(this).attr('data-song-id')
        let container = $(this).parent();

        currentArtist = currentArtist.replace("Artist: ", "");

        console.log (currentTitle);
        console.log (currentArtist);

        let js_data = [currentTitle, currentArtist, songId];
        
        //$(this).find("i").toggleClass("fa-heart fa-heart-o");
        $.ajax({
            url: '/add-user-log-spotify',
            type : 'post',
            contentType: 'application/json',
            dataType : 'json',
            data : JSON.stringify(js_data), //passing the variable
            success: function ( data ){
                if ( !$.trim( data.feedback )) { // response from Flask is empty
                    toast_error_msg = "An empty response was returned.";
                    toast_category = "danger";
                }
                else { // response from Flask contains elements
                    toast_error_msg = data.feedback;
                    toast_category = data.category;
                    if( toast_category == 'success' ){
                        $(container).remove();
                    }
                }
            },
            error: function(xhr) {console.log("error. see details below.");
                console.log(xhr.status + ": " + xhr.responseText);
                toast_error_msg = "An error occured";
                toast_category = "danger";
            },
        }).done(function(result) {
            console.log("success: " + JSON.stringify(result));

            M.toast({html: toast_error_msg, classes: 'bg-' + toast_category + ' text-white'});
        });
    }

});

$('#suggestSpotifySongBtn').on('click', function(e){
    var checkboxes = document.querySelectorAll('[data-track]');
    var suggestedTitle = document.getElementById("suggestedTitle");
    var suggestedImage = document.getElementById("suggestedImage");
    var suggestedArtist = document.getElementById("suggestedArtist");

    console.log("suggest Button")
    var js_data = new Array();
    for (var i = 0; i < checkboxes.length; i++) {
        var item = checkboxes[i];
        if (item.checked) {
            if (js_data.length < 5) {

                js_data.push(item.getAttribute('data-track'));
                console.log(item.getAttribute('data-track'));
            }
        }
    }

    console.log(js_data)
    $.ajax({
        url: '/spotify-suggest',
        type: 'post',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify(js_data)
    }).done(function (result) {
        console.log("success: " + JSON.stringify(result));
        console.log(result.data)
        suggestedTitle.innerText = result.data[0];
        suggestedArtist.innerText = result.data[1];
        suggestedImage.src = result.data[2]['url'];
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.log("fail: ", textStatus, errorThrown);
    });
});