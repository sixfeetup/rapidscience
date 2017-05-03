function checkfile(sender) {
    if (!sender.value) {
        return false;
    }
    var validExts = [];
    var validAttachExts = [".pdf", ".jpeg", ".jpg", '.png', '.tif', '.tiff'];
    var validFileExts = [".doc", ".docx", ".epub", ".html", ".odt", ".pdf", ".rtf", ".txt", ".zip"];
    var fileExt = sender.value;
    fileExt = fileExt.substring(fileExt.lastIndexOf('.'));
    var attachexpr = "/attachment/";
    if (sender.id == 'uploadfile') {
        validExts = validFileExts;
    } else if (attachexpr.search(sender.name)) {
        validExts = validAttachExts;
    }
    var message = '';
    if (validExts.indexOf(fileExt) < 0) {
        message += 'Invalid file selected, valid files are of ' + validExts.toString() + ' types.';
    }
    if (sender.files[0].size > 2*1024*1024) {
        message += ' File size must be smaller than 2MB.';
    }
    if (message != '') {
        $(sender).parent().before(
            '<div class="alert alert-danger alert-dismissible fade in" role="alert">'+
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
                '<span aria-hidden="true">&times;</span>'+
            '</button>'+ message + '</div>'
        );
        $(sender).val('');
        return false;
    }
    else return true;
}

$(document).ready(function() {
    var max_fields      = 20; //maximum input boxes allowed
    var wrapper         = $(".authors-div"); //Fields wrapper
    var add_button      = $(".add_field_button"); //Add button ID

    var x = 1; //initlal text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(wrapper).append('<div class="form-group col-md-8 col-xs-8 "><label for="title">Authorized Email:</label>' +
                    '<input  class="form-control col-md-11" id="author_email" type="email" placeholder="Healthcare professional or administrator authorized to edit this record" name="author"/>' +
                    '<a href="#" class="remove_field"><i class="fa  fa-times"></i></a></div>'); //add input box
        }
    });

    // manage placeholders
    $('.placeholder').each(function() {
      $(this).attr('placeholder', $(this).attr('placeholder_text'));
      $(this).focus(function() {
          $(this).attr('placeholder', '');
      });
      $(this).blur(function() {
        $(this).attr('placeholder', $(this).attr('placeholder_text'));
      });
    });

    $(".select2").select2();

    $(wrapper).on("click",".remove_field", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent('div').remove(); x--;
    })
});


function captcha(){
    captcha_0 = $('#id_captcha_0').val();
    captcha_1 = $('#id_captcha_1').val();
    agree_checkbox = $(".agree-checkbox");
    if (captcha_1 =='') {
        caseform.captcha_1.focus();
        $(".required-message").show();
        $(".captcha-message").show();
        return false
    }$(".captcha-message").hide();
    if (agree_checkbox.prop('checked') == false ){
        agree_checkbox.focus();
        $(".agree-message").show();
        return false
    }

    var form = document.getElementById('caseform');

        csrfmiddlewaretoken = document.getElementsByName('csrfmiddlewaretoken')[0].value;


        data = {'captcha_0':captcha_0,'captcha_1':captcha_1,'csrfmiddlewaretoken':csrfmiddlewaretoken}
        $.ajax({
                            type:"post",
                            url : "/casereport/add/",
                            data : data,
                            success : function(response) {
                                if (response != 'OK') {
                                    $('#invalid_cap').removeClass('hide');
                                    $("#captcha img").attr("src", response.new_cptch_image);
                                    $("#id_captcha_0").val(response.new_cptch_key);
                                    $("#id_captcha_1").focus();
                                    return false
                                }
                                else{
                                    $("#crdb-overlay-loader.active").show();
                                    $('#caseform').submit();
                                    $('#invalid_cap').addClass('hide');
                                    return true
                                }
                            },
                            error: function() {
                                console.log('Error occured');
                                return false
                            }
                        });

}

    $(".radiobut").click(function(){
        type = $(this).val();
        $(".manual-form").hide();
        $(".free-text").hide();
        $(".file-form").hide();
        
        if (type == 'M') {
            $(".manual-form").show();
        } else if (type == 'T') {
            $(".free-text").show();
        } else if (type == 'F') {
            $(".file-form").show();
        } 

    });



    $(document).ready(function() {
    var max_fields      = 20; //maximum input boxes allowed
    var new_wrapper         = $(".molecular-abberations"); //Fields wrapper
    var add_button      = $(".add_button"); //Add button ID

    var x = 1; //initlal text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(new_wrapper).append('<div><label for="comment">Molecular Abberations:</label>' +
                            '<div class="row ">'+
                            '<div class="form-group col-xs-6">'+
                            '<input name="test" class="form-control test" ></div>'+
                            '<div class="form-group col-xs-6">'+
                          '<input type="text" name="test_result" class="form-control"></div>'+
                    '<a href="#" class="remove_field"><i class="fa  fa-times"></i></a></div>'); //add input box
        }
    });

    $(new_wrapper).on("click",".remove_field", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent().parent('div').remove(); x--;
    })




});


    $('body').on('focusin','.test',function() {
        $(this).autocomplete({
            source: "/casereport/autocomplete/",
            minLength: 2,
        })

    })



