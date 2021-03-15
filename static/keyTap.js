var startTime;
var instanceTime;

var timesTap = new Array();
var timeTapArray = [];

var dif;

$( document ).ready(function() {
var keyStartButton = document.createElement("keyContainer");
var keyTapButton = document.createElement("keyTap");
var keyStopButton = document.createElement("keyStop");
var keyResetButton = document.createElement("keyReset");


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

document.addEventListener("keydown", function(){
	resetTap();
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

/*    keyStartButton.disabled = false;
	keyTapButton.disabled = true;
	keyStopButton.disabled = true;*/
		}//end of if
	}//end of stop

/***************************************************************************/
function stopTime(){

        if (startTime){

        console.log("Time Stop");
        console.log("Stop: "+dif);
        console.log("END ARRAY: "+returnTapTimes());

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
}//end of stopTime
/***************************************************************************/
function resetTap(){
    		if(){
			keyResetButton.click(resetTap2());
    }
}//end of resetTap
/***************************************************************************/
function resetTap2(){
        if (startTime){

        console.log("Time Reset");
        console.log("Stop: "+dif);
        console.log("END ARRAY: "+returnTapTimes());
        //do something with the return times array here

        timeArray = [];
        times = new Array();
        }//enf of if

        else{
        console.log("time has not started");
        }//end of else
}
/***************************************************************************/
 function returnTapTimes(){

	for(var i = 0; i < timesTap.length; i++){
		   timeTapArray[i] = timesTap[i];

	   }//end of for

	   return timeTapArray;

}//end of returnTapTimes
/***************************************************************************/
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

});