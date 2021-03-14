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


$('.material-click').on('click', function(e) { 
    var colorBox = getColor(e);
    console.log("color was " + colorBox);   
    if (document.getElementById("counter-number").className == "py-5 counter-text-active" || colorBox > 0) {
        var element, circle, d, x, y;
        element = $(this);
        if(element.find(".md-click-circle").length == 0) {
            element.prepend("<span class='md-click-circle'></span>");
        }
        circle = element.find(".md-click-circle");
        circle.removeClass("md-click-animate-red");
        circle.removeClass("md-click-animate");
        if(!circle.height() && !circle.width()) {
            d = Math.max(element.outerWidth(), element.outerHeight());
            circle.css({height: d, width: d});
        }
        x = e.pageX - element.offset().left - circle.width()/2;
        y = e.pageY - element.offset().top - circle.height()/2;
        
        switch (colorBox) {
            case -1:
                break; 

            case 1:
                console.log("you pressed red")
                circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate-red");
                var incrementBeatCount = parseInt(document.getElementById("counter-number").innerHTML) + 1;
                document.getElementById("counter-number").innerHTML = incrementBeatCount;
                var healthCountg = Math.floor((incrementBeatCount / 10) * 153);
                var healthCountb = Math.floor((incrementBeatCount / 10) * 255);
                document.getElementById("counter-number").style.color = RGBToHex(0, healthCountg, healthCountb);
                break;
        
            default:
                circle.css({top: y+'px', left: x+'px'}).addClass("md-click-animate");
                var incrementBeatCount = parseInt(document.getElementById("counter-number").innerHTML) + 1;
                document.getElementById("counter-number").innerHTML = incrementBeatCount;
                var healthCountg = Math.floor((incrementBeatCount / 12) * 153);
                var healthCountb = Math.floor((incrementBeatCount / 12) * 255);
                if (incrementBeatCount >= 12) {
                    document.getElementById("counter-number").style.color = RGBToHex(0, 153, 255);
                    document.getElementById("counter-number").style.textShadow = "0 0 16px var(--blue)";
                }
                else {
                    document.getElementById("counter-number").style.color = RGBToHex(0, healthCountg, healthCountb);
                }
                break;
        }
        
    }

  });

  function RGBToHex(r,g,b) {
    r = r.toString(16);
    g = g.toString(16);
    b = b.toString(16);
  
    if (r.length == 1)
      r = "0" + r;
    if (g.length == 1)
      g = "0" + g;
    if (b.length == 1)
      b = "0" + b;
  
    return "#" + r + g + b;
  }

function goToRegister() {
      window.location.href= "/register";
}

function userLogin() {
      window.location.href= "/login";

}

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
        }
    }
    return 0;
}