//for physician

$(document).ready(function() {
    var max_fields      = 20; //maximum input boxes allowed
    var phy_wrapper         = $(".physician-div"); //Fields wrapper
    var add_button      = $(".add_phy_button"); //Add button ID
    
    var x = $(".physician-div .row.physician").length; //initlal text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(phy_wrapper).append(
                '<div class="row physician"><div class="form-group col-md-6">' +
                '<label for="physician_name' + x + '">Name</label>' +
                '<input name="physician_name" type="text" class="form-control" id="physician_name' + x + '" placeholder="First and Last Name">'+
                '<div class="helpText">' +
                    'ex: John Smith, MD, PhD' +
                '</div>' +
                '</div><div class="form-group col-md-5">' +
                '<label for="physician_email' + x + '">Email Address</label>' +
                '<input name="physician_email" type="EMAIL" class="form-control" id="physician_email' + x + '" placeholder="Email">'+
                '<div class="helpText">' +
                    'You must use an institutional email address' +
                '</div>' +
                '</div><div class="col-md-1"><a href="#" class="remove_phy"><i class="fa fa-times"></i></a></div></div>'
            );
            if ($('.row.physician').length > 0) {
                $(".add_phy_button_text").text('Add another co-author');
            }
            if ($('.row.physician').length >= max_fields) {
                add_button.hide();
            }
        }
    });

    $(phy_wrapper).on("click",".remove_phy", function(e){ //user click on remove text
        e.preventDefault(); $(this).parents('.row.physician').remove();
        if ($('.row.physician').length == 0) {
            $(".add_phy_button_text").text('Add co-author');
        }
        if ($('.row.physician').length <= max_fields) {
            $(".add_phy_button").show();
        }
    })

});


function validate(ev) {
    ev.preventDefault()
    $(".required-message").hide();
    var radio = $('.radiobut').val();
    var e = $('.radiobut:checked').length > 0;
    if (e != true) {
        $(".radiobut").focus();
        $(".choose-message").show();
        return false;
    } else {
        $(".choose-message").hide();
        if ($("#id_radio3").is(':checked')) {
            return file_validate();
        } else if ($("#id_radio1").is(':checked')) {
            return manual_validate();
        } else {
            return freetext_validate();
        }
    }
}


function file_validate() {
    var uploadfile = $('#uploadfile').val();

    if(uploadfile == '') {
    caseform.uploadfile.focus();
    $(".required-message").show();
    $(".file-message").show();
    return false;
        }$(".file-message").hide();
    $('#caseform').submit();
}

