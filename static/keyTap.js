var startTime;
var instanceTime;

var timesTap = new Array(10);
var timeTapArray = [];

var dif;

var keyStartButton = document.getElementById("keyContainer");
var keyTapButton = document.getElementById("keyTap");
var keyStopButton = document.getElementById("keyStop");

/***************************************************************************/
//event listener for key press
document.addEventListener("keydown", function(){
	start();
});

document.addEventListener("keyup", function(){
	record();
});

document.addEventListener("keydown", function(){
	stop();
});

/***************************************************************************/
	function start(){
		if(event.keyCode != 13 && event.keyCode != 32){
			keyStartButton.click(beginTime());

		}//end of if
	}//end of start

/***************************************************************************/
function beginTime(){
	startTime = new Date();
	console.log(startTime);

	keyStartButton.disabled = true;
	keyTapButton.disabled = false;
	keyStopButton.disabled = false;

}//end of beginTime

/***************************************************************************/
	function record(){

		//32 is the space bar
		if(event.keyCode == 32){
			keyTapButton.click(recordTime());

			}//end of if
	}//end of record

/***************************************************************************/
function recordTime(){
	if (startTime){
		instanceTime = new Date();

	dif = (instanceTime.getTime() - startTime.getTime()) / 1000;
				console.log(dif);
	}//end of if

	else{
			console.log("time has not started")
			}//end of else

}//end of recordTIme
/***************************************************************************/
//if the user hits the enter key then it will stop the recording
	function stop(){

		if(event.keyCode == 13){
			keyStopButton.click(stopTime());

		}//end of if
	}//end of stop

/***************************************************************************/
function stopTime(){
	if (startTime){

		console.log("Time Stop");
		console.log("END ARRAY: "+returnTapTimes(dif));
	}//end of if

	else{
		console.log("time has not started")
	}//end of else
}//end of stopTime

/***************************************************************************/
 function returnTapTimes(value){

	for(var i = 0; i < timesTap.length; i++){
		   timeTapArray[i] = value;

	   }//end of for

	   return timeTapArray;

}//end of returnTapTimes