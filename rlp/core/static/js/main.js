var selectedBookmarksFolderName; // will contain ID of selected bookmarks folder

function remaining_characters(){
    // Magical spell to count characters
    $('.remaining-characters').each(function() {
        var maxLength = $(this).attr('maxlength');
        var length = $(this).val().length;
        var length = maxLength-length;
        var paragraph = '<p class="character-count">'+ length + '/' + maxLength + '</p>';
        $(this).after(paragraph);
    });
    $('.remaining-characters').keyup(function() {
        var maxLength = $(this).attr('maxlength');
        var length = $(this).val().length;
        var length = maxLength-length;
        $(this).next('.character-count').text(length + '/' + maxLength);
    });
}

$(document).on('ready', remaining_characters);

var showChar = 170;
var ellipsestext = '&hellip;';
var moretext = '+';
var lesstext = '-';

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

// Open Discussion form if #topic-form in path
(function($) { $(function() {
    if (window.location.hash == '#topic-form') {
        $("button[href='#topic-form']").click();
    }
}); })(jQuery);
