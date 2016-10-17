function remaining_characters(){
    // Magical spell to count characters
    $('.remaining-characters').one('focus', function() {
        var maxLength = $(this).attr('maxlength');
        var length = $(this).val().length;
        var length = maxLength-length;
        var paragraph = '<p class="character-count">You have ' + length + ' characters remaining</p>';
        $(this).after(paragraph);
    });
    $('.remaining-characters').keyup(function() {
        var maxLength = $(this).attr('maxlength');
        var length = $(this).val().length;
        var length = maxLength-length;
        $(this).next('.character-count').text('You have ' + length + ' characters remaining');
    });
}
$(document).on('ready', remaining_characters);

var showChar = 170;
var ellipsestext = '...';
var moretext = 'more';
var lesstext = '<br><br>less';

// More or less
function show_more() {
    $('.more').each(function() {
        var content = $(this).html();

        if(content.length > showChar) {

            var c = content.substr(0, showChar);
            var h = content.substr(showChar, content.length - showChar);

            var html = c + '<span class="moreellipses">' + ellipsestext+ '&nbsp;</span><span class="morecontent"><span>' + h + '</span>&nbsp;<a href="" class="morelink">' + moretext + '</a></span>';

            $(this).html(html);
        }

    });
}

$(document).on('ready', show_more);

$('.container').on('click', '.morelink', function(event){
    if($(this).hasClass('less')) {
        $(this).removeClass('less');
        $(this).html(moretext);
    } else {
        $(this).addClass('less');
        $(this).html(lesstext);
    }
    $(this).parent().prev().toggle();
    $(this).prev().toggle();
    return false;
});

// Collapse forms on cancel
$('.cancel-button-collapse').on('click', function(event) {
    event.preventDefault();
    $(this).closest('.collapse').collapse('hide');
});

$('.container').on('submit', 'form.bookmark', function(event) {
  var form = $(this);
  event.preventDefault();
  $.post($(form).attr('action'), $(form).serialize(), function(data) {
    if (data.messages) {
      // Clear out any old messages
      $('.alert').remove();
      $(form).parents('.activity-stream').prepend(data.messages);
    }
    if (data.form) {
      $(form).replaceWith(data.form);
    }
  });
});

$('.container').on('submit', 'form.share', function(event) {
  var form = $(this);
  event.preventDefault();
  $.post($(form).attr('action'), $(form).serialize(), function(data) {
    if (data.messages) {
      // Clear out any old messages
      $('.alert').remove();
      $(form).children('.modal-body').prepend(data.messages);
    }
    if (data.form) {
      $(form).children('.modal-body').empty();
      $(form).children('.modal-body').html(data.form);
      $(form).find('.chosen-select').chosen({
        placeholder_text_multiple: 'Choose a recipient'
      });
    }
  });
});

$('.activity-actions').on('shown.bs.modal', function (event) {
  // Get the action from the form, this is where we'll fetch the form from
  var form = $(this).find('form.share');
  var form_url = $(form).attr('action');
  $.get(form_url, function(data) {
    // Replace .modal-body with the results
    $(form).find('.modal-body').html(data.form);
    $(form).find('.chosen-select').chosen({
      placeholder_text_multiple: 'Choose a recipient'
    });
  });
});
$('.activity-actions').on('hidden.bs.modal', function (event) {
  $('.chosen-select', this).chosen('destroy');
});
