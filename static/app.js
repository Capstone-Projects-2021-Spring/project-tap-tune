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

function goToMelody() {
  window.location.href= "/recordingMelody"; //link from rhythm button
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

