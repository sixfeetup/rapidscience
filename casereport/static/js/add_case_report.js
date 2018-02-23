function checkfile(sender) {
    if (!sender.value) {
        return false;
    }
    var validExts = [];
    var validAttachExts = [".pdf", ".jpeg", ".jpg", '.png', '.tif', '.tiff', ".doc", ".docx"];
    var validFileExts = [".doc", ".docx", ".epub", ".html", ".odt", ".pdf", ".rtf", ".txt", ".zip"];
    var fileExt = sender.value;
    fileExt = fileExt.substring(fileExt.lastIndexOf('.')).lower();
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
    if (sender.files[0].size > 6*1024*1024) {
        message += ' File size must be smaller than 6MB.';
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
                    '<a href="#" class="remove_field">✕</a></div>'); //add input box
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

    $(".hiddenField").parents(".sharing-wrapper").hide().find("#share3").prop('checked', true);
    if ($('.action-buttons').length) {
        $(".main-footer").css({"padding-bottom": "120px"});
    }

    // sharing fields
    var sharing_fields = $("#sharing-field-members, #sharing-field-external, #sharing-field-groups, #sharing-field-comment")
    $(".sharing-wrapper .choices input").click(function(){
        $(sharing_fields).hide()
        if ($(this).val() == 'share-all') {
            $("#sharing-field-comment").show();
        } else if ($(this).val() == 'share-pick') {
            $(sharing_fields).show()
        }
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

    $(document).ready(function() {
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
        var mode = $("#caseform").data('mode');
        console.log("mode: '" + mode + "'");
        if (mode) {
            $(".radiobut[value=" + mode + "]").trigger("click");
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
                    '<a href="#" class="remove_field">✕</i></a></div>'); //add input box
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



//for coauthors

$(document).ready(function() {
    var max_fields      = 20; //maximum input boxes allowed
    var coauthor_wrapper         = $(".coauthor-div"); //Fields wrapper
    var add_button      = $(".add_coauthor_button"); //Add button ID

    var x = $(".coauthor-div .row.coauthor").length; //initlal text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(coauthor_wrapper).append(
                '<div class="row coauthor"><div class="form-group col-md-6">' +
                '<label for="coauthor_name' + x + '">Add Co-Author Name (If Non-Member)</label>' +
                '<input name="coauthor_name" type="text" class="form-control" id="coauthor_name' + x + '" placeholder="First and Last Name">'+
                '<div class="helpText">' +
                    'ex: John Smith, MD, PhD' +
                '</div>' +
                '</div><div class="form-group col-md-5">' +
                '<label for="coauthor_email' + x + '">Add Co-Author Email (If Non-Member)</label>' +
                '<input name="coauthor_email" type="EMAIL" class="form-control" id="coauthor_email' + x + '" placeholder="Email">'+
                '<div class="helpText">' +
                    'Please use an institutional email address' +
                '</div>' +
                '</div><div class="col-md-1"><a href="#" class="remove_coauthor">✕</a></div></div>'
            );
            if ($('.row.coauthor').length > 0) {
                $(".add_coauthor_button_text").text('Add another non-member as a co-author');
            }
            if ($('.row.coauthor').length >= max_fields) {
                add_button.hide();
            }
        }
    });

    $(coauthor_wrapper).on("click",".remove_coauthor", function(e){ //user click on remove text
        e.preventDefault(); $(this).parents('.row.coauthor').remove();
        if ($('.row.coauthor').length == 0) {
            $(".add_coauthor_button_text").text('Add a non-member as a co-author(s)');
        }
        if ($('.row.coauthor').length <= max_fields) {
            $(".add_coauthor_button").show();
        }
    })

});


function validate(ev) {
    ev.preventDefault()
    $(".required-message").hide();
    var radio = $('.radiobut').val();
    var subtype = $('#subtype').val();
    var subtypeOther = $('#subtype-other').val();
    var e = $('.radiobut:checked').length > 0;
    if (e != true) {
        $(".radiobut").focus();
        $(".radio-box .choose-message").show();
        return false;
    }

    if(subtype == '' && subtypeOther == '') {
        caseform.subtype.focus()
        $(".required-message").show();
        $(".subtype-message").show();
    return false;
    }$(".subtype-message").hide();
    $(".choose-message").hide();
    if (!$('#consent').prop('checked')) {
        $(".agree-message").show();
        window.location = '#consent-wrapper';
        $('#consent').focus();
        return false;
    } else {
        $(".agree-message").hide();
    }
    var sharing = $("input[name='sharing-options']:checked").val();
    if (!sharing) {
        $("input[name='sharing-options']").focus();
        $(".choices .choose-message").show();
        return false;
    }
    if ($("#id_radio3").is(':checked')) {
        return file_validate();
    } else if ($("#id_radio1").is(':checked')) {
        return manual_validate();
    } else {
        return freetext_validate();
    }
}


function file_validate() {
    var uploadfile = $('#uploadfile').val();

    if(uploadfile == '' && !casefile_exists) {
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
    if (stop) { return false; }

    $('#caseform').submit();
}


function freetext_validate(){
    var gender = $('#gender').val();
    var age = $('#age').val();


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

    $('#caseform').submit();

}

$('#draftsave').click(function(e){
    $("#save-final").val('');
    e.preventDefault()
    validate(e)
});
$('#finalsave').click(function(e){
    $("#save-final").val('True');
    e.preventDefault()
    validate(e)
});

$('.agree-checkbox').click(function(){
    $(".agree-message").hide();
});


//for attachments

$(document).ready(function() {

    var max_fields      = 3; //maximum input boxes allowed
    var att_wrapper         = $(".attachments-div"); //Fields wrapper
    var add_button      = $(".add_att_button"); //Add button ID


    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        var x = $(".attachments-div .attachment.row").length;
        var new_num = 0
        if ($("#attachment1").length == 0) {
            new_num = 1;
        } else if ($("#attachment2").length == 0) {
            new_num = 2;
        } else if ($("#attachment3").length == 0) {
            new_num = 3;
        }
        if(x < max_fields){ //max input box allowed
            x++; //text box increment
            $(att_wrapper).append(
                '<div class="attachment row"><div class="col-md-11">'+
                    '<div class="figure">File ' + x + '</div>'+
                    '<div class="form-control">'+
                        '<input type="file" name="attachment' + new_num + '" id="attachment' + new_num + '" onchange="checkfile(this);">'+
                    '</div>'+
                    '<div class="helpText">JPG, PDF, PNG, TIFF, DOCX/DOC file types; max file size 6MB; minimum image width 770px'+
                                          '<br/>Be sure to explicitly cite this file\'s name in relevant text below</div>'+
                    '<label for="attachment' + new_num + '_title">Title</label>'+
                    '<input id="attachment' + new_num + '_title" name="attachment' + new_num + '_title" class="form-control attachment' + new_num + '_title">'+
                    '<label for="attachment' + new_num + '_description">Description</label>'+
                    '<textarea id="attachment' + new_num + '_description" name="attachment' + new_num + '_description"'+
                              'rows="4" cols="73" class="form-control attachment' + new_num + '_description editor"></textarea>'+
                '</div><div class="col-md-1"><a href="#" class="remove_att">✕</a></div></div>'
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

    // open the first attachment field
    if ($('.attachments-div .attachment').length == 0){
        $('.add_att_button').trigger("click");
    }

});

