var table = document.getElementById("resultsSecondaryTable");
var mainSearchTitle = document.getElementById("resultsMainSearchTitle");
var mainSearchArtist = document.getElementById("resultsMainSearchArtist");
var data = document.getElementById("filteredResultsList").getAttribute("data-filtered");
var data2 = data.replace(/'/g, '"');
var jsonObj = $.parseJSON(data2);

//Order jsonObj by match percentage code here;

for(var i = 0; i < jsonObj.length; i++) {
    var obj = jsonObj[i];
    console.log(obj);
    var row = table.insertRow(-1);
    var titleCell = row.insertCell(0);
    var artistCell = row.insertCell(1);
    var percentageMatchCell = row.insertCell(2);
    var sampleAudioLinkCell = row.insertCell(3);
    titleCell.innerHTML = obj.title;
    artistCell.innerHTML = obj.artist;
    //percentageMatchCell.innerHTML = obj.title; "in development" text placeholder for now?
    sampleAudioLinkCell.innerHTML = obj.artist;
    
}
