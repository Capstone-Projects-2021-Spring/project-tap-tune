$('.greeting').on('click',function(e){
    alert("HELLO WORLD");
});

$('div.topnav a').on('click', function(){
    $('a.active').removeClass('active'); // to remove the current active tab
    $(this).addClass('active'); // add active class to the clicked tab
});