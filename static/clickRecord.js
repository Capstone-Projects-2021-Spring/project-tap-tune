var startTime;
var instanceTime;
var times = new Array();
var timeArray = [];
var dif;

let startButton = null;
let tapButton = null;
let stopButton = null;
let finishButton = null;
$( document ).ready(function() {
    startButton = document.getElementById("startRecordingBtn");
    tapButton = document.getElementById("tapScreenButton");
    resetButton = document.getElementById("resetRecordingBtn");
    finishButton = document.getElementById("finishRecordingBtn");

    startButton.onclick = function () {
        startTime = new Date();
        console.log(startTime);


        document.getElementById("counter-number").className = "py-5 counter-text-active";
        document.getElementById("counter-number").style.opacity = "1";
        document.getElementById("finishRecordingBtn").className = "btn btn-lg btn-success ml-3";
        document.getElementById("startRecordingBtn").className = "btn btn-lg btn-primary disabled ml-3";
        document.getElementById("resetRecordingBtn").className = "btn btn-lg btn-secondary ml-3";

    }//end of startButton

    /*************************************************************************/

    tapButton.onclick = function () {
        if (document.getElementById("counter-number").className == "py-5 counter-text-active") {
            //console.log(startTime);
            instanceTime = new Date();
            dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

        times.push(dif);
        console.log("TAP TIME: "+dif);
        console.log(times);
        }//end of if

        return dif;
    }//end of tapButton
    /*************************************************************************/
    resetButton.onclick = function () {

        document.getElementById("finishRecordingBtn").innerHTML = "Stop";
        document.getElementById("counter-number").className = "py-5 counter-text";
        document.getElementById("counter-number").style.color = "#858585";
        document.getElementById("counter-number").style.opacity = "0.5";
        document.getElementById("counter-number").style.textShadow = "";

        document.getElementById("counter-number").innerHTML = 0;
        document.getElementById("finishRecordingBtn").className = "btn btn-lg btn-success disabled ml-3";
        document.getElementById("startRecordingBtn").className = "btn btn-lg btn-primary ml-3";
        document.getElementById("resetRecordingBtn").className = "btn btn-lg btn-secondary disabled ml-3";

        if (startTime){

        console.log("Time Reset");
        console.log("Stop: "+dif);
        console.log("END ARRAY: "+returnTimes());
        //do something with the return times array here

        timeArray = [];
        times = new Array();
        }//enf of if

        else{
        console.log("time has not started");
        }//end of else


    }//end of stopButton

    /*************************************************************************/
    finishButton.onclick = function () {


        if (startTime){

        console.log("Time Stop");
        console.log("Stop: "+dif);
        console.log("END ARRAY: "+returnTimes());

        }//enf of if

        else{
        console.log("time has not started");
        }//end of else

        if (finishButton.innerHTML == "Submit")
            goToFiltering();
        else {
            document.getElementById("counter-number").className = "py-5 counter-text";
            finishButton.innerHTML = "Submit";
        }


    }//end of stopButton

    /************************************************************************/
    function returnTimes(){

        for(var i = 0; i < times.length; i++){
            timeArray[i] = times[i];
        }//end of for

        return timeArray;
    }//end of returnTimes

    
    
    document.addEventListener("keydown", function(){
        record();
    });
    
    /***************************************************************************/
    function record(){
        
        //32 is the space bar
        if(event.keyCode == 32){
            if (document.getElementById("counter-number").className == "py-5 counter-text-active") {
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
                circle.removeClass("md-click-animate");
                if(!circle.height() && !circle.width()) {
                    d = Math.max(element.outerWidth(), element.outerHeight());
                    circle.css({height: d, width: d});
                }
                x = element.offset().left - circle.width()/2;
                y = element.offset().top - circle.height()/2;
                
        
                circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate");
                var incrementBeatCount = parseInt(document.getElementById("counter-number").innerHTML) + 1;
                document.getElementById("counter-number").innerHTML = incrementBeatCount;
                var healthCountg = Math.floor((incrementBeatCount / 12) * 153);
                var healthCountb = Math.floor((incrementBeatCount / 12) * 255);
                if (incrementBeatCount >= 12) {
                    document.getElementById("counter-number").style.color = RGBToHex(0, 153, 255);
                    document.getElementById("counter-number").style.textShadow = "0 0 16px var(--blue)";
                }
                else {
                    document.getElementById("counter-number").style.color = RGBToHex(0, healthCountg, healthCountb);
                }
            }//end of if
            
            return dif;
            
        }//end of if
    }//end of record



    $('.material-click').on('click', function(e) { 
        var colorBox = getColor(e);
        console.log("color was " + colorBox);   
        if (document.getElementById("counter-number").className == "py-5 counter-text-active" || colorBox > 0) {
            var element, circle, d, x, y;
            element = $(this);
            if(element.find(".md-click-circle").length == 0) {
                element.prepend("<span class='md-click-circle'></span>");
            }
            circle = element.find(".md-click-circle");
            circle.removeClass("md-click-animate-red");
            circle.removeClass("md-click-animate");
            if(!circle.height() && !circle.width()) {
                d = Math.max(element.outerWidth(), element.outerHeight());
                circle.css({height: d, width: d});
            }
            x = e.pageX - element.offset().left - circle.width()/2;
            y = e.pageY - element.offset().top - circle.height()/2;
            
            switch (colorBox) {
                case -1:
                    break; 
    
                case 1:
                    console.log("you pressed red")
                    circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate-red");
                    var incrementBeatCount = parseInt(document.getElementById("counter-number").innerHTML) + 1;
                    document.getElementById("counter-number").innerHTML = incrementBeatCount;
                    var healthCountg = Math.floor((incrementBeatCount / 10) * 153);
                    var healthCountb = Math.floor((incrementBeatCount / 10) * 255);
                    document.getElementById("counter-number").style.color = RGBToHex(0, healthCountg, healthCountb);
                    break;
            
                default:
                    circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate");
                    var incrementBeatCount = parseInt(document.getElementById("counter-number").innerHTML) + 1;
                    document.getElementById("counter-number").innerHTML = incrementBeatCount;
                    var healthCountg = Math.floor((incrementBeatCount / 12) * 153);
                    var healthCountb = Math.floor((incrementBeatCount / 12) * 255);
                    if (incrementBeatCount >= 12) {
                        document.getElementById("counter-number").style.color = RGBToHex(0, 153, 255);
                        document.getElementById("counter-number").style.textShadow = "0 0 16px var(--blue)";
                    }
                    else {
                        document.getElementById("counter-number").style.color = RGBToHex(0, healthCountg, healthCountb);
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
        var startButtonRect = document.getElementById("startRecordingBtn").getBoundingClientRect();
        var resetButtonRect = document.getElementById("resetRecordingBtn").getBoundingClientRect();
        var finishButtonRect = document.getElementById("finishRecordingBtn").getBoundingClientRect();
        var incrementBeatCount = parseInt(document.getElementById("counter-number").innerHTML);
    
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
    
});

