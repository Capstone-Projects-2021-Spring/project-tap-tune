var startTime;
var instanceTime;
var times = new Array();
var timeArray = [];
var dif;

var startButton = document.getElementById("container");
var tapButton = document.getElementById("recordTap");
var stopButton = document.getElementById("recordStop");


startButton.onclick = function () {
    startTime = new Date();
    console.log(startTime);

	startButton.disabled = true;
	tapButton.disabled = false;
	stopButton.disabled = false;

}//end of startButton

/*************************************************************************/

 tapButton.onclick = function () {


    if (startTime){
		//console.log(startTime);
        instanceTime = new Date();
        dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

	   times.push(dif);
	   console.log("TAP TIME: "+dif);
	   console.log(times);
    }//end of if

    else{
        alert("time has not started");

    }//end of else

	return dif;
}//end of tapButton

/*************************************************************************/
stopButton.onclick = function () {

    if (startTime){

    console.log("Time Stop");
	console.log("Stop: "+dif);
	console.log("END ARRAY: "+returnTimes());

    }//enf of if

    else{
    console.log("time has not started");
    }//end of else
}//end of stopButton
/************************************************************************/
 function returnTimes(){

	for(var i = 0; i < times.length; i++){
		   timeArray[i] = times[i];
	   }//end of for

	   return timeArray;
}//end of returnTimes
