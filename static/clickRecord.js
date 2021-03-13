var startTime;
var instanceTime;
var times = new Array();
var timeArray = [];
var dif;

var startButton = document.getElementById("startRecordingBtn");
var tapButton = document.getElementById("tapScreenButton");
var resetButton = document.getElementById("resetRecordingBtn");
var finishButton = document.getElementById("finishRecordingBtn");


startButton.onclick = function () {
    startTime = new Date();
    console.log(startTime);


    document.getElementById("counter-number").className = "py-5 counter-text-active";
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


