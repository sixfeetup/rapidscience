(function($) { $(function() {
    var max_fields = 20; //maximum input boxes allowed
    var treatment_wrapper = $(".treatment-section-form"); //Fields wrapper
    treatment_copy = $(".treatment-section-form .row").eq(0).clone();
    treatment_content = $(treatment_copy).html();
    var field_count = $(".row.treatment").length + 1; //initial text box count
    var level = 1;
    var label_value = 2;
    
    $(".add_treatment").click(function(e){ 
        e.preventDefault();
        if(field_count < max_fields){ //max input box allowed
            var new_treatment = '<a href="#" class="remove_treatment">✕</a>' + treatment_content;
            new_treatment = new_treatment.replace(/_1/g, "_" + field_count)
            $(new_treatment).find("input").val("");
            $(treatment_wrapper).append('<div class="row treatment">' + new_treatment + '</div>');
            $(".row.treatment").eq(field_count-1).find("input, textarea").val("");
            $(".row.treatment").eq(field_count-1).find("select").each(function(){
                this.selectedIndex = 0
            });
            field_count++; //text box increment
        }
        $('.remove_treatment').on("click", function(e){
            e.preventDefault();
            $(this).parent('.row').remove();
        });
        CKEDITOR.replace('treatment_outcome_' + (field_count-1), {
            language: 'en',
            skin: 'moono',
            toolbar: [
               ['Undo', 'Redo'],
               ['ShowBlocks'],
               ['Format', 'Styles'],
               ['PasteText', 'PasteFromWord'],
               ['Maximize', ''],
               '/',
               ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
               ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
               ['HorizontalRule'],
               ['Link', 'Unlink'],
               ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Table'],
               ['Source']
            ],
            allowedContent: true,
            toolbarCanCollapse: false,
            extraPlugins: '',
            width: '100%',
            height: '275px'
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
}); })(jQuery);




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










