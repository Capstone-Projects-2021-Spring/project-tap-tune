$( document ).ready(function() {

    var current_page = 1;
    var records_per_page = 5;
    var current_pageTwo = 1;
    var records_per_pageTwo = 5;
    var testData = document.querySelectorAll("#songRow");
    var testDataTwo = document.querySelectorAll("#songRowTwo");
    var btn_next = document.getElementById("nextPageList");
    var btn_prev = document.getElementById("prevPageList");
    var btn_nextTwo = document.getElementById("nextPageListTwo");
    var btn_prevTwo = document.getElementById("prevPageListTwo");
    var listing_table = document.getElementById("pageContainer");
    var listing_tableTwo = document.getElementById("pageContainerTwo");
    var page_span = document.getElementById("page");

// let currentTitle = document.getElementById("songLogTitle").innerText;
// let currentArtist = document.getElementById("songLogArtist").innerText;

    btn_next.onclick = function () {
        nextPage();
        console.log("Hello Next Button One Pressed");
    }

    btn_prev.onclick = function () {
        prevPage();
        console.log("Hello Prev Button One Pressed");
    }

////////////////////////////////////////////////////////////////////////

    btn_nextTwo.onclick = function () {
        nextPageTwo();
        console.log("Hello Next Button Two Pressed");
    }

    btn_prevTwo.onclick = function () {
        prevPageTwo();
        console.log("Hello Prev Button Two Pressed");
    }


    function nextPage()
    {
        if (current_page < numPages()) {
            current_page++;
            changePage(current_page);
        }
    }

    function prevPage()
    {
        if (current_page > 1) {
            current_page--;
            changePage(current_page);
        }
    }

    function nextPageTwo()
    {
        if (current_pageTwo < numPages()) {
            current_pageTwo++;
            changePageTwo(current_pageTwo);
        }
    }

    function prevPageTwo()
    {
        if (current_pageTwo > 1) {
            current_pageTwo--;
            changePageTwo(current_pageTwo);
        }
    }
////////////////////////////////////////////////////////////////////////////////////////////////
    function changePage(page)
    {
        // Validate page
        if (page < 1) page = 1;
        if (page > numPages()) page = numPages();

        listing_table.innerHTML = "";


        for (var i = (page-1) * records_per_page; i < (page * records_per_page) && i < testData.length; i++) {
            listing_table.innerHTML += testData[i].innerHTML;
        }
        //page_span.innerHTML = page + "/" + numPages();

        if (page == 1) {
            btn_prev.disabled = true;
        } else {
            btn_prev.disabled = false;
        }

        if (page == numPages()) {
            btn_next.disabled = true;
        } else {
            btn_next.disabled = false;
        }
    }

/////////////////////////////////////////////////////////////////////////////////////////////
    function changePageTwo(pageTwo)
    {
        // Validate pageTwo
        if (pageTwo < 1) pageTwo = 1;
        if (pageTwo > numPagesTwo()) pageTwo = numPagesTwo();

        listing_tableTwo.innerHTML = "";

        for (var i = (pageTwo-1) * records_per_page; i < (pageTwo * records_per_page) && i < testDataTwo.length; i++) {
            listing_tableTwo.innerHTML += testDataTwo[i].innerHTML;
        }
        //page_span.innerHTML = pageTwo + "/" + numPages();

        if (pageTwo == 1) {
            btn_prevTwo.disabled = true;
        } else {
            btn_prevTwo.disabled = false;
        }

        if (pageTwo == numPagesTwo()) {
            btn_nextTwo.disabled = true;
        } else {
            btn_nextTwo.disabled = false;
        }
    }




    function numPages()
    {
        return Math.ceil(testData.length / records_per_page);
    }

    function numPagesTwo() {
        return Math.ceil(testDataTwo.length / records_per_pageTwo);
    }


    window.onload = function() {
        changePage(1);
        changePageTwo(1);
    };

});