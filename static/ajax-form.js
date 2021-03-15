$('[data-ajax-submit]').on('click', function(e){
    // prevent default form submission
    e.preventDefault();
    e.stopImmediatePropagation();
    e.stopPropagation();

    let form = $(this).closest('form');
    let form_id = form.prop('id');
    let url = form.prop('action');
    let type = form.prop('method');
    let success_response = form.attr('data-success-response');
    let formData = getFormData(form_id);

    // submit form via AJAX
    send_form(form, form_id, url, type, success_response, modular_ajax, formData);
});

function getFormData(form) {
    // creates a FormData object and adds chips text
    let formData = new FormData(document.getElementById(form));
//    for (let [key, value] of formData.entries()) { console.log('formData', key, value);}
    return formData
}

function send_form(form, form_id, url, type, success_response, inner_ajax, formData) {
    // form validation and sending of form items

    if ( form[0].checkValidity() && isFormDataEmpty(formData) == false ) { // checks if form is empty
        event.preventDefault();

        // inner AJAX call
        inner_ajax(url, type, success_response, formData);

    }
    else {
        // first, scan the page for labels, and assign a reference to the label from the actual form element:
        let labels = document.getElementsByTagName('LABEL');
        for (let i = 0; i < labels.length; i++) {
            if (labels[i].htmlFor != '') {
                 let elem = document.getElementById(labels[i].htmlFor);
                 if (elem)
                    elem.label = labels[i];
            }
        }

        // then find all invalid input elements (form fields)
        let Form = document.getElementById(form_id);
        let invalidList = Form.querySelectorAll(':invalid');

        if ( typeof invalidList !== 'undefined' && invalidList.length > 0 ) {
            // errors were found in the form (required fields not filled out)

            // for each invalid input element (form field) return error
            for (let item of invalidList) {
                M.toast({html: "Please fill in the "+item.label.innerHTML+"", classes: 'bg-danger text-white'});
            }
        }
        else {
            M.toast({html: "Another error occured, please try again.", classes: 'bg-danger text-white'});
        }
    }
}

function isFormDataEmpty(formData) {
    // checks for all values in formData object if they are empty
    for (let [key, value] of formData.entries()) {
        if (value != '' && value != []) {
            return false;
        }
    }
    return true;
}

function modular_ajax(url, type, success_response, formData) {
    // Most simple modular AJAX building block
    $.ajax({
        url: url,
        type: type,
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function() {
            // show the preloader (progress bar)
            $('#form-response').html("<div class='progress'><div class='indeterminate'></div></div>");
        },
        complete: function () {
            // hide the preloader (progress bar)
            $('#form-response').html("");
        },
        success: function ( data ){
            if ( !$.trim( data.feedback )) { // response from Flask is empty
                toast_error_msg = "An empty response was returned.";
                toast_category = "danger";
            }
            else { // response from Flask contains elements
                toast_error_msg = data.feedback;
                toast_category = data.category;
                if( data.category == 'success' ){
                    if( success_response == 'redirect' ){
                        window.location.href = data.redirect_url;
                    }
                }
            }
        },
        error: function(xhr) {console.log("error. see details below.");
            console.log(xhr.status + ": " + xhr.responseText);
            toast_error_msg = "An error occured";
            toast_category = "danger";
        },
    }).done(function() {
        M.toast({html: toast_error_msg, classes: 'bg-' +toast_category+ ' text-white'});
    });
};