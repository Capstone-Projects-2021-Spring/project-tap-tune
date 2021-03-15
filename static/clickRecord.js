var startTime;
var instanceTime;
var times = new Array();
var timeArray = [];
var dif;

var startButton = document.getElementById("startRecordingBtn");
var tapButton = document.getElementById("tapScreenButton");
var resetButton = document.getElementById("resetRecordingBtn");
var finishButton = document.getElementById("finishRecordingBtn");



$( document ).ready(function() {

let startButton = null;
let tapButton = null;
let stopButton = null;
var finishButton = null;

    startButton = document.getElementById("startRecordingBtn");
    tapButton = document.getElementById("tapScreenButton");
    resetButton = document.getElementById("resetRecordingBtn");
    finishButton = document.getElementById("finishRecordingBtn");

    startButton.onclick = function (){startClick()}
    tapButton.onclick = function (){tapClick()}
    resetButton.onclick = function (){resetClick()}
    finishButton.onclick = function (){finishClick()}

    function startClick(){
        startTime = new Date();
        console.log(startTime);


        document.getElementById("counter-number").className = "py-5 counter-text-active";
        document.getElementById("counter-number").style.opacity = "1";
        document.getElementById("finishRecordingBtn").className = "btn btn-lg btn-success ml-3";
        document.getElementById("startRecordingBtn").className = "btn btn-lg btn-primary disabled ml-3";
        document.getElementById("resetRecordingBtn").className = "btn btn-lg btn-secondary ml-3";

    }//end of startButton

/*************************************************************************/

    function tapClick() {
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
    function resetClick(){

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
    function finishClick(){

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

        return returnTimes();
    }//end of stopButton

/************************************************************************/
    function returnTimes(){

        for(var i = 0; i < times.length; i++){
            timeArray[i] = times[i];
        }//end of for

        return timeArray;
    }//end of returnTimes
/************************************************************************/
 $(document).ready(function () {
                $("#finishRecordingBtn").on("click", function() {
                    var js_data = JSON.stringify(finishClick());
                    $.ajax({
                        url: '/rhythm',
                        type : 'post',
                        contentType: 'application/json',
                        dataType : 'json',
                        data : js_data
                    }).done(function(result) {
                        console.log("AJAX CLICK: "+result);
                        //return result;
                        //$("#data").html(result);
                    }).fail(function(jqXHR, textStatus, errorThrown) {
                        console.log("fail: ",textStatus, errorThrown);
                    });
                });
            });
/************************************************************************/

});