function manual_validate() {
    var age = $('#age').val();
    var gender = $('#gender').val();
    var subtype = $('#subtype').val();
    var treatment_names = $('input[name=treatment_name]');
    var treatment_durations = $('input[name=treatment_duration]');
    var treatment_types = $('select[name=treatment_type]');
    var stop = false;

    if (age == '') {
    caseform.age.focus();
    $(".required-message").show();
    $(".age-message").show();
    return false;
    }$(".age-message").hide();
    if(gender == null) {
    caseform.gender.focus()
    $(".required-message").show();
    $(".gender-message").show();
    return false;
    }$(".gender-message").hide();
    if(subtype == '') {
    caseform.subtype.focus()
    $(".required-message").show();
    $(".subtype-message").show();
    return false;
    }$(".subtype-message").hide();
    treatment_names.each(function() {
        if ($(this).val() == '') {
            $(".required-message").show();
            $(this).siblings('.treatment-name-message').show();
            $(this).focus();
            stop = true;
        } else {
            $(this).siblings('.treatment-name-message').hide();
        }
    });
    if (stop) { return false; }
    treatment_durations.each(function() {
        if ($(this).val() == '') {
            $(".required-message").show();
            $(this).siblings('.treatment-duration-message').show();
            $(this).focus();
            stop = true;
        } else {
            $(this).siblings('.treatment-duration-message').hide();
        }
    });
    if (stop) { return false; }
    treatment_types.each(function() {
        if ($(this).val() == '') {
            $(".required-message").show();
            $(this).siblings('.treatment-type-message').show();
            $(this).focus();
            stop = true;
        } else {
            $(this).siblings('.treatment-type-message').hide();
        }
    });
    if (stop) { return false; }



    if(treatment_name_0 == '') {
    caseform.treatment_name_0.focus()
    $(".required-message").show();
    $(".treatment-name-0-message").show();
    return false;
    }$(".treatment-name-0-message").hide();

    $('#caseform').submit();
}


function freetext_validate(){
    var gender = $('#gender').val();
    var age = $('#age').val();
    var subtype = $('#subtype').val();
    var detail = $('#details').val();


    if(age == '') {
    $('#age').focus();
    $(".required-message").show();
    $(".age-message").show();
    return false;
    }$(".age-message").hide();
    if(gender == null) {
    $('#gender').focus();
    $(".required-message").show();
    $(".gender-message").show();
    return false;
    }$(".gender-message").hide();
    if(subtype == '') {
    $('#subtype').focus();
    $(".required-message").show();
    $(".subtype-message").show();
    return false;
    }$(".subtype-message").hide();
    if(detail == '') {
    caseform.details.focus();
    $(".required-message").show();
    $(".detail-message").show();
    return false;
    }$(".detail-message").hide();

    $('#caseform').submit();

}

$('#submit-button').click(function(e){
    e.preventDefault()
    validate(e)
});

$('input[type=submit]').click(function(e) {
    if ($('#agreement').prop('checked')) {
        return true
    }
    e.preventDefault();
    $(".agree-message").show();
    return false
});

$('.agree-checkbox').click(function(){
    $(".agree-message").hide();
});


//for attachments

$(document).ready(function() {

    var max_fields      = 3; //maximum input boxes allowed
    var att_wrapper         = $(".attachments-div"); //Fields wrapper
    var add_button      = $(".add_att_button"); //Add button ID

    var x = $(".attachments-div .attachment.row").length; //initlal text box count

    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(att_wrapper).append(
                '<div class="attachment row"><div class="col-md-11">'+
                    '<div class="figure">Fig ' + x + '</div>'+
                    '<div class="form-control">'+
                        '<input type="file" name="attachment' + x + '" id="attachment' + x + '" onchange="checkfile(this);">'+
                    '</div>'+
                    '<div class="helpText">JPG, PDF, PNG, TIFF file types; max file size 2MB; minimum width 770px'+
                                          '<br/>Be sure to explicitly cite this figure\'s name in relevant text above</div>'+
                    '<label for="attachment' + x + '_title">Title</label>'+
                    '<input id="attachment' + x + '_title" name="attachment' + x + '_title" class="form-control attachment' + x + '_title">'+
                    '<label for="attachment1_description">Description</label>'+
                    '<textarea id="attachment' + x + '_description" name="attachment' + x + '_description"'+
                              'rows="4" cols="73" class="form-control attachment' + x + '_description editor"></textarea>'+
                '</div><div class="col-md-1"><a href="#" class="remove_att"><i class="fa fa-times"></i></a></div></div>'
            );
            if ($('.row.attachment').length >= max_fields) {
                add_button.hide();
            }
        }
    });

    $(att_wrapper).on("click",".remove_att", function(e){ //user click on remove text
        e.preventDefault(); $(this).parents('.row.attachment').remove();
        if ($('.row.attachment').length <= max_fields) {
            add_button.show();
        }
    });

});

