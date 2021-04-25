//-----------------------------------
// JS code for listening for table row selction
// - will also make ajax calls to possibly the Spotify API upon table selection to change main contents
//----------------------------------

//Instantiate all the variables
var currentRow                      = null;
var currentRowDetails               = null;
var currentSongPattern              = null;
var currentTimeStamp                = null;

var selectedResultTitle             = null;
var selectedResultArtist            = null;
var selectedResultMatchPercent      = null;
var selectedResultLyrics            = null; 
var selectedResultTapCount          = null; 
var selectedResultSpotifyEmbed      = null;
var selectedResultSpotifyTrackURI   = null;
var selectedResultSpotifyTimeStamp  = null;
var selectedResultImage             = null;

var playSongPatternButton           = null;
var playUserPatternButton           = null;
var userPatternArray                = null;

//Canvas Variables
var canvas                          = null;
var darkModeSwitch                  = null;
const barWidth = 6;
const barGutter = 7;
var barColorMute = "#878787";
var barColor = "#3b3a3a";
const barColorStart = "#f70000";
const barColorLatest = "#E06666";
const barColorEnd = "#00c92c";
let bars = [];
let width = 0;
let height = 0;
let halfHeight = 0;
let drawing = false;
let isRecording = false;
var beatCount = 0;


