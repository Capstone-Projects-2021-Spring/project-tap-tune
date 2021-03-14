var startTime;
var instanceTime;

var timesTap = new Array();
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

document.addEventListener("keydown", function(){
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

	   timesTap.push(dif);
	   console.log("TAP TIME: "+dif);
	   console.log(timesTap);
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

    keyStartButton.disabled = false;
	keyTapButton.disabled = true;
	keyStopButton.disabled = true;
		}//end of if
	}//end of stop

/***************************************************************************/
function stopTime(){

	if (startTime){
		console.log("Time Stop");
		console.log("END ARRAY: "+returnTapTimes());

		outKey = returnTapTimes();

		return outKey;
	}//end of if

	else{
		console.log("time has not started")
	}//end of else
}//end of stopTime

/***************************************************************************/
 function returnTapTimes(){

	for(var i = 0; i < timesTap.length; i++){
		   timeTapArray[i] = timesTap[i];

	   }//end of for

	   return timeTapArray;

}//end of returnTapTimes

 $(document).ready(function () {
                $("#keyStop").on("click", function() {
                    var js_data = JSON.stringify(stopTime());
                    $.ajax({
                        url: '/rhythm',
                        type : 'post',
                        contentType: 'application/json',
                        dataType : 'json',
                        data : js_data
                    }).done(function(result) {
                        console.log("AJAX TAP: "+result);

                    }).fail(function(jqXHR, textStatus, errorThrown) {
                        console.log("fail: ",textStatus, errorThrown);
                    });
                });
            });