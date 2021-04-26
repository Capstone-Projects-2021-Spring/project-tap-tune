$( document ).ready(function() {
    //spotifySuggest();
    $(document).on("click", "a", function() {
        var currentId = $(this).attr('id')

        //If the a element is for the add to Spotify feature
        if (currentId === "songLogLink") {

            let idIndex = $(this).attr('data-index')
            console.log(idIndex);
            
            let currentTitle = document.getElementById("songLogTitle" + idIndex).innerText;
            let currentArtist = document.getElementById("songLogArtist" + idIndex).innerText;
            let currentIcon = document.getElementById("songLogIcon" + idIndex)
            let songId = $(this).attr('data-song-id')
            let container = $(this);

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

        else if (currentId === "songDeleteLink")
        {
            let container = $(this).parent().parent();
            console.log ("I'm here in the else")
            var currentSongID = $(this).attr('data-song-id')
            console.log(currentSongID)

            let js_data = [currentSongID];

            console.log(js_data)
            $.ajax({
                url: '/remove-user-song-history',
                type: 'post',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(js_data),
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
            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.log("fail: ", textStatus, errorThrown);
            });
        }

        else if (currentId === "songDeleteFav")
        {
            let container = $(this).parent().parent();
            console.log ("I'm here in the else else")
            console.log(container)
            var currentSongID = $(this).attr('data-song-id')
            var songTitle = $(this).attr('data-title')
            var songArtist = $(this).attr('data-artist')


            console.log(currentSongID)

            let js_data = [songTitle, songArtist, currentSongID];

            console.log(js_data)
            $.ajax({
                url: '/remove-user-fav-spotify',
                type: 'post',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(js_data),
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
            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.log("fail: ", textStatus, errorThrown);
            });
        }

    });

    $('#suggestSpotifySongBtn').on('click', function(e){
        spotifySuggest();
    });

    function spotifySuggest() {
        var checkboxes = document.querySelectorAll('[data-track]');
        // var suggestedTitle = document.getElementById("suggestedTitle");
        // //var suggestedImage = document.getElementById("suggestedImage");
        var suggestedImageLink = document.getElementById("suggestframe");
        // var suggestedArtist = document.getElementById("suggestedArtist");
        
        //Sliders
        var sliders = document.querySelectorAll('span.value');
        var js_slider_data = [];
        for (var i = 0; i < sliders.length; i++) {
            var slider_item = sliders[i];
            js_slider_data.push(slider_item.innerHTML);
        }

        var tracks = [];
        for (var i = 0; i < checkboxes.length; i++) {
            var item = checkboxes[i];
            if (item.checked) {
                if (tracks.length < 5) {

                    tracks.push(item.getAttribute('data-track'));
                    console.log(item.getAttribute('data-track'));
                }
            }
        }
        var js_data = new Array();
        js_data.push(tracks);
        js_data.push(js_slider_data);
        console.log(js_data)
        $.ajax({
            url: '/spotify-suggest',
            type: 'post',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(js_data)
        }).done(function (result) {
            console.log("success: " + JSON.stringify(result));
            console.log(result.data);
            //suggestedTitle.innerText = result.data[0];
            //suggestedArtist.innerText = result.data[1];
            //suggestedImage.src = result.data[2]['url'];
            var spotifyUrlHead = "https://open.spotify.com";
            var spotifyUrlTail =  result.data[3].substring(spotifyUrlHead.length)
            console.log(spotifyUrlHead + "/embed" + spotifyUrlTail);
            suggestedImageLink.src = spotifyUrlHead + "/embed" + spotifyUrlTail;
            //suggestedImageLink.contentWindow.location.reload(true);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log("fail: ", textStatus, errorThrown);
        });
    }


});