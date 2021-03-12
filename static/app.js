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

function goToResult() {
    console.log("asdf");
    window.location.href= "/asdfasdf"; //link from rhythm button
}


function setCounterActive() {
    document.getElementById("counter-number").className = "py-5 counter-text-active";
    document.getElementById("finishRecordingBtn").className = "btn btn-lg btn-success ml-3";
    document.getElementById("startRecordingBtn").className = "btn btn-lg btn-primary disabled ml-3";
    document.getElementById("resetRecordingBtn").className = "btn btn-lg btn-secondary ml-3";
    
}

function setCounterInactive() {
    document.getElementById("counter-number").className = "py-5 counter-text";
    document.getElementById("counter-number").innerHTML = 0;
    document.getElementById("finishRecordingBtn").className = "btn btn-lg btn-success disabled ml-3";
    document.getElementById("startRecordingBtn").className = "btn btn-lg btn-primary ml-3";
    document.getElementById("resetRecordingBtn").className = "btn btn-lg btn-secondary disabled ml-3";
}

$('.material-click').on('click', function(e) { 
    if (document.getElementById("counter-number").className == "py-5 counter-text-active") {
        var element, circle, d, x, y;
        element = $(this);
        if(element.find(".md-click-circle").length == 0) {
            element.prepend("<span class='md-click-circle'></span>");
        }
        circle = element.find(".md-click-circle");
        circle.removeClass("md-click-animate");
        if(!circle.height() && !circle.width()) {
            d = Math.max(element.outerWidth(), element.outerHeight());
            circle.css({height: d, width: d});
        }
        x = e.pageX - element.offset().left - circle.width()/2;
        y = e.pageY - element.offset().top - circle.height()/2;
        circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate");
        
        var incrementBeatCount = parseInt(document.getElementById("counter-number").innerHTML) + 1;
        document.getElementById("counter-number").innerHTML = incrementBeatCount;
    }

  });