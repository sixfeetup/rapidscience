var selectedBookmarksFolderName; // will contain ID of selected bookmarks folder

(function($) { $(function() {
    // Magical spell to count characters
    $('.remaining-characters').each(function() {
        var maxLength = $(this).attr('maxlength');
        var length = $(this).val().length;
        var length = maxLength-length;
        var paragraph = '<p class="character-count">'+ length + '/' + maxLength + '</p>';
        if (!$(this).hasClass('comment-field')) {
            $(this).after(paragraph);
        }
    });
    $('.remaining-characters').keyup(function() {
        var maxLength = $(this).attr('maxlength');
        var length = $(this).val().length;
        var length = maxLength-length;
        if ($(this).hasClass('comment-field')) {
            $(this).parent().find('.character-count').text(length + '/' + maxLength + " characters");
        } else {
            $(this).next('.character-count').text(length + '/' + maxLength);
        }
    });

    // add space to footer when .buttonbar is present
    if ($('.buttonbar, .action-buttons, .float-buttons').length) {
        $(".main-footer").css({"padding-bottom": "120px"});
    }

    // var showChar = 170;
    // var ellipsestext = '&hellip;';
    // var moretext = '+';
    // var lesstext = '-';

    // More or less
    // $('.more').each(function() {
    //     var content = $(this).html();

    //     if(content.length > showChar) {

    //         var c = content.substr(0, showChar);
    //         var h = content.substr(showChar, content.length - showChar);

    //         var html = c + '<span class="moreellipses">' + ellipsestext+ '&nbsp;</span><span class="morecontent"><span>' + h + '</span>&nbsp;<a href="" class="morelink">' + moretext + '</a></span>';

    //         $(this).html(html);
    //     }

    // });

    // $('.container').on('click', '.morelink', function(event){
    //     if($(this).hasClass('less')) {
    //         $(this).removeClass('less');
    //         $(this).html(moretext);
    //     } else {
    //         $(this).addClass('less');
    //         $(this).html(lesstext);
    //     }
    //     $(this).parent().prev().toggle();
    //     $(this).prev().toggle();
    //     return false;
    // });

    // hide hiddenField wrappers
    $(".hiddenField").parent(".fieldWrapper").hide();

    // Clear comment field
    $(".comment-form button[type=reset]").click(function(){
        form_id = $(this).parents("form").find('.django-ckeditor-widget').attr('data-field-id');
        CKEDITOR.instances[form_id].setData('');
    });
    // Make search input active
  $(".search-icon").click(function(){
      setTimeout(function() { $('.navbar-nav .search-widget input.form-control').focus() }, 500);
  })

}); })(jQuery);

// Collapse forms on cancel
$('.cancel-button-collapse').on('click', function(event) {
    event.preventDefault();
    $(this).closest('.collapse').collapse('hide');
});

// Utility to dynamically fetch forms shown in modals so we don't bloat the HTML with hundreds of pre-rendered forms
$('.modal').on('shown.bs.modal', function (event) {
    // Get the action from the form, this is where we'll fetch the form from
    var form = $(this).find('form');
    var form_url = $(form).attr('action')  + "?preventCache=" + $.now();
    selectedBookmarksFolderName = ''; // may be set on prev.actions, so clear it
    $.get(form_url, function(data) {
        // Replace .modal-body with the results
        $(form).find('.modal-body').html(data.form);
        $(form).find('.chosen-select').chosen({ // share modal window
            placeholder_text_multiple: 'Choose a recipient'
        });
        // Add placeholder text for field
        $(form).find('#id_name').attr("placeholder", "Bookmark title. Leave empty for default.");
        // Show/hide block with New Folder input and save button
        $(form).parent().find('.btn-add-folder').off('click').on('click', function(event){
            $(form).find('.form-group-new-folder-title').toggle("100");
            $(form).find('#id_folder_title').focus();
        });
        initFolderList(form);
        // Click on AddNewFolder icon
        $(form).find('.btn-add-new-folder').off('click').on('click', function(event){
            // debugger;
            event.preventDefault();
            var editblock = $(this).parents('.form-group-new-folder-title');
            var folderName = $(form).find('#id_folder_title').val();
            var urlFolderAdd = $(form).find('#id_folder_title').data('url-folder-add');
            var CSRF = $('[name="csrfmiddlewaretoken"]').val();
            if (folderName) {
                $.post(urlFolderAdd, {'name':folderName, 'csrfmiddlewaretoken': CSRF}, function(data) {
                    if (data.messages) {
                        setMessageForActiveModal(data.messages)
                    }
                    if (data.error == false) {
                        editblock.hide();
                        // Add new folder in the list
                        selectedBookmarksFolderName = data.folder_id;
                        var a = '<li class="bookmarks-folder" data-name="' +
                                data.folder_id + '"><a href="#"><i class="fa fa-folder"></i>' +
                                data.folder_name + '</a></li>';
                        $(form).find('.bookmarks-list').prepend(a);
                        initFolderList(form);
                    }
                });
            } else {
                setMessageForActiveModal('<div class="alert alert-warning">You should enter new folder name before saving</div>');
            }
        });
    });
});