$( document ).ready(function() {
    //Grab all the document elements
    canvas                          = document.getElementById("js-canvas");
    
    selectedResultTitle             = document.getElementById("selectedResultTitle");
    selectedResultArtist            = document.getElementById("selectedResultArtist");
    selectedResultSpotifyEmbed      = document.getElementById("selectedResultSpotifyEmbed");
    selectedResultSpotifyTimeStamp  = document.getElementById("songPatternTimestamp");
    selectedResultTapCount          = document.getElementById("selectedResultTapCount");
    selectedResultLyrics            = document.getElementById("selectedResultLyrics"); 
    selectedResultImage             = document.getElementById("selectedResultImage");
    
    playSongPatternButton           = document.getElementById("playSongPatternButton");
    playUserPatternButton           = document.getElementById("playUserPatternButton");
    userPatternArray                = JSON.parse(document.getElementById("userTaps").getAttribute('data-user-taps'));
    
    //Make the first clickable-row active and set the variables
    $(".clickable-row").first().addClass('active');

    currentRow = $(".clickable-row").first();
    currentRowDetails = currentRow.children();
    currentSongPattern = JSON.parse(currentRow.attr('data-song-pattern'));

    //Format the initial Lyrics
    var lyrics = selectedResultLyrics.innerHTML;
    lyrics = lyrics.replace(/(?:\r\n|\r|\n)/g, '<br>');
    selectedResultLyrics.innerHTML  = lyrics;

    //Update the initial Progress Bar Match %
    setTimeout(() => {
        document.getElementById("progressBar").style.width = parseInt(currentRowDetails[2].innerHTML) + "%"
    }, 700);

    //Update the timestamp [[TODO Update the Spotify URI, Album Photo, iframeEmbed]]
    console.log("Timestamp" + currentRow.attr('data-song-timestamp'));
    currentTimeStamp = getTimeStampAndFormat(currentRow.attr('data-song-timestamp'));
    selectedResultSpotifyTimeStamp.innerHTML = currentTimeStamp;
    selectedResultSpotifyTrackURI =  document.getElementById("spotifyURI").getAttribute('data-spotify-URI') + '#' + currentTimeStamp;

    
    //Listening for Table Row Selection
    $('#resultsSecondaryTableBody').on('click', '.clickable-row', function(event) {
        //1. Hightlight selected Row
        currentRow = $(this);
        $(this).addClass('active').siblings().removeClass('active');

        //2. Retrieve the Song, Title, Match Percentage
        currentRowDetails = currentRow.children();

        //3. Retrieve the Song Pattern and store it to array
        currentSongPattern = JSON.parse(currentRow.attr('data-song-pattern'));
        console.log("Initial Song Pattern:")
        console.log(currentSongPattern)

        //4. Call Spotify API and get Embed Url/TrackURI/Album Photo
        getSpotifyMetadata(currentRowDetails[0].innerHTML , currentRowDetails[1].innerHTML )

        document.getElementById("progressBar").style.width = "0%"

    });


    function getSpotifyMetadata(title,artist) {
        var js_data = [title,artist]
        $.ajax({
            url: '/spotify-track-metadata',
            type: 'post',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(js_data)
        }).done(function (result) {
            console.log("success: " + JSON.stringify(result));
            console.log(result.data);

            //Set the selected title, artist, matchpercentage to the row after success
            selectedResultTitle.innerHTML           = currentRowDetails[0].innerHTML;
            selectedResultArtist.innerHTML          = currentRowDetails[1].innerHTML + '<span style="float:right;">' + currentRowDetails[2].innerHTML + '</span>';
            document.getElementById("progressBar").style.width = parseInt(currentRowDetails[2].innerHTML) + "%"
            selectedResultTapCount.innerHTML        = currentSongPattern.length;

            //Set the spotify uri with timestamp link
            console.log("Timestamp" + currentRow.attr('data-song-timestamp'));
            currentTimeStamp = getTimeStampAndFormat(currentRow.attr('data-song-timestamp'));
            selectedResultSpotifyTimeStamp.innerHTML = currentTimeStamp;
         
            //Set the Embed Link for iframe
            var spotifyUrlHead = "https://open.spotify.com";
            var spotifyUrlTail =  result.data[0].substring(spotifyUrlHead.length)
            selectedResultSpotifyEmbed.src  = spotifyUrlHead + "/embed" + spotifyUrlTail;

            //Set the TrackURI, Lyrics, Album Image Src
            selectedResultSpotifyTrackURI = result.data[1] + "#" + currentTimeStamp;

            var lyrics = result.data[2];
            lyrics = lyrics.replace(/(?:\r\n|\r|\n)/g, '<br>');
            selectedResultLyrics.innerHTML  = lyrics

            if (result.data[3] != '')
                selectedResultImage.src         = result.data[3]["url"];
            else 
                selectedResultImage.src         = "https://www.dia.org/sites/default/files/No_Img_Avail.jpg";

        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log("fail: ", textStatus, errorThrown);
        });
    }

    //Play the Song Pattern of the current row selected
    function playSound(currentSongPattern) {
        var sound = document.getElementById("percussion");
        isPlayback = true;
        isRecording = true; //start the Canvas Recording
        beatCount = 0;
        bars.push(30);
        bars.push(30);
        for (var i = 0; (i < currentSongPattern.length) && isPlayback; i++) {
            var millisecondsTime = (currentSongPattern[i]) * 1000;
            setTimeout(() => {
                var audio = document.createElement('audio');
                audio.src = sound.src;
                audio.volume = 0.3;
                document.body.appendChild(audio);
                
                bars.pop()
                bars.pop()
                bars.pop()
                bars.push(10)
                bars.push(20)
                bars.push(10)
                beatCount++;
                audio.play();
                audio.onended = function () {
                    this.parentNode.removeChild(this);
                }
            }, millisecondsTime);
        }
        
        //Stop the recording after the last beat taps
        var millisecondsTime = (currentSongPattern[currentSongPattern.length-1]) * 1000 + 700;
        setTimeout(() => {
            bars.push(29);
            bars.push(29);
            if (bars.length <= Math.floor(width / (barWidth + barGutter))) {
                renderBars(bars);
            } else {
                renderBars(bars.slice(bars.length - Math.floor(width / (barWidth + barGutter))), bars.length);
            }
            isPlayback = false;
            isRecording = false;
        }, millisecondsTime);
            
        
    }

    /************************************************************************/
    function getTimeStampAndFormat(pattern){
        //Return the first timestamp and format it in mm:ss
        var timestamp = parseInt(pattern)
        var minutes = Math.floor(timestamp / 60);
        var seconds = parseInt(timestamp % 60);
        if (minutes < 10) {minutes = "0"+minutes;}
        if (seconds < 10) {seconds = "0"+seconds;}
        return minutes + ":" + seconds
    }
    function adjustArray(pattern){
        //adjust array times so that the first item does not count and all following items are subtracted from the first timestamp

        var newArray = new Array();
        var dif = pattern[0];
        for(var i = 0; i < pattern.length; i++){
            var num = pattern[i] - dif + 1; //add 1 second for start playback
            newArray[i] = parseFloat(num.toFixed(3));
        }//end of for
        return newArray;
    }//end of returnTimes


    //----------------------------
    //METHODS FOR VISUALIZER
    //----------------------------
    // Start recording
    const startRecording = (pattern) => {
        var times = adjustArray(pattern);
        playSound(times);
    }  

    // Stop recording
    const stopRecording = () => {
        isRecording = false;
        isPlayback = false;
        bars.push(29);
        bars.push(29);
        if (bars.length <= Math.floor(width / (barWidth + barGutter))) {
            renderBars(bars);
        } else {
            renderBars(bars.slice(bars.length - Math.floor(width / (barWidth + barGutter))), bars.length);
        }
    }

    // Setup the canvas 
    const setupWaveform = () => {
        canvasContext = canvas.getContext('2d');

        width = canvas.offsetWidth;
        height = canvas.offsetHeight;
        halfHeight = canvas.offsetHeight / 2;

        canvasContext.canvas.width = width;
        canvasContext.canvas.height = height;

        setInterval(processInput, 70);
    }

    // Process the bars, push 1.5 to represent no input
    //[TODO] Might make it more responsive, right now popping 3 last elements if a tap has bee made
    //could make it so that it renders one at a time so there is no choppy animations
    const processInput = canvasProcessingEvent => {
        if (isRecording) {
            bars.push(1.5);

            if (bars.length <= Math.floor(width / (barWidth + barGutter))) {
                renderBars(bars);
            } else {
                renderBars(bars.slice(bars.length - Math.floor(width / (barWidth + barGutter))), bars.length);
            }

        } else {
            bars = [];
            beatCount = 0;
        }
    }

    // Render the bars
    const renderBars = bars => {
        if (!drawing) {
            drawing = true;

            window.requestAnimationFrame(() => {
            canvasContext.clearRect(0, 0, width, height);

            bars.forEach((bar, index) => {
                if (bar <= 5) {
                    if ((bars.length - index) == 1 ) {
                        bar = 0;
                    }
                    canvasContext.fillStyle = barColorMute;
                }
                else if (bar >= 30) {
                    canvasContext.fillStyle = barColorStart;
                }
                else if (bar == 29) {
                    canvasContext.fillStyle = barColorEnd;
                }
                else {
                    let counter = "BEAT COUNT - " + beatCount;
                    canvasContext.font = "bold 24px Arial";
                    canvasContext.fillStyle = barColor;
                    canvasContext.fillText(counter, canvas.width/20, canvas.height/10);
                }

                if (isPlayback) {
                    var latestBars = (bars.length - index) <= 5 && (bars.length - index) >= 3;
                    if (latestBars) {
                        canvasContext.fillStyle = barColorLatest;
                    }
                }

                canvasContext.fillRect((index * (barWidth + barGutter)), halfHeight, barWidth, (halfHeight * (bar / 100)));
                canvasContext.fillRect((index * (barWidth + barGutter)), (halfHeight - (halfHeight * (bar / 100))), barWidth, (halfHeight * (bar / 100)));
            });

                drawing = false;
            });
        }
    }
    
    // Start the application
    setupWaveform();
    
    // Add event listeners to the buttons
    playSongPatternButton.onclick = function () {startRecording(currentSongPattern);}
    playUserPatternButton.onclick = function () {startRecording(userPatternArray);  }

    var coll = document.getElementById("collapsible");
    coll.addEventListener("click", function() {
        this.classList.toggle("active");
        var content = document.getElementById("collapsibleContent");
        if (content.style.maxHeight){
        content.style.maxHeight = null;
        } else {
        content.style.maxHeight = content.scrollHeight + "px";
        } 
    });

    document.getElementById("selectedResultSpotifyTrackURI").onclick = function() {
        window.open(
            selectedResultSpotifyTrackURI
        );
        return false;
    };

    
      
});