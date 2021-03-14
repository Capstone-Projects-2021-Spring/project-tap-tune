var startTime;
var instanceTime;
var times = new Array();
var timeArray = [];
var dif;

var startButton = document.getElementById("container");
var tapButton = document.getElementById("recordTap");
var stopButton = document.getElementById("recordStop");

startButton.onclick = function(){startClick()};
tapButton.onclick = function(){tapClick()};
stopButton.onclick = function(){stopClick()};

function startClick() {
    startTime = new Date();
    console.log(startTime);

	startButton.disabled = true;
	tapButton.disabled = false;
	stopButton.disabled = false;

}//end of startButton

/*************************************************************************/
function tapClick() {


    if (startTime){
		//console.log(startTime);
        instanceTime = new Date();
        dif = (instanceTime.getTime() - startTime.getTime()) / 1000;

	   times.push(dif);
	   console.log("CLICK TIME: "+dif);
	   console.log(times);
    }//end of if

    else{
        alert("time has not started");

    }//end of else

	return dif;
}//end of tapButton

/*************************************************************************/
function stopClick(){

    if (startTime){

    console.log("Time Stop");
	console.log("Stop: "+dif);
	console.log("END ARRAY: "+returnTimes());

    out = returnTimes();

    startButton.disabled = false;
	tapButton.disabled = true;
	stopButton.disabled = true;

    return out;
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

 $(document).ready(function () {
                $("#recordStop").on("click", function() {
                    var js_data = JSON.stringify(stopClick());
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
