// Stolen and modified from http://www.sitepoint.com/track-outbound-links-google-analytics/
(function() {
    'use strict';
    // click event on body
    $("body").on("click", function(e) {
        // abandon if link already aborted or analytics is not available
        if (e.isDefaultPrevented() || typeof ga !== "function") return;
        // abandon if MEDIA_URL/STATIC_URL are not set, which is the case for logged in CMS admins
        if (window.MEDIA_URL === undefined || window.STATIC_URL === undefined) return;
        var links = $(e.target).closest("a");
        // abandon if no active link
        if (links.length != 1) return;

        var link = links[0];
        // Determine whether the link is for a hosted filed or not. Remote file downloads should be tracked as outbound links.
        var is_download = (link.href.indexOf(MEDIA_URL) === 0 || link.href.indexOf(STATIC_URL) === 0);
        // Check for outbound link events, local downloads should be ignored
        var is_outbound_link = link.href.indexOf(window.location.host) === -1 && !is_download;
        // Bail if we don't need to track anything
        if (!(is_download || is_outbound_link)) return;
        // cancel event and record outbound link
        e.preventDefault();
        if (is_download) {
            ga('send', {
                'hitType': 'event',
                'eventCategory': 'Files',
                'eventAction': 'Download',
                'eventLabel': link.href,
                'hitCallback': loadPage
            });
        // Don't fire if this was already tracked as a local file download.
        } else if (is_outbound_link) {
            ga('send', {
                'hitType': 'event',
                'eventCategory': 'outbound',
                'eventAction': 'link',
                'eventLabel': link.href,
                'hitCallback': loadPage
            });
        }
        // redirect after one second if recording takes too long
        setTimeout(loadPage, 1000);

        // redirect to outbound page
        function loadPage() {
            document.location = link.href;
        }
    });
})();