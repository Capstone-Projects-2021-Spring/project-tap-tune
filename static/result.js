function loadTableItems(list) {

    var table = document.getElementById("resultsSecondaryTable");
    var mainSearchTitle = document.getElementById("resultsMainSearchTitle");
    var mainSearchArtist = document.getElementById("resultsMainSearchArtist");


    for (item in list) {
        console.log(item.title);
        console.log(item.artist);
    }

}


