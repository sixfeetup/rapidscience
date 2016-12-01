$(document).ready(function() {
    var max_fields      = 20; //maximum input boxes allowed
    var new_wrapper         = $(".molecular-abberations"); //Fields wrapper
    var add_button      = $(".add_button"); //Add button ID

    var field_count = 1; //initial text box count
    $(add_button).click(function(e){ //on add input button click
        e.preventDefault();
        if(field_count < max_fields){ //max input box allowed
            field_count++; //text box increment
            $(new_wrapper).append('<div><label for="comment">Genetic Abberations:</label>' +
                            '<div class="row ">'+
                            '<div class="form-group col-xs-6">'+
                            '<input name="test" class="form-control test" ></div>'+
                            '<div class="form-group col-xs-6">'+
                          '<input type="text" name="test_result" class="form-control"></div>'+
                    '<a href="#" class="remove_field"><i class="fa  fa-times"></i></a></div>'); //add input box
        }
    });

    $(new_wrapper).on("click",".remove_field", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent().parent('div').remove();
        field_count--;
    })


});


//$(document).ready(function() {
//    var max_fields      = 20; //maximum input boxes allowed
//    var wrapper         = $(".authors-div"); //Fields wrapper
//    var add_button      = $(".add_field_button"); //Add button ID
//
//    var x = 1; //initlal text box count
//    $(add_button).click(function(e){ //on add input button click
//        e.preventDefault();
//        if(x < max_fields){ //max input box allowed
//            x++; //text box increment
//            $(wrapper).append('<div class="form-group"><label for="title">Authorized Email:</label>' +
//                    '<input  class="form-control col-md-11" id="author_email" type="email" placeholder=""name="author"/>' +
//                    '<a href="#" class="remove_field"><i class="fa  fa-times"></a></div>'); //add input box
//        }
//    })
//    $(wrapper).on("click",".remove_field", function(e){ //user click on remove text
//        e.preventDefault(); $(this).parent('div').remove(); x--;
//    })
//});

$(document).ready(function() {
    var max_fields      = 20; //maximum input boxes allowed
    var treatment_wrapper         = $(".treatment-section-form"); //Fields wrapper
    var button      = $(".add_treatment"); //Add button ID
    var level = 1;
    var label_value = 2;
    var field_count = 1; //initlal text box count
    $(button).click(function(e){ //on add input button click
        e.preventDefault();
        if(field_count < max_fields){ //max input box allowed
            field_count++; //text box increment
            $(treatment_wrapper).append('<div class="treatment-section-extra"><label><h4>Treatment Section</h4></label>'+
        '<div class="form-group row">'+
          '<div class="col-md-8 col-xs-6">'+
          '<label class="treatment_label">Treatment Type ('+label_value+'):</label>'+
                      '<select name="treatment_type_'+level+'" class="form-control treatment_type">'+
                          '<option value="" selected>Select Treatment Type</option>'+
                          '<option value="Chemoradiotherapy">Chemoradiotherapy</option>'+
                          '<option value="Radiotherapy">Radiotherapy</option>'+
                          '<option value="Surgery">Surgery</option>'+
                          '<option value="Systemic Therapy">Systemic Therapy</option>'+
                      '</select></div></div>'+
                 '<div class="form-group">'+
                '<label >Treatment Name:</label>'+
                '<input name="treatment_name" class="form-control treatment_name" >'+
            '</div>'+
            //'<div class="chemo-section" ><!--chemo-section start -->'+
            //   ' <div class="form-group row">'+
            //    '  <div class="col-xs-4">'+
            //       ' <label >Treatment length:</label>'+
            //         ' <input name="treatment_length_'+i+'" class="form-control">'+
            //      '</div>'+
            //      '<div class="col-xs-4">'+
            //        '<label >Dose:</label>'+
            //        '<input name="dose_'+i+'" class="form-control" >'+
            //      '</div>'+
            //        '<div class="col-xs-4">'+
            //         '<label >Number of cycles:</label>'+
            //        '<div class="input-group">'+
            //          '<span class="input-group-btn">'+
            //              '<button type="button" class="btn btn-default btn-number" data-type="minus" data-field="cycles_'+i+'">'+
            //                  '<span class="glyphicon glyphicon-minus"></span>'+
            //              '</button>'+
            //          '</span>'+
            //          '<input type="text" name="cycles_'+i+'" class="form-control input-number" onkeypress="return isNumberKey(event)" value="1" min="1" max="100">'+
            //          '<span class="input-group-btn">'+
            //              '<button type="button" class="btn btn-default btn-number" data-type="plus" data-field="cycles_'+i+'">'+
            //                  '<span class="glyphicon glyphicon-plus"></span>'+
            //              '</button>'+
            //          '</span>'+
            //     '</div>'+
            //      '</div>'+
            //    '</div>'+
                 '<div class="row ">'+
                    '<div class="form-group col-xs-4">'+
                        '<label >Performance Status:</label>'+
                        '<select name="status_'+level+'" class="form-control">'+
                        '<option value="" disabled selected>select performance status</option>'+
                        '<option value="0">0</option>'+
                        '<option value="1">1</option>'+
                        '<option value="2">2</option>'+
                        '<option value="3">3</option>'+
                        '<option value="4">4</option>'+
                        '<option value="5">5</option>'+
                    '</select></div>'+
                    '<div class="form-group col-xs-4">'+
                        '<label >Tumor Size(post-treatment):</label>'+
                        '<input type="text" name="tumor_size_'+level+'"   class="form-control" ></div>' +
                '<div class="form-group col-xs-4">'+
                      '<label >Objective Response:</label>'+
                      '<select name="objective_response_'+level+'" class="form-control" id="response" >'+
                          '<option value="">select</option>'+
                          '<option value="SD">Stable Disease</option>'+
                          '<option value="PR">Partial Response</option>'+
                          '<option value="PD">Progressive Disease</option>'+
                          '<option value="CR">Complete Response</option>'+
                      '</select>'+
                    '</div>'+
                '</div>'+
                // '</div><!--chemo-section-end -->'+
                // '<div class="non-chemo-section" >'+
                //'</div>'+

         '<div class="form-group">'+
          '<label >Treatment Notes/Outcome:</label>'+
          '<textarea name="treatment_outcome_'+level+'" class="form-control editor" rows="5" cols="73" id="editor" placeholder="E.g., treatment length, dose/cycle, response, time to progression, adverse events"></textarea></div>'+
                '<a href="#" class="remove_section"><i class="fa  fa-times">Remove Treatment</i></a></div>'); //add input box
         //$('.treatment_type').select2();

        //$(".treatment_type").each(function(index, el) {
        //    $(el).change(function () {
        //        var form_group = $(this).parent('.form-group');
        //        var treatment_section = form_group.parent('.treatment-section-extra');
        //        if ($(this).val() == "Chemotherapy") {
        //            treatment_section.find(".chemo-section").show();
        //            treatment_section.find(".non-chemo-section").hide();
        //        } else {
        //            treatment_section.find(".non-chemo-section").show();
        //            treatment_section.find(".chemo-section").hide();
        //        }
        //        var val = $(this).val();
        //        if(val)
        //            treatment_section.find(".treatment_name").prop('required', true);
        //        else
        //            treatment_section.find(".treatment_name").prop('required', false);
        //    });
        //  });

//btn increment decrement
$('.btn-number').click(function(e){
    e.preventDefault();

    fieldName = $(this).attr('data-field');
    type      = $(this).attr('data-type');
    var input = $("input[name='"+fieldName+"']");
    var currentVal = parseInt(input.val());
    if (!isNaN(currentVal)) {
        if(type == 'minus') {

            if(currentVal > input.attr('min')) {
                input.val(currentVal - 1).change();
            }
            if(parseInt(input.val()) == input.attr('min')) {
                $(this).attr('disabled', false);
            }

        } else if(type == 'plus') {

            if(currentVal < input.attr('max')) {
                input.val(currentVal + 1).change();
            }
            if(parseInt(input.val()) == input.attr('max')) {
                $(this).attr('disabled', false);
            }

        }}});
        }
        level++;
        label_value++;
    });


    $(treatment_wrapper).on("click",".remove_section", function(e){ //user click on remove text
        e.preventDefault(); $(this).parent('div').remove();
        level--;
        var field_label = $('.treatment_label');
        var index;
        var count = 1;
        for (index = 0; index < field_label.length; ++index) {
            count++;
            field_label[index].textContent = 'Treatment Type ('+count+ '):'
        }
        label_value=field_count--;
    })
});



 //$('.treatment_type').select2();

    //
    // $(function () {
    //    $(".treatment_type").change(function () {
    //        var form_group = $(this).parent('.form-group');
    //        var treatment_section = form_group.parent('.treatment-section-form');
    //        if ($(this).val() == "Chemotherapy") {
    //            treatment_section.find(".chemo-section").show();
    //            treatment_section.find(".non-chemo-section").hide();
    //        } else {
    //            treatment_section.find(".non-chemo-section").show();
    //            treatment_section.find(".chemo-section").hide();
    //        }
    //        var val = $(this).val();
    //        if(val)
    //            $(treatment_section.find(".treatment_name")[0]).prop('required', true);
    //        else
    //            $(treatment_section.find(".treatment_name")[0]).prop('required', false);
    //    });
    //});





$('.btn-number').click(function(e){
    e.preventDefault();

    fieldName = $(this).attr('data-field');
    type      = $(this).attr('data-type');
    var input = $("input[name='"+fieldName+"']");
    var currentVal = parseInt(input.val());
    if (!isNaN(currentVal)) {
        if(type == 'minus') {

            if(currentVal > input.attr('min')) {
                input.val(currentVal - 1).change();
            }
            if(parseInt(input.val()) == input.attr('min')) {
                $(this).attr('disabled', false);
            }

        } else if(type == 'plus') {

            if(currentVal < input.attr('max')) {
                input.val(currentVal + 1).change();
            }
            if(parseInt(input.val()) == input.attr('max')) {
                $(this).attr('disabled', false);
            }

        }}});


function isNumberKey(evt)
      {
         var charCode = (evt.which) ? evt.which : event.keyCode
         if (charCode != 46 && charCode > 31 && (charCode < 48 || charCode > 57))
            return false;

         return true;
      }










