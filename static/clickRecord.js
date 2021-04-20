//Variables for Recording
var startTime;
var instanceTime;
var times = new Array();
var timeArray = [];
var timeJsonArray = [];
var dif;
var beatCount = 0;

let isRecording = false;
let isPlaying = false;

// Canvas variables
const barWidth = 6;
const barGutter = 7;
var barColorMute = "#878787";
var barColor = "#595959";
const barColorStart = "#f70000";
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
var dynamicRecordType = "Percussion + Harmonics";
$( document ).ready(function() {

    // UI Elements
    const canvas = document.querySelector('.js-canvas');
    let canvasContext = canvas.getContext('2d');

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
    }//end of startButton

    /*************************************************************************/
    tapButton.onclick = function () {
        if (beatCountElement.disabled == false) {
            if (startTime) {
                instanceTime = new Date();
                dif = (instanceTime.getTime() - startTime.getTime()) / 1000;
                beatCount+=1;
                playSound(true);
                bars.pop()
                bars.pop()
                bars.pop()
                bars.push(10)
                bars.push(20)
                bars.push(10)
                //Recording Type is HarmonicLeft/PercussionRight
                // if (recordingType.innerHTML == dynamicRecordType) {
                //     var recordingTapType = getRecordingTypeMouse();
                //     if (recordingTapType == 0) {
                //         //this is harmonics
                //         timeJsonArray.push({type: recordingTapType, timestamp: dif})
                //     }
                //     else if (recordingTapType == 1) {
                //         //this is percussion
                //         timeJsonArray.push({type: recordingTapType, timestamp: dif})
                //     }
                //     console.log("TAP TIME: " + dif);
                //     console.log(timeJsonArray);
                // }

                //Recording Type is General 
                // else {
                    //do general rhythm recording
                times.push(dif);
                console.log("TAP TIME: "+dif);
                console.log(times); 
                // }

            }
            else { //record the first tap
                startTime = new Date();
                console.log(startTime);
            }
        }//end of if

        return dif;
    }//end of tapButton
    /*************************************************************************/

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
        console.log("END ARRAY: "+returnTimes());

        //Reset the recording values
        timeArray = [];
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
            console.log("END ARRAY: " + returnTimes());
            beatCountElement.disabled = true;
            playButton.disabled = false;
            startTime = null;
            if (beatCount < 5) {
                finishButton.disabled = true;
            }
        }


        if (finishButton.innerHTML == "Submit"){
            // if (recordingType.innerHTML == dynamicRecordType) { 
            //     var js_data = returnTimes();
            //     var flask_url = '/multiplerhythm';
            // } 
            // else {} commented out since we made a recent change on how to pass the arrays
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
                var multiply = multiplier();
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

        returnArray.push(adjustedArray)
        console.log("array with recordType" + returnArray);
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
    //[TODO] Update Keytap to include the canvas animation ]
    //[TODO] Adjust Keytap to update correct array
    function record(){
        //82 is the r button
        if(event.keyCode == 82){
            if (beatCountElement.disabled == false) {
                //console.log(startTime);
                instanceTime = new Date();
                dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

                times.push(dif);
                console.log("TAP TIME: "+dif);
                console.log(times);
                beatCount+=1;
                playSound(true);
                bars.pop()
                bars.pop()
                bars.pop()
                bars.push(10)
                bars.push(20)
                bars.push(10)
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
        var quit = true;
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
            case "Disable Sound":
                quit = false;
                return;
            default:
                var sound = document.getElementById("percussion");
                break;
        }
        if (single && quit) {
            var audio = document.createElement('audio');
            audio.src = sound.src;
            audio.volume = 0.3;
            document.body.appendChild(audio);
            audio.play();
            audio.onended = function () {
                this.parentNode.removeChild(this);
            }
        }
        else {
            // if (recordingType == dynamicRecordType) { 
            //     for (var i = 0; i < timeJsonArray.length; i++) {
            //         var timeObj = timeJsonArray[i];
            //         console.log(timeObj);
            //         var millisecondsTime = timeObj.timestamp * 1000;
            //         setTimeout(() => {
            //             var audio = document.createElement('audio');
            //             audio.src = sound.src;
            //             audio.volume = 0.3;
            //             document.body.appendChild(audio);
            //             audio.play();
            //             audio.onended = function () {
            //                 this.parentNode.removeChild(this);
            //             }
            //         }, millisecondsTime);
            //     }
            // } 
            // else {
                for (var i = 0; i < times.length; i++) {
                    var millisecondsTime = (times[i]/(multiplier())) * 1000;
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
            // }
        }
    }
        
    playButton.onclick = function () {
        playSound();
    }//end of play

    //get the multiplier value from the slider
    function multiplier(){
        var mult = 0;
        const playbackrate = document.querySelector('.speedcontrolcontainer input');
        const display = document.querySelector('.speedcontrolcontainer span');
        playbackrate.addEventListener('change', e => {
            console.log("Multiplier "+playbackrate.value);
        });
        mult = playbackrate.value;
        return mult;
    }//end of multiplier


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
            barColorMute = "#878787";
            barColor = "#595959";
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
  
      setInterval(processInput, 50);
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
    startButton .addEventListener('mouseup', startRecording);
    resetButton .addEventListener('mouseup', resetRecording);
    finishButton.addEventListener('mouseup', stopRecording);
    
});