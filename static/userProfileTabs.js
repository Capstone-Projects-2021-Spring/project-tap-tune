$(document).on("click", "a", function() {
    var currentId = $(this).attr('id')

    var idType = currentId.substring(0, currentId.length -1);

    //If the a element is for the add to Spotify feature
    if (idType == "songLogLink") {

        var idIndex = currentId.slice(-1);
        
        var currentTitle = document.getElementById("songLogTitle" + idIndex).innerText;
        var currentArtist = document.getElementById("songLogArtist" + idIndex).innerText;
        var currentIcon = document.getElementById("songLogIcon" + idIndex)

        var currentArtist = currentArtist.replace("Artist: ", "");

        console.log (currentTitle);
        console.log (currentArtist);

        var js_data = [currentTitle, currentArtist];
        
        //$(this).find("i").toggleClass("fa-heart fa-heart-o");
        $.ajax({
            url: '/add-user-log-spotify',
            type : 'post',
            contentType: 'application/json',
            dataType : 'json',
            data : JSON.stringify(js_data) //passing the variable
        }).done(function(result) {
            console.log("success: " + JSON.stringify(result));

            //return result;
            //$("#data").html(result);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.log("fail: ",textStatus, errorThrown);
        });

    }

});