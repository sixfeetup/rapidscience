/**
 * Created by nadeemaslam on 28/1/16.
 */
     $(function () {
        $("#subtype-field").change(function () {
            if ($(this).val() == "Other") {
                $(".others").show();
                $("#other-sarcoma-field").prop('required',true);
            } else {
                $(".others").hide();
            }
        });
    });



