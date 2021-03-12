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


function goToRhythm() {
      window.location.href= "/recordingRhythm"; //link from rhythm button
}


function goToRegister() {
      window.location.href= "/register";
}

function userLogin() {
      window.location.href= "/login";

}