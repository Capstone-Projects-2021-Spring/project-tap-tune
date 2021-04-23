//-----------------------------------
// JS code for listening for table row selction
// - will also make ajax calls to possibly the Spotify API upon table selection to change main contents
//----------------------------------

//Instantiate all the variables
var currentRow                      = null;
var currentSongPattern              = null;

var selectedResultTitle             = null;
var selectedResultArtist            = null;
var selectedResultMatchPercent      = null;
var selectedResultLyrics            = null; 
var selectedResultSpotifyEmbed      = null;
var selectedResultSpotifyTrackURI   = null;
var selectedResultImage             = null;

var playUserPatternButton           = null;
var playSongPatternButton           = null;
var stopCanvasPlaybackButton        = null;

//Canvas Variables
var canvas                          = null;
var darkModeSwitch                  = null;
const barWidth = 6;
const barGutter = 7;
var barColorMute = "#878787";
var barColor = "#3b3a3a";
const barColorStart = "#f70000";
const barColorEnd = "#00c92c";
let bars = [];
let width = 0;
let height = 0;
let halfHeight = 0;
let drawing = false;
let isRecording = false;


$( document ).ready(function() {
    //Make the first clickable-row active
    $(".clickable-row").first().addClass('active');

    //Grab all the document elements
    canvas                          = document.getElementById("js-canvas");

    selectedResultTitle             = document.getElementById("selectedResultTitle");
    selectedResultArtist            = document.getElementById("selectedResultArtist");
    selectedResultSpotifyEmbed      = document.getElementById("selectedResultSpotifyEmbed");
    selectedResultSpotifyTrackURI   = document.getElementById("selectedResultSpotifyTrackURI");
    //selectedResultLyrics            = document.getElementById("selectedResultLyrics"); 
    selectedResultImage             = document.getElementById("selectedResultImage");

    playUserPatternButton           = document.getElementById("playUserPatternButton");
    playSongPatternButton           = document.getElementById("playSongPatternButton");
    stopCanvasPlaybackButton        = document.getElementById("stopCanvasPlaybackButton");

    //Listening for Table Row Selection
    $('#resultsSecondaryTableBody').on('click', '.clickable-row', function(event) {
        //1. Hightlight selected Row
        currentRow = $(this);
        console.log(currentRow)
        $(this).addClass('active').siblings().removeClass('active');

        //2. Populate the Song, Title, Match Percentage
        var currentRowDetails = currentRow.children();
        selectedResultTitle.innerHTML           = currentRowDetails[0].innerHTML;
        selectedResultArtist.innerHTML          = currentRowDetails[1].innerHTML + '<span style="float:right;">' + currentRowDetails[2].innerHTML + '</span>';
     
        //3. Call Spotify API and get Embed Url/TrackURI/Album Photo
        //getSpotifyMetadata(selectedResultTitle.innerHTML , selectedResultArtist.innerHTML )

        //4. Retrieve the Song Pattern and store it to array
        currentSongPattern = currentRow.attr('data-song-pattern');

        //Using the Song Pattern, preview the Canvas Element with the beginning Array
        //[TODO]  Do this after the playback visualizer feature 
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
            //0 trackLink, 1 trackURI,  2lyrics,  3trackAlbumImage
            var spotifyUrlHead = "https://open.spotify.com";
            var spotifyUrlTail =  result.data[0].substring(spotifyUrlHead.length)
            console.log(spotifyUrlHead + "/embed" + spotifyUrlTail);
            selectedResultSpotifyEmbed.src  = spotifyUrlHead + "/embed" + spotifyUrlTail;
            //selectedResultSpotifyTrackURI   = result.data[1]
            var lyrics = result.data[2];
            lyrics = lyrics.replace(/(?:\r\n|\r|\n)/g, '<br>');
            selectedResultLyrics.innerHTML  = lyrics
            selectedResultImage.src         = result.data[3]["url"]

        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log("fail: ", textStatus, errorThrown);
        });
    }

    //Play the Song Pattern of the current row selected
    function playSound(times) {
        var sound = document.getElementById("percussion");

        for (var i = 0; i < times.length; i++) {
            var millisecondsTime = (times[i]/(multiplierValue)) * 1000;
            setTimeout(() => {
                var audio = document.createElement('audio');
                audio.src = sound.src;
                audio.volume = 0.3;
                document.body.appendChild(audio);
                audio.play();
                audio.onended = function () {
                    this.parentNode.removeChild(this);
                }
            }, millisecondsTime);
        }
    }


    //----------------------------
    //METHODS FOR VISUALIZER
    //----------------------------
    // Start recording
    const startUserRecording = () => {
        playSound(times)
        //change the visualizer color
        switch (recordingType.innerHTML) {
            case "Percussion":
                barColorMute = "#5cb6ff";
                barColor = "#249dff";
                break;
            case "Harmonic":
                barColorMute = "#e0a35c";
                barColor = "#e67b00";
                break;
            default:
                if (darkModeSwitch.checked) {
                    barColorMute = "#302f2d";
                    barColor = "#242423";
                }
                else {
                    barColorMute = "#878787";
                    barColor = "#3b3a3a";
                }
                break;
            }
        isRecording = true;
    } 
    
    const startSongRecording = () => {
        //change the visualizer color
        switch (recordingType.innerHTML) {
            case "Percussion":
                barColorMute = "#5cb6ff";
                barColor = "#249dff";
                break;
            case "Harmonic":
                barColorMute = "#e0a35c";
                barColor = "#e67b00";
                break;
            default:
                if (darkModeSwitch.checked) {
                    barColorMute = "#302f2d";
                    barColor = "#242423";
                }
                else {
                    barColorMute = "#878787";
                    barColor = "#3b3a3a";
                }
                break;
            }
        isRecording = true;
    } 

    // Stop recording
    const stopRecording = () => {
        if (finishButton.innerHTML != "Submit"){

            isRecording = false;
            bars.push(29);
            bars.push(29);
            
            if (bars.length <= Math.floor(width / (barWidth + barGutter))) {
                renderBars(bars);
            } else {
                renderBars(bars.slice(bars.length - Math.floor(width / (barWidth + barGutter))), bars.length);
            }
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
                    canvasContext.fillStyle = barColorMute;
                }
                else if (bar >= 30) {
                    canvasContext.fillStyle = barColorStart;
                }
                else if (bar == 29) {
                    canvasContext.fillStyle = barColorEnd;
                }
                else {
                    canvasContext.fillStyle = barColor;
                    let counter = "BEAT COUNT - " + beatCount;
                    canvasContext.font = "bold 24px Arial";
                    canvasContext.fillText(counter, canvas.width/20, canvas.height/10);
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
    playUserPatternButton       .addEventListener('mouseup', startUserRecording);
    stopCanvasPlaybackButton    .addEventListener('mouseup', stopRecording);

    $('#toggle-event').change(function() {
        var currentType = recordingType.innerHTML;
        console.log(currentType)
        if ($(this).prop('checked')) {
            //Change CSS to dark mode
            console.log("darkmode")
            canvas.className = "js-canvas waveform-canvas-dark";
            if (currentType != "Percussion" && currentType != "Harmonic") {
                barColorMute = "#302f2d";
                barColor = "#242423";
            }
        }
        else {
            //Change CSS to light mode
            canvas.className = "js-canvas waveform-canvas";
            if (currentType != "Percussion" && currentType != "Harmonic") {
                barColorMute = "#878787";
                barColor = "#3b3a3a";
            }
        }
    })

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
      
});