var startTime;
var instanceTime;
var times = new Array(50);
var timeArray = [];
var dif;

var startButton = document.getElementById("container");
var tapButton = document.getElementById("recordTap");
var stopButton = document.getElementById("recordStop");


startButton.onclick = function () {
    startTime = new Date();
    console.log(startTime);

	startButton.disabled = false;
	tapButton.disabled = false;
	stopButton.disabled = false;
}

/*************************************************************************/

 tapButton.onclick = function () {


    if (startTime){
		//console.log(startTime);
        instanceTime = new Date();
        dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

	   console.log("TAP TIME: "+dif);



    }//end of if
    else{
        alert("time has not started");

    }


	//console.log(timeArray);

	   //console.log(timeArray);
	   console.log("END OF TAP: "+dif);
	return dif;
}

/*************************************************************************/
stopButton.onclick = function () {

    if (startTime){

    console.log("Time Stop");


	console.log("Stop: "+dif);
	//console.log("Array: "+timeArray);
	console.log("END ARRAY: "+returnTimes(dif));
    }

    else{


    console.log("time has not started");


    }//end of else
}
/************************************************************************/
 function returnTimes(value){

		   for(var i = 0; i < times.length; i++){
		   timeArray[i] = value;

	   }

	   return timeArray;


}
