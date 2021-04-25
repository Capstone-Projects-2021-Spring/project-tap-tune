$( document ).ready(function() { 
    //setup before functions
    var typingTimer;                //timer identifier
    var updateInterval;
    var doneTypingInterval = 3000;  //time in ms (3 seconds)
    var typingSearchMessageResult = document.getElementById("typingSearchMessageResult");

    //on keyup, start the countdown
    $('#song_artist').keyup(function(){
        clearTimeout(typingTimer);
        if ($('#song_title').val() && $('#song_artist').val()) {
            typingTimer = setTimeout(doneTyping, doneTypingInterval);
            typingSearchMessageResult.innerText = "Looking for song ";
            if (!updateInterval)
                updateInterval = setInterval(change, 400);
        }
    });

    $('#song_title').keyup(function(){
        clearTimeout(typingTimer);
        if ($('#song_title').val() && $('#song_artist').val()) {
            typingTimer = setTimeout(doneTyping, doneTypingInterval);
            typingSearchMessageResult.innerText = "Looking for song ";
            if (!updateInterval)
                updateInterval = setInterval(change, 400);
        }
    });

    function change() {
        if (!typingSearchMessageResult.innerText.includes(" . . ."))
            typingSearchMessageResult.innerText += " ."
        else 
            typingSearchMessageResult.innerText = "Looking for song"
    }

    //user is "finished typing," do something
    function doneTyping () {

        clearInterval(updateInterval)
        updateInterval = null;
        var js_data = [$('#song_title').val(), $('#song_artist').val()]
        $.ajax({
            url: '/search',
            type: 'post',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(js_data)
        }).done(function (result) {            
            //Show in Results Section Top Two Results
            if (result.data.length > 0) 
                typingSearchMessageResult.innerHTML = '<i class="fas fa-times" style="color: #ff1a1a"></i>' + " Song already exists in database.";
            else 
                typingSearchMessageResult.innerHTML = `<i class="fas fa-check" style="color: #00b300"></i>` + " Song not found in database.";
            
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log("fail: ", textStatus, errorThrown);
            typingSearchMessageResult.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: orange"></i>' + " Error looking into database.";
        });
    }


    /**
    class to store the artist, title, and file extension of the audio file
    used to pass a JSON string as filename for audio file
    JSON string to be parsed in backend to obtain aritst, title, and the file extension
    **/
    class file_upload_data{
        constructor(artist, title, ext){
            this.meta = {
                "artist" : artist,
                "title" : title,
                "ext" : ext
            }
        }
        getMeta(){
            return this.meta;
        }
    }

    $('#sendSourceButton').on('click', function(e){
        var title = document.getElementById("song_title").value;
        var artist = document.getElementById("song_artist").value;
        var url = document.getElementById("song_link").value;

        var outFile = document.getElementById("song_file").value;

        var outFile = document.getElementById("song_file").files[0];
        var button = document.getElementById("sendSourceButton").value;


        var titleError = document.getElementById("song_title_help");
        var artistError = document.getElementById("song_artist_help");
        var urlError = document.getElementById("song_link_help");
        $('#sourcingModalSongResponse').hide();



        console.log("SUBMIT BUTTON PRESSED")
        //console.log(outFile);
        //console.log(typeof(outFile));


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

        //console.log(file);
        if (!outFile && (!url || !(isValidHttpUrl(url)))) {
            // urlError.textContent = "Please enter a valid YouTube Link to the song before submitting.";
            urlError.textContent = "Please enter a valid YouTube Link or song file before submitting.";
            return;
        }
        else {
            urlError.textContent = "";
        } 
        
        //[TODO?] Insert Code here to verify that the song title and song artist is able to be found through Spotify API?

        //AJAX call to /source to add user's song to database
        var js_data = [title, artist, url];

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
        } else if (outFile) {
            console.log("FILE UPLOAD CONDITIONAL");

            // set fileData to pass back
            var fileData = new FormData();
            console.log(outFile["name"].split("."))
            last_ele = ((outFile["name"].split(".")).length) - 1;
            var  ext = outFile["name"].split(".")[last_ele];
            let upload_data = new file_upload_data(artist, title, ext);
            var filename = JSON.stringify(upload_data.getMeta());

            fileData.set('file', outFile, filename);
            console.log(typeof(fileData));
            console.log(outFile)
            console.log("AJAX CALL FOR FILE INITIATED");
            $.ajax({
                url: '/fileSource',
                type: 'post',
                contentType: false,
                processData: false,
                data: fileData
            }).done(function (result) {
                console.log("success: " + fileData);
                $('#sourcingModalSongResponse').modal();

            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.log("fail: ", textStatus, errorThrown);
            });
    //        });
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

    $('#searchDatabaseButton').on('click', function(e){ 
        var title = document.getElementById("searchTitle").value;
        var artist = document.getElementById("searchArtist").value;
        var resultParagraph = document.getElementById("searchResult");
        var resultsLabel = document.getElementById("searchResultLabel");

        //AJAX call to /search
        var js_data = [title, artist];
        console.log(js_data)
        if (title == '' && artist == '') {
            resultsLabel.innerHTML = "Result " + `<i class="fas fa-exclamation-triangle" style="color: orange"></i>`;
            resultParagraph.innerHTML = 'Provide title or artist before searching.';
        }
        else {
            $.ajax({
                url: '/search',
                type: 'post',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(js_data)
            }).done(function (result) {
                console.log("success: " +  JSON.stringify(result));
                console.log(result.data)
                
                //Show in Results Section Top Two Results
                if (result.data.length > 0) {
                    resultsLabel.innerHTML = "Result " + '<i class="far fa-check-circle" style="color: green"></i>'; 
                    resultParagraph.innerHTML = '';
                    
                    for (var i = 0; i < result.data.length; i ++) {
                        let song = result.data[i];
                        //add the song title and release Date
                        resultParagraph.innerHTML += resultRowHtml(song[0], song[1], song[2]);
                    }
                }
                else {
                    console.log("Cant find showing on results no found")
                    resultsLabel.innerHTML = "Result " + '<i class="fas fa-times" style="color: red"></i>'; 
                    resultParagraph.innerHTML = " No songs by that title and/or artist."
                } 
                
            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.log("fail: ", textStatus, errorThrown);
            });
        }
    });

    function resultRowHtml(title, artist, releaseDate) {
        if (releaseDate) {
            releaseDate = releaseDate.replace('00:00:00 GMT','');
        }
        var resultSongBase = `<span>
                                <span style="font-weight: bold;"> Title - </span>${title}<br>
                                <span style="font-weight: bold;"> Artist - </span>${artist}<br>
                                <span style="font-weight: bold;"> Release - </span>${releaseDate}<br>
                            </span> <br>`;
        
        return resultSongBase
    }

});