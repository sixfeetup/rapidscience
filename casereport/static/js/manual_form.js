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
    var max_fields = 20; //maximum input boxes allowed
    var treatment_wrapper = $(".treatment-section-form"); //Fields wrapper
    var treatment_content = $(".treatment-section-form .form-group").html();
    var field_count = 1; //initial text box count
    var level = 1;
    var label_value = 2;
    
    $(".add_treatment").click(function(e){ 
        e.preventDefault();
        if(field_count < max_fields){ //max input box allowed
            var new_treatment = '<a href="#" class="remove_treatment"><i class="fa fa-times"></i></a>' + treatment_content;
            new_treatment = new_treatment.replace(/_0/g, "_" + field_count)
            $(treatment_wrapper).append('<div class="form-group row">' + new_treatment + '</div>');
            field_count++; //text box increment
        }
        $('.remove_treatment').on("click", function(e){
            e.preventDefault();
            console.log("OH HAI");
            $(this).parent('.form-group').remove();
        });
    });

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

            }}
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










