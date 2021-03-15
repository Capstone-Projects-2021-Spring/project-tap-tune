/**
Service Worker used by PWA
*/
if ('serviceWorker' in navigator) {
    navigator.serviceWorker
    .register('./service-worker.js')
    .then(function(registration) {
        console.log('Service Worker Registered!');
        return registration;
    })
    .catch(function(err) {
        console.error('Unable to register service worker.', err);
    });
}

$('.greeting').on('click',function(e){
    alert("HELLO WORLD");
});

function goToFiltering() {
    window.location.href= "/filtering"; //link from rhythm button
}

function goToRhythm() {
      window.location.href= "/recordingRhythm"; //link from rhythm button
}

function goToRegister() {
      window.location.href= "/register";
}

function userLogin() {
      window.location.href= "/login";
}

//Stuff for forgotPass html
function forgotPass() {
	window.location.href= "/forgot"
}
$(document).ready(function() {
  $('#olvidado').click(function(e) {
    e.preventDefault();
    $('div#form-olvidado').toggle('500');
  });
  $('#acceso').click(function(e) {
    e.preventDefault();
    $('div#form-olvidado').toggle('500');
  });
});
//end stuff for forgotPass html

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

            else if ((e.pageX < resetButtonRect.right) && (e.pageX > resetButtonRect.left) && (incrementBeatCount > 0)) { //gray
                return 2;
            }

            else if ((e.pageX < finishButtonRect.right) && (e.pageX > finishButtonRect.left) && (incrementBeatCount > 0)) { //green
                
                return 3;
            }
        }
    }
    return 0;
}