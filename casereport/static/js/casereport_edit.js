function ajax_edit(url, data, section_class) {
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        dataType: 'json',
        success: function (response) {
            $('.container').html(response.message);
            // $('.success-change').css('display', 'block');
            // $('.success-change').delay(2000).fadeOut();
            // this.hide_message().delay(3000);
        },
        // hide_message: function() {
        //     window.location.href = '/';

        // }

    });
}

function showEditForm(content, edit_area) {
    edit_area.each(function() {
        var field = $(this).find('.field');
        var source_text = $(this).prev('.edit_area_content');
        field.val(source_text.text().trim());
    });
    content.addClass('hide');
    edit_area.removeClass('hide');
}

function setEditedValues(edit_area) {
    data = ''
    edit_area.each(function() {
        var field = $(this).find('.field');
        var source_text = $(this).prev('.edit_area_content');
        if (field.val() != source_text.text().trim())
            data = data + '&' + field.attr('name') + '=' + field.val();
    });
    return data
}

$(document).ready(function() {
    var url = window.location.href;
    var form = $('.case_edit_form');
    var edit = form.find('.edit');
    var submit = form.find('.submit');
    var cancel = form.find('.cancel');
    var approve = form.find('.approve');
    var overlay = $('.overlay');
    var content = form.find('.edit_area_content');
    var edit_area = form.find('.edit_area');
    edit.click(function(event) {
        event.preventDefault();
        overlay.removeClass('hide');
        edit.addClass('hide');
        approve.addClass('hide');
        submit.removeClass('hide');
        cancel.removeClass('hide');
        showEditForm(content, edit_area);
        overlay.addClass('hide');
    });
    cancel.click(function(event) {
        event.preventDefault();
        overlay.removeClass('hide');
        submit.addClass('hide');
        cancel.addClass('hide');
        edit.removeClass('hide');
        approve.removeClass('hide');
        edit_area.addClass('hide');
        content.removeClass('hide');
        overlay.addClass('hide');
    });
    submit.click(function(event) {
        event.preventDefault();
        overlay.removeClass('hide');
        data = setEditedValues(edit_area);
        if (data != '') {
            data = data + '&action=' + $(this).val();
            ajax_edit(url, data, '.edit_area');
            $("#crdb-overlay-loader.active").show();
        }
        else {
            $('.no-change').css('display', 'block');
            $('.no-change').delay(2000).fadeOut();
        }
        overlay.addClass('hide');
    });
    approve.click(function(event) {
        event.preventDefault();
        overlay.removeClass('hide');
        $('.action').val($(this).val());
        ajax_edit(url, form.serialize(), '.edit_area');
        overlay.addClass('hide');
        $("#crdb-overlay-loader.active").show();
    }
    );
});