// Get active modal window
function getActiveModal() {
    return $(".modal.in");
}


//
// SHARE MODAL WINDOW
//

// Save share window: submit form
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

// Share modal window: clear select list
$('.activity-actions').on('hidden.bs.modal', function (event) {
    $('.chosen-select', this).chosen('destroy');
});


//
// BOOKMARK MODAL WINDOW
//

// Set message for active (visible) bookmark modal window
function setMessageForActiveModal(message) {
    getActiveModal().find('.status-message').html(message);
}

// Bookmarks modal: save bookmark (submit form), set message and close modal
$('.container').on('submit', 'form.bookmark', function(event) {
    event.preventDefault();
    var form = $(this);
    var actions = form.parents('.activity-actions');
    $.post(form.attr('action'), form.serialize(), function(data) {
        if (data.messages) {
            // Clear out any old messages
            $('.alert').remove();
            form.parents('.activity-stream').prepend(data.messages);
        }
        if (data.form) {
            form.replaceWith(data.form);
        }
        // hide active modal
        getActiveModal().modal('hide');
        // New bookmark successfully added, block action link to prevent showing modal again
        actions.find('.bookmark-widget button').attr('title','Item already bookmarked').attr('disabled','');
    });
});

// Init folder selection on click
function initFolderList(form) {
    var folders = $(form).find('.bookmarks-folder');
    for (i = 0; i < folders.length; i++) {
        var folder = $(folders[i]);
        if(folder.data('name') == selectedBookmarksFolderName) {
            $(form).find('#id_folder').attr('value', selectedBookmarksFolderName); // Add selected folder ID to hidden INPUT
            folder.addClass('selected');
        }
    }
    folders.off('click').on('click', function(event){
        event.preventDefault();
        folders.removeClass('selected'); // Clear all folders from .selected class
        $(this).addClass('selected'); // Set .selected class for clicked folder
        $(form).find('#id_folder').attr('value', $(this).attr('data-name')); // Add selected folder ID to hidden INPUT
    });
}


//
// PROFILE BOOKMARKS TAB
//

// Profile bookmarks tab: show AddFolder form on .link-create-folder click
$('.tab-pane#bookmarks .link-create-folder').click(function(event){
    event.preventDefault();
    $('#bookmarks-tab-add-folder-form').toggle("100");
    $('#id_folder_title').focus();
});

// Profile bookmarks tab: Update bookmark title and reload page
$('.btn-edit-bookmark-title').click(function(event) {
    event.preventDefault();
    var form = $(this).parents('.bookmark-edit-form');
    var i = form.find('input.form-control');
    var urlBookmarkUpdate = i.data('url-bookmark-update');
    var bookmarkName = i.val();
    var folderID = i.data('folderid');
    var CSRF = $('[name="csrfmiddlewaretoken"]').val();
    $.post(urlBookmarkUpdate, {'name':bookmarkName, 'folder':folderID, 'csrfmiddlewaretoken': CSRF}, function(data) {
        if (data.messages) {
            form.parents('.bookmarks-single-item').find('.status-message').html(data.messages)
        }
        if (data.error == false) {
            // New folder successfully added
            form.find('.bookmark-edit-form-wrapper').hide(); // Hide edit elements
            location.reload(); //reload page to display it
        }
    });
});

