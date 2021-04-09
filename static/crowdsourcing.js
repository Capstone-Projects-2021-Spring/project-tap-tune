$('#sendSourceButton').on('click', function(e){
    var title = document.getElementById("song_title").value;
    var artist = document.getElementById("song_artist").value;
    var url = document.getElementById("song_link").value;
    var file = document.getElementById("song_file").value;

    var titleError = document.getElementById("song_title_help");
    var artistError = document.getElementById("song_artist_help");
    var urlError = document.getElementById("song_link_help");

    //Verify the required fields
    if (!title) {
        titleError.textContent = "Please enter a song title before submitting.";
        return;
    }
    else {
        titleError.textContent = "";
    } 

    if (!artist) {
        artistError.textContent = "Please enter a song artist before submitting.";
        return;
    } 
    else {
        artistError.textContent = "";
    } 

    console.log(file);
    if (!file && (!url || !(isValidHttpUrl(url)))) {
        // urlError.textContent = "Please enter a valid YouTube Link to the song before submitting.";
        urlError.textContent = "Please enter a valid YouTube Link or song file before submitting.";
        return;
    }
    else {
        urlError.textContent = "";
    } 
    
    //[TODO?] Insert Code here to verify that the song title and song artist is able to be found through Spotify API?


    //AJAX call to /source to add user's song to database
    // var js_data = [title, artist, url];
    // console.log(js_data)
    // //[TODO] Add Ajax Loading Icon Animation next to button here
    // $.ajax({
    //     url: '/source',
    //     type : 'post',
    //     contentType: 'application/json',
    //     dataType : 'json',
    //     data : JSON.stringify(js_data)
    // }).done(function(result) {
    //     console.log("success: " + JSON.stringify(result));
    //     $('#sourcingModalSongResponse').modal();
    //
    // }).fail(function(jqXHR, textStatus, errorThrown) {
    //     console.log("fail: ",textStatus, errorThrown);
    // });

    //AJAX call to /source to add user's song to database
    var js_data = [title, artist, url];
    var js_data2 = [title, artist, file];
    console.log(js_data);
    console.log(js_data2);
    //[TODO] Add Ajax Loading Icon Animation next to button here
    if (url) {
        console.log(js_data)
        $.ajax({
            url: '/source',
            type: 'post',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(js_data)
        }).done(function (result) {
            console.log("success: " + JSON.stringify(result));
            $('#sourcingModalSongResponse').modal();

        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log("fail: ", textStatus, errorThrown);
        });
    } else {
        $.ajax({
            url: '/fileSource',
            type: 'post',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(js_data2)
        }).done(function (result) {
            console.log("success: " + JSON.stringify(result));
            $('#sourcingModalSongResponse').modal();

        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log("fail: ", textStatus, errorThrown);
        });
    }


});

function isValidHttpUrl(string) {
    let url;
    
    try {
      url = new URL(string);
    } catch (_) {
      return false;  
    }
  
    return url.protocol === "http:" || url.protocol === "https:";
  }