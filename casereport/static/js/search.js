function search() {
    var url = window.location.href;
    var newquery = $("input.search").val();
    url = url.split('&')[0];
    if (url.split('?').length == 1)
        url = url + '?'
    url = url.split('q=');
    var front = url[0];
    url = front + "q=" + encodeURIComponent(newquery);
    var selected_gender =  $('.gender-section input:checked');
    selected_gender.each(function(index, el) {
        url = url + '&' + $(el).attr('data-url');
    });
    var cases_cat = $('.category-section input:checked')
    cases_cat.each(function(index, el) {
        url = url + '&' + $(this).attr('data-url');
    });
    $('select.select2').each(function(index, el) {
        vals = $(el).val();
        if (Array.isArray(vals)) {
            for (val in vals) {
                url = url + '&' + vals[val];
            }
        } else {
            url = url + '&' + vals;
        }
    });
    $('select.sorting').each(function(index, el) {
        url = url + '&' + $(el).attr('name') + '=' + $(el).val();
    });
    var age = '['+$("#amount").val().split(' - ').join('TO')+']'
    url = url + '&' + 'selected_facets=age_exact:' + age
    // ajax_search(url);
    window.location.href = url;

}

$('.search-cases').on('submit', function (e) {
    e.preventDefault();
    search();
});


function toggleChevron(e) {
    $(e.target)
        .toggleClass('glyphicon-chevron-down glyphicon-chevron-up');
}






$(document).ready(function() {
    $(".select2").select2();
    $('#ex2').slider({
        formatter: function(value) {
        return 'Current value: ' + value;
        }
    });
    if ($('.filter-section').length>0) {
        $('.filter-checkbox').each(function(index, el) {
            $(el).bind('click', function() {
                search();
            })
        });
        $('.select2').each(function(index, el) {
            $(el).bind('change', function() {
                search();
            })
        });
        $('.treat_select').each(function(index, el) {
            $(el).bind('change', function() {
                search();
            })
        });
    }
    $('#sort_button').click(function() {
        search();
    });
    if ($("#amount").length>0) {
        var minhandle = $( "#custom-min-handle" );
        var maxhandle = $( "#custom-max-handle" );
        $( "#slider-range" ).slider({
            range: true,
            min: 0,
            max: 100,
            values: $("#amount").val().split('-'),
            create: function() {
                minhandle.text( $( this ).slider( "values", 0 ) );
                var maxval;
                if ($( this ).slider( "values", 1 ) == 100) {
                    maxhandle.text( '100+' );
                } else {
                    maxhandle.text( $( this ).slider( "values", 1 ) );
                }
            },
            slide: function( event, ui ) {
                $( "#amount" ).val( "" + ui.values[ 0 ] + " - " + ui.values[ 1 ] );
                minhandle.text( ui.values[ 0 ] );
                var maxval;
                if (ui.values[ 1 ] == 100) {
                    maxhandle.text( '100+' );
                } else {
                    maxhandle.text( ui.values[ 1 ] );
                }
            },
            stop:function( event, ui ) {
                search();
            }
        });
        $( "#amount" ).val( "" + $( "#slider-range" ).slider( "values", 0 ) +
        " - " + $( "#slider-range" ).slider( "values", 1 ) );
    }

    $('body').on('click', '#moretreat', toggleChevron);
    $('body').on('click', '.sorting', function(e){
        e.preventDefault();
        return false

    });
    
    $(".notes-trigger a").click(function() {
        var notes = $("#editorial-notes");
        if ($(notes).is(":visible")) {
            $(notes).slideUp();
        } else {
            $(notes).slideDown();
        }
        return false;
    });

});

     $(function () {
        $("#sort").change(function () {
            if ($(this).val() == "created_on") {
              $('#order-sort').removeAttr('disabled');
            }
            else{

                $('#order-sort').attr('disabled', 'disabled');
            }
        });
    });

$(document).ready(function() {
    if($('.sticky').length) {
        $('body.casereport-view').scrollspy({ target: '.sticky' });
        $('.sticky').affix({
          offset: {
            top: $('.sticky').offset().top - 52,
            bottom: function () {
              if ($('.action-buttons').length > 0) {
                  return (this.bottom = $('.main-footer').outerHeight(true) + $('.action-buttons').outerHeight(true) + 20);
              } else {
                  return (this.bottom = $('.main-footer').outerHeight(true) + 20);
              }
            }
          }
        });
   }
});
