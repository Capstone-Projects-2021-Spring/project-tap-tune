$( document ).ready(function() {

    var selectedResultLyrics            = document.getElementById("selectedResultLyrics"); 
    var lyrics = selectedResultLyrics.innerHTML;
    lyrics = lyrics.replace(/(?:\r\n|\r|\n)/g, '<br>');
    selectedResultLyrics.innerHTML  = lyrics;
});