var table = document.getElementById("resultsSecondaryTable");
var mainSearchTitle = document.getElementById("resultsMainSearchTitle");
var mainSearchArtist = document.getElementById("resultsMainSearchArtist");
var mainSearchLyrics = document.getElementById("resultsMainSearchLyrics");
var data = document.getElementById("filteredResultsList").getAttribute("data-filtered");
var lyrics = new Array();
var data2 = data.replace(/'/g, '"');
if (data2.length > 0)
    var jsonObj = $.parseJSON(data2);

//Order jsonObj by match percentage code here;

for(var i = 0; i < jsonObj.length; i++) {

    var obj = jsonObj[i];
    console.log(obj);
    //Main Search in main view
    if (i == 0) {
        mainSearchTitle.textContent = obj.title;
        mainSearchArtist.textContent = obj.artist;
    }
    lyrics.push(obj);
    //Secondary searches in table
    var row = table.insertRow(-1);
    var titleCell = row.insertCell(0);
    var artistCell = row.insertCell(1);
    var percentageMatchCell = row.insertCell(2);
    var sampleAudioLinkCell = row.insertCell(3);
    titleCell.innerHTML = obj.title;
    artistCell.innerHTML = obj.artist;
    percentageMatchCell.innerHTML = "N/A"
    sampleAudioLinkCell.innerHTML = `
    <audio controls="controls">
        <source src="${obj.spotifyPreview}" type="audio/mpeg"/>
    </audio>`;
    
}

        /*    $.ajax({
                url: '/lyrics',
                type : 'post',
                contentType: 'application/json',
                dataType : 'json',
                data : JSON.stringify(lyrics) //passing the variable
            }).done(function(result) {
                console.log("success: " + JSON.stringify(result[0].title));
                console.log("success: " + JSON.stringify(result[0].artist));
            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.log("fail: ",textStatus, errorThrown);
            });*/