// Profile bookmarks tab: add new folder on button .btn-add-new-folder click
$('#bookmarks-tab-add-folder-form .btn-add-new-folder').click(function(event) {
    event.preventDefault();
    var form = $(this).parents('form');
    var folderName = $('#id_folder_title').val();
    var urlFolderAdd = $(form).find('#id_folder_title').data('url-folder-add');
    var CSRF = $('[name="csrfmiddlewaretoken"]').val();
    if (folderName) {
        $.post(urlFolderAdd, {'name':folderName, 'csrfmiddlewaretoken': CSRF}, function(data) {
            if (data.messages) {
                form.find('.status-message').html(data.messages)
            }
            if (data.error == false) {
                // New folder successfully added, reload page to display it
                location.reload();
            }
        });
    }
});

// Profile bookmarks tab: remove bookmark and reload page
$('.action-remove').click(function(event) {
    event.preventDefault();
    var urlBookmarkDelete = $(this).data('url-bookmark-delete');
    var CSRF = $('[name="csrfmiddlewaretoken"]').val();
    $.post(urlBookmarkDelete, {'csrfmiddlewaretoken': CSRF}, function(data) {
        if (data.error == false) {
            // New folder successfully added, reload page to display it
            location.reload();
        } else {
            setMessageForActiveModal('<div class="alert alert-warning">Some error occured, can\'t delete this bookmark</div>');
        }
    });
});

// Profile bookmarks tab: toggle internal edit form on .action-edit click for bookmark items
$('.action-edit').click(function(event){
    event.preventDefault();
    $(this).parents('.bookmarks-single-item').find('.bookmark-edit-form-wrapper').toggle('100');
});

// Group invite overlay
$(".invite-link").click(function(){
    $("#project-invite").fadeIn();
    $("body").addClass("overlay-active");
});
$(".close-overlay").click(function(){
    $(".overlay-form").fadeOut();
    $("body").removeClass("overlay-active");
});

// Edit Group overlay
/* disabled in favor of page-based forms
$(".edit-group-link").click(function(){
    $("#edit-group").fadeIn();
    $("body").addClass("overlay-active");
});
$(".close-overlay").click(function(){
    $(".overlay-form").fadeOut();
    $("body").removeClass("overlay-active");
});
*/


// Open Discussion form if #topic-form in path
(function($) { $(function() {
    if (window.location.hash == '#topic-form') {
        $("#topic-form").removeClass("collapse");
    }
    $("#topic-form .cancel-button-collapse").click(function(){
        $("#topic-form").addClass("collapse");
    });
}); })(jQuery);

// check for content in a field
$(".clear-input").on('input, keyup', function() {
    if ($(this).val() == '') {
        $(this).siblings('.glyphicon-remove').css('display', 'none');
    } else {
        $(this).siblings('.glyphicon-remove').css('display', 'block');
    }
});

// clear content of a field
$(".clear-input+.glyphicon-remove").on('click', function(){
    $(this).siblings('.clear-input').val('');
    $(".clear-input").keyup();
});

// on submit of refine, copy potentially changed keywords from search input
$(".sub-menu").on('submit', function(e) {
    $("#id_q_hidden").val($("#id_q").val());
});

(function($) { $(function() {
  // Display help_text over the email address field in The registration form
  $("#id_register-email").before("<p class='helptext'> Use your professional email address when applicable</p>");

  // don't allow browsers provide suggestions on 'New Tags'
  $("#id_new_tags").attr("autocomplete", "off");

  // Display text below "My Groups"
  $("#id_groups").before("<p>Note: when an item is posted from a <i>Group Dashboard</i>, it is automatically shared with that Group.</p>");

  // Display help text over header add links
  $(".add-links-info").on('click', function(){
    $(".add-links-info-text").fadeIn(300);
  });
  $(".add-links-info-text").on('click', function(){
    $(this).fadeOut(300);
  });

}); })(jQuery);
