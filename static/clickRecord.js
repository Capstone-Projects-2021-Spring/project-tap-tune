//Variables for Recording
var startTime;
var instanceTime;
var times = new Array();
var timeJsonArray = [];
var dif;
var beatCount = 0;

let isRecording = false;
let isPlayback = false;
let isPlaying = false;

// Canvas variables
var canvas = null;
var darkModeSwitch = null;
const barWidth = 6;
const barGutter = 7;
var barColorMute = "#878787";
var barColor = "#3b3a3a";
const barColorStart = "#f70000";
const barColorLatest = "#E06666";
const barColorEnd = "#00c92c";
//const barColor2;
let bars = [];
let width = 0;
let height = 0;
let halfHeight = 0;
let drawing = false;

//More UI Elements
var cursorX = null;
let startButton = null;
let tapButton = null;
let stopButton = null;
let finishButton = null;
let playButton = null;
let recordingTypeDropdown = null;
let recordingKeyDropdown = null;
let recordingType = null;
let beatCountElement = null;
$( document ).ready(function() {

    // UI Elements
    canvas = document.getElementById("js-canvas");
    darkModeSwitch = document.getElementById("toggle-event");
    let canvasContext = canvas.getContext('2d');

    const playbackrate = document.querySelector('.speedcontrolcontainer input');
    tapButton = document.getElementById("tapScreenButton");
    startButton = document.getElementById("startRecordingBtn");
    resetButton = document.getElementById("resetRecordingBtn");
    finishButton = document.getElementById("finishRecordingBtn");
    playButton = document.getElementById("playRecordingBtn");
    recordingTypeDropdown = document.getElementById("recordingTypeDropdown");
    recordingKeyDropdown = document.getElementById("tapKeyDropdown");
    recordingType = document.getElementById("selected1");
    harmonicsKeyType = document.getElementById("selected2");
    beatCountElement = document.getElementById("counter-number");
    //recordingKey = document.getElementById("selected2");
    speedButton = document.getElementById("speedPlay");

    /*************************************************************************/
    startButton.onclick = function () {
        setButtonDisables(true);
        resetCounterStyle(1);
        playButton.disabled = true;

        //Canvas Animation + Ripple
        bars.push(30)
        bars.push(30)
        animateRipple("start")
        startTime = new Date();
        console.log(startTime);
    }//end of startButton

    resetButton.onclick = function () {
        //Reset HTML values and disables
        finishButton.innerHTML = "Stop";
        beatCountElement.innerHTML = 0;
        beatCount=0;
        playButton.disabled = true;
        setButtonDisables(false);
        resetCounterStyle(0);

        //Log the arrays that were recorded so far
        console.log("Time Reset");
        console.log("Stop: "+dif);
        console.log("END ARRAY: "+JSON.stringify(returnTimes()));

        //Reset the recording values
        times = new Array();
        timeJsonArray = [];
        startTime = null;
        
        //animation
        animateRipple("reset");

    }//end of stopButton

    /*************************************************************************/
    finishButton.onclick = function () {
        if (startTime){
            console.log("Time Stop");
            console.log("Stop: "+dif);
            console.log("END ARRAY: "+JSON.stringify(times));
            beatCountElement.disabled = true;
            playButton.disabled = false;
            startTime = null;
            if (beatCount < 5) {
                finishButton.disabled = true;
            }
        }


        if (finishButton.innerHTML == "Submit"){
            var js_data = JSON.stringify(returnTimes());
            var flask_url = '/rhythm';
            
            $.ajax({
                url: flask_url,
                type : 'post',
                contentType: 'application/json',
                dataType : 'json',
                data : js_data //passing the variable
            }).done(function(result) {
                console.log("success: " + JSON.stringify(result));
                document.querySelector('#rLoader').style.visibility = 'visible';
                goToFiltering();

                //return result;
                //$("#data").html(result);
            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.log("fail: ",textStatus, errorThrown);
            });

            //AJAX for multiplier
                var multiply = document.getElementById("speedMultipler").innerHTML;
                $.ajax({
                url: '/multiplier',
                type : 'post',
                contentType: 'application/json',
                dataType : 'json',
                data : multiply//passing the variable
            }).done(function(result) {
                console.log("success for multiplier: " + JSON.stringify(result));

            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.log("fail: ",textStatus, errorThrown);
            });
        }
        else {
            //animation
            animateRipple("finish");
            
            //change text class to be stagnat and confirm user submit 
            //Also enable playback button
            beatCountElement.disabled == true;
            finishButton.innerHTML = "Submit";
            playButton.disabled = false;
        }


    }//end of stopButton
    
    /*************************************************************************/
    window.addEventListener('mousedown', e => {
        if (beatCountElement.disabled == false) {
            if (startTime) {
                instanceTime = new Date();
                dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

                //Check If the mouse coordinates of x and y is less than the dimensions of stopButton inside
                // its CURRENT container of the event, then don't record or play a sound 
                let ButtonRect = finishButton.getBoundingClientRect();
                let heightDif = ButtonRect.bottom - ButtonRect.top;
                let widthDif = ButtonRect.right - ButtonRect.left;
                let widthBoolean = (e.offsetX > widthDif);
                let heightBoolean = (e.offsetY > heightDif);
                if (widthBoolean || heightBoolean) {
                    playSound(true);
                    beatCount+=1;
                    bars.pop()
                    bars.pop()
                    bars.pop()
                    bars.push(10)
                    bars.push(20)
                    bars.push(10)
                    times.push(dif);
                    console.log("TAP TIME: "+dif);
                    console.log(times);                  
                                    
                }
            }
        }
    });//end of tapButton
    /*************************************************************************/

    /************************************************************************/
    function returnTimes(){
        //General Recording Return
        var returnArray = [];
        var adjustedArray = adjustArray(times);
        times = adjustedArray;

        switch (recordingType.innerHTML) {
            case "Percussion":
                returnArray.push([1])
                break;
            case "Harmonic":
                returnArray.push([2])
                break;
            default:
                returnArray.push([0])
                break;
        }

        returnArray.push(adjustedArray);
        return returnArray;
    }//end of returnTimes

    /************************************************************************/
    function adjustArray(array){
        //adjust array times so that the first item does not count and all following items are subtracted from the first timestamp

        // if (recordingType.innerHTML == dynamicRecordType) { 
        //     var jsonArray = array;
        //     var dif = jsonArray[0].timestamp;
        //     for (var i = 0; i < jsonArray.length; i++) {
        //         var num = jsonArray[i].timestamp - dif;
        //         jsonArray[i].timestamp = parseFloat(num.toFixed(3));
        //     }
        //     //console.log("finished array " + timeJsonArray)
        //     //times = returnArray;
        //     return jsonArray;
        // }
        // else {

            var newArray = new Array();
            var dif = array[0];
            for(var i = 0; i < array.length; i++){
                var num = array[i] - dif;
                newArray[i] = parseFloat(num.toFixed(3));
            }//end of for
        // }
            
        return newArray;
    }//end of returnTimes
    
    
    document.addEventListener("keydown", function(){
        record();
    });

    /***************************************************************************/
    function record(){
        //82 is the r button
        if (beatCountElement.disabled == false) {
            if(event.keyCode >= 48 && event.keyCode <= 57){
                //console.log(startTime);
                playSound(true);
                instanceTime = new Date();
                dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

                beatCount+=1;
                bars.pop()
                bars.pop()
                bars.pop()
                bars.push(10)
                bars.push(20)
                bars.push(10)

                times.push(dif);
                console.log("TAP TIME: "+dif);
                console.log(times);
            }//end of if
        }//end of if
    }//end of record

    function animateRipple(button) {
        switch (button) {
            case "finish":
                var ButtonRect = finishButton.getBoundingClientRect();
                var animateColor = "md-click-animate-green";
                break;

            case "start":
                var ButtonRect = startButton.getBoundingClientRect();
                var animateColor = "md-click-animate-red";
                break;

            case "reset":
                var ButtonRect = resetButton.getBoundingClientRect();
                var animateColor = "md-click-animate-gray";
                break;
        
            default:
                break;
        }
        var element, circle, d, x, y;
        element = $("#tapScreenButton");
        if(element.find(".md-click-circle").length == 0) {
            element.prepend("<span class='md-click-circle'></span>");
        }
        circle = element.find(".md-click-circle");
        circle.removeClass("md-click-animate-red");
        circle.removeClass("md-click-animate-orange");
        circle.removeClass("md-click-animate-green");
        circle.removeClass("md-click-animate-gray");
        circle.removeClass("md-click-animate");
        if(!circle.height() && !circle.width()) {
            d = Math.max(element.outerWidth(), element.outerHeight());
            circle.css({height: d, width: d});
        }

        x = ((ButtonRect.right - ButtonRect.left) / 2) + ButtonRect.left - circle.width()/2;
        y = ((ButtonRect.bottom - ButtonRect.top) / 2) + ButtonRect.top - circle.height()/2;
        circle.css({top: y+'px', left: x+'px'}).addClass(animateColor);
    }

    function RGBToHex(r,g,b) {
        r = r.toString(16);
        g = g.toString(16);
        b = b.toString(16);

        if (r.length == 1)
          r = "0" + r;
        if (g.length == 1)
          g = "0" + g;
        if (b.length == 1)
          b = "0" + b;

        return "#" + r + g + b;
    }

    function getColor(e) {
        //well first of all are we even in button territory
        var startButtonRect = startButton.getBoundingClientRect();
        var incrementBeatCount = parseInt(beatCountElement.innerHTML);

        if (finishButton.innerHTML == "Submit") return -1;
        if (e.pageY > startButtonRect.top && e.pageY < startButtonRect.bottom) {
            if (e.pageX > startButtonRect.left) {
                if (e.pageX < startButtonRect.right && incrementBeatCount == 0) { //red
                    if (incrementBeatCount == 0)
                        return 1;
                }
            }
        }
        return 0;
    }
    
    $('#recordingTypeDropdown a').click(function(){
        var selected = $(this).text();
        $('#selected1').text(selected);
    });

    $('#recordingKeyDropdown a').click(function(){
        $('#selected2').text($(this).text());
    });

    /***************************************************************************/
    //Update Mouse Position for Recording both Percussion and Harmonics feature.
    document.addEventListener('mousemove', onMouseUpdate, false);
    
    function onMouseUpdate(e) {
        cursorX = e.pageX;
        cursory = e.pageY;
    }

    function getRecordingTypeMouse() {
        var window_width = $(window).width();

        if (cursorX < (window_width/2)) {
            console.log("tapped on the left");
            return 0; //this is harmonics
        }
        else {
            console.log("tapped on the right");
            return 1; //This is percussion
        }
    }
    //end of mouse position related methods 
    /***************************************************************************/

    function setButtonDisables(boolean) {
        startButton.disabled                    = boolean;
        resetButton.disabled                    = !boolean;
        finishButton.disabled                   = !boolean;
        recordingTypeDropdown.disabled          = boolean;
        beatCountElement.disabled               = !boolean;
    }

    function resetCounterStyle(button) {
        if (button == 0) { //reset button
            beatCountElement.style.color = "#858585";
            beatCountElement.style.opacity = "0.5";
            beatCountElement.style.textShadow = "";
        }
        else if (button == 1) { //start button
            beatCountElement.style.opacity = "1";
            beatCountElement.style.color = "#FFFFFF"
        }
    }

    function playSound(single) {
        var recordingType = $('#selected1').text();
        var enableTapSound = true;
        // Make Playback sound a specific key
        //if (recordingType == dynamicRecordType) {
        var tapKey = $('#selected2').text();
        switch (tapKey) {
            case "C":
                var sound = document.getElementById("harmony1");
                break;
            case "D":
                var sound = document.getElementById("harmony2");
                break;
            case "E":
                var sound = document.getElementById("harmony3");
                break;
            case "F":
                var sound = document.getElementById("harmony4");
                break;    
            case "G":
                var sound = document.getElementById("harmony5");
                break;
            case "A":
                var sound = document.getElementById("harmony6");
                break;
            case "B":
                var sound = document.getElementById("harmony7");
                break;    
            case "Disable":
                var sound = document.getElementById("percussion");
                enableTapSound = false;
                break;
            default:
                var sound = document.getElementById("percussion");
                break;
        }
        if (single && enableTapSound) {
            var audio = document.createElement('audio');
            audio.src = sound.src;
            audio.volume = 0.3;
            document.body.appendChild(audio);
            audio.play();
            audio.onended = function () {
                this.parentNode.removeChild(this);
            }
        }
        else if (!single) {
            var multiplierValue = document.getElementById("speedMultipler").innerHTML;
            isPlayback = true;
            startRecording();
            beatCount = 0;
            bars.push(30);
            bars.push(30);
            for (var i = 0; i < times.length; i++) {
                var millisecondsTime = (times[i]/(multiplierValue)) * 1000;
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
            var millisecondsTime = (times[times.length-1]/(multiplierValue)) * 1000 + 700;
            setTimeout(() => {
                console.log("ending");
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
    }
        
    playButton.onclick = function () {
        playSound();
    }//end of play

    //get the multiplier value from the slider    
    playbackrate.addEventListener('change', e => {
        console.log("Multiplier "+playbackrate.value);
        document.getElementById("speedMultipler").innerHTML = playbackrate.value;
    });
    
    //----------------------------
    //METHODS FOR VISUALIZER
    //----------------------------
    // Start recording
    const startRecording = () => {
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

    // Reset recording
    const resetRecording = () => {
        isRecording = false;
        bars = [];
  
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
    startButton .addEventListener('mouseup', startRecording);
    resetButton .addEventListener('mouseup', resetRecording);
    finishButton.addEventListener('mouseup', stopRecording);

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
});