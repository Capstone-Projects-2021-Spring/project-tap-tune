var startTime;
var instanceTime;
var times = new Array();
var timeArray = [];
var timeJsonArray = [];
var dif;

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

    startButton.onclick = function () {
        setButtonDisables(true);
        resetCounterStyle(1);
        playButton.disabled = true;
    }//end of startButton

    /*************************************************************************/

    tapButton.onclick = function () {
        if (beatCountElement.disabled == false) {
            if (startTime) {
                instanceTime = new Date();
                dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

                //Recording Type is HarmonicLeft/PercussionRight
                if (recordingType.innerHTML == dynamicRecordType) {
                    var recordingTapType = getRecordingTypeMouse();
                    if (recordingTapType == 0) {
                        //this is harmonics
                        timeJsonArray.push({type: recordingTapType, timestamp: dif})
                    }
                    else if (recordingTapType == 1) {
                        //this is percussion
                        timeJsonArray.push({type: recordingTapType, timestamp: dif})
                    }
                    console.log("TAP TIME: " + dif);
                    console.log(timeJsonArray);
                }

                //Recording Type is General 
                else {
                    //do general rhythm recording
                    
                    times.push(dif);
                    console.log("TAP TIME: "+dif);
                    console.log(times); 
                }

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

        finishButton.innerHTML = "Stop";
        beatCountElement.innerHTML = 0;
        playButton.disabled = true;
        setButtonDisables(false);
        resetCounterStyle(0);

        if (startTime){

            console.log("Time Reset");
            console.log("Stop: "+dif);
            console.log("END ARRAY: "+returnTimes());
            //do something with the return times array here

            timeArray = [];
            times = new Array();
            timeJsonArray = [];
            startTime = null;

            //animation
            var resetButtonRect = resetButton.getBoundingClientRect();
            var element, circle, d, x, y;
            element = $("#tapScreenButton");
            if(element.find(".md-click-circle").length == 0) {
                element.prepend("<span class='md-click-circle'></span>");
            }
            circle = element.find(".md-click-circle");
            circle.removeClass("md-click-animate-red");
            circle.removeClass("md-click-animate-green");
            circle.removeClass("md-click-animate-orange");
            circle.removeClass("md-click-animate-gray");
            circle.removeClass("md-click-animate");
            if(!circle.height() && !circle.width()) {
                d = Math.max(element.outerWidth(), element.outerHeight());
                circle.css({height: d, width: d});
            }

            x = ((resetButtonRect.right - resetButtonRect.left) / 2) + resetButtonRect.left - circle.width()/2;
            y = ((resetButtonRect.bottom - resetButtonRect.top) / 2) + resetButtonRect.top - circle.height()/2;
            circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate-gray");

            //also set playbutton to disabled again
            playButton.disabled = true;

        }//enf of if

        else{
            console.log("time has not started");
            timeArray = [];
            times = new Array();
            timeJsonArray = [];
            startTime = null;
        }//end of else


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
            if (parseInt(beatCountElement.innerHTML) < 5) {
                finishButton.disabled = true;
            }
        }


        if (finishButton.innerHTML == "Submit"){
            if (recordingType.innerHTML == dynamicRecordType) { 
                var js_data = returnTimes();
                var flask_url = '/multiplerhythm';
            } 
            else {
                var js_data = JSON.stringify(returnTimes());
                var flask_url = '/rhythm';
            }
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

            //goToFiltering();
        }
        else {
            //animation
            var finishButtonRect = finishButton.getBoundingClientRect();
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

            x = ((finishButtonRect.right - finishButtonRect.left) / 2) + finishButtonRect.left - circle.width()/2;
            y = ((finishButtonRect.bottom - finishButtonRect.top) / 2) + finishButtonRect.top - circle.height()/2;
            circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate-green");
            
            //change text class to be stagnat and confirm user submit 
            //Also enable playback button
            beatCountElement.disabled == true;
            finishButton.innerHTML = "Submit";
            playButton.disabled = false;
        }


    }//end of stopButton

    /************************************************************************/
    function returnTimes(){
        if (recordingType.innerHTML == dynamicRecordType) { 
            var returnArray = adjustArray(timeJsonArray);
            timeJsonArray = returnArray;
            return JSON.stringify(returnArray);
        }
        else {
            //General Recording Return
            var returnArray = adjustArray(times);
            console.log("finished array " + returnArray)
            times = returnArray;
            return returnArray;
        }
    }//end of returnTimes

    /************************************************************************/
    function adjustArray(array){
        //adjust array times so that the first array does not count

        if (recordingType.innerHTML == dynamicRecordType) { 
            var jsonArray = array;
            var dif = jsonArray[0].timestamp;
            for (var i = 0; i < jsonArray.length; i++) {
                var num = jsonArray[i].timestamp - dif;
                jsonArray[i].timestamp = parseFloat(num.toFixed(3));
            }
            //console.log("finished array " + timeJsonArray)
            //times = returnArray;
            return jsonArray;
        }
        else {

            var newArray = new Array();
            var dif = array[0];
            for(var i = 0; i < array.length; i++){
                var num = array[i] - dif;
                newArray[i] = parseFloat(num.toFixed(3));
            }//end of for
        }
            
        return newArray;
    }//end of returnTimes
    
    
    document.addEventListener("keydown", function(){
        record();
    });

    /***************************************************************************/
    function record(){

        //32 is the space bar
        if(event.keyCode == 82){
            if (beatCountElement.disabled == false) {
                //console.log(startTime);
                instanceTime = new Date();
                dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

                times.push(dif);
                console.log("TAP TIME: "+dif);
                console.log(times);

                var element, circle, d, x, y;
                element = $("#tapScreenButton");
                if(element.find(".md-click-circle").length == 0) {
                    element.prepend("<span class='md-click-circle'></span>");
                }
                circle = element.find(".md-click-circle");
                circle.removeClass("md-click-animate-red");
                circle.removeClass("md-click-animate-gray");
                circle.removeClass("md-click-animate-orange");
                circle.removeClass("md-click-animate-green");
                circle.removeClass("md-click-animate");
                if(!circle.height() && !circle.width()) {
                    d = Math.max(element.outerWidth(), element.outerHeight());
                    circle.css({height: d, width: d});
                }
                x = ((element.offset().right - element.offset().left) / 2)  - circle.width()/2;
                y = ((element.offset().bottom - element.offset().top) / 2) - circle.height()/2;


                circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate");
                var incrementBeatCount = parseInt(beatCountElement.innerHTML) + 1;
                beatCountElement.innerHTML = incrementBeatCount;
                var healthCountg = Math.floor((incrementBeatCount / 12) * 153);
                var healthCountb = Math.floor((incrementBeatCount / 12) * 255);
                if (incrementBeatCount >= 12) {
                    beatCountElement.style.color = RGBToHex(0, 153, 255);
                    beatCountElement.style.textShadow = "0 0 16px var(--blue)";
                }
                else {
                    beatCountElement.style.color = RGBToHex(0, healthCountg, healthCountb);
                }
            }//end of if
        }//end of if
    }//end of record

    $('.material-click').on('click', function(e) {
        var colorBox = getColor(e);
        if (beatCountElement.disabled == false || colorBox > 0) {
            var element, circle, d, x, y;
            element = $(this);
            if(element.find(".md-click-circle").length == 0) {
                element.prepend("<span class='md-click-circle'></span>");
            }
            circle = element.find(".md-click-circle");
            circle.removeClass("md-click-animate-red");
            circle.removeClass("md-click-animate-green");
            circle.removeClass("md-click-animate-gray");
            circle.removeClass("md-click-animate-orange");
            circle.removeClass("md-click-animate");
            if(!circle.height() && !circle.width()) {
                d = Math.max(element.outerWidth(), element.outerHeight());
                circle.css({height: d, width: d});
            }
            x = e.pageX - element.offset().left - circle.width()/2;
            y = e.pageY - element.offset().top - circle.height()/2;
            if (recordingType.innerHTML == dynamicRecordType) { 
                var recordingTapType = getRecordingTypeMouse();
                if (recordingTapType == 1 && (colorBox != 1)) {
                    colorBox = 2; //make the circle animate as orange
                }
            }

            switch (colorBox) {
                case -1:
                    break;

                case 1:
                    circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate-red");
                    beatCountElement.style.color = RGBToHex(0, 0, 0);
                    break;
                case 2:
                    playSound(true);
                    circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate-orange");
                    var incrementBeatCount = parseInt(beatCountElement.innerHTML) + 1;
                    beatCountElement.innerHTML = incrementBeatCount;
                    var healthCountg = Math.floor((incrementBeatCount / 12) * 153);
                    var healthCountb = Math.floor((incrementBeatCount / 12) * 255);
                    if (incrementBeatCount >= 12) {
                        beatCountElement.style.color = RGBToHex(0, 153, 255);
                        beatCountElement.style.textShadow = "0 0 16px var(--blue)";
                    }
                    else {
                        beatCountElement.style.color = RGBToHex(0, healthCountg, healthCountb);
                    }
                    break;
                default:
                    playSound(true);
                    circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate");
                    var incrementBeatCount = parseInt(beatCountElement.innerHTML) + 1;
                    beatCountElement.innerHTML = incrementBeatCount;
                    var healthCountg = Math.floor((incrementBeatCount / 12) * 153);
                    var healthCountb = Math.floor((incrementBeatCount / 12) * 255);
                    if (incrementBeatCount >= 12) {
                        beatCountElement.style.color = RGBToHex(0, 153, 255);
                        beatCountElement.style.textShadow = "0 0 16px var(--blue)";
                    }
                    else {
                        beatCountElement.style.color = RGBToHex(0, healthCountg, healthCountb);
                    }
                    break;
            }

        }

    });

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
        //var boolean = (selected == dynamicRecordType);
        //recordingKeyDropdown.disabled = !boolean;
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
            if (recordingType == dynamicRecordType) { 
                for (var i = 0; i < timeJsonArray.length; i++) {
                    var timeObj = timeJsonArray[i];
                    console.log(timeObj);
                    var millisecondsTime = timeObj.timestamp * 1000;
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
            else {
                for (var i = 0; i < times.length; i++) {
                    var millisecondsTime = times[i] * 1000;
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
        }
    }
        
    playButton.onclick = function () {
        playSound();
    }
});



