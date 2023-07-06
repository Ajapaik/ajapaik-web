(function() {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    /*global gtag*/
    /*global isMapview*/
    // Geotagger events
    window.reportGeotaggerMapClick = function() {
        gtag('event', 'click', { 'category': 'geotagger', 'label': 'map', 'value': 0 });
    };
    window.reportGeotaggerMapDragstart = function() {
        gtag('event', 'map_drag_start', {
            'category': 'geotagger',
            'label': 'geotagging',
            'value': 0,
        });
    };
    window.reportGeotaggerMapDragstartFeedback = function() {
        gtag('event', 'map_drag_start', {
            'category': 'geotagger',
            'label': 'feedback',
            'value': 0,
        });
    };
    window.reportGeotaggerMarkerDragend = function() {
        gtag('event', 'map_drag_end', { 'category': 'geotagger', 'label': null, 'value': 0 });
    };
    window.reportGeotaggerFullScreenOpen = function(id) {
        gtag('event', 'fullscreen', {
            'category': 'geotagger',
            'label': id.toString(),
            'value': 0,
        });
    };
    window.reportGeotaggerStreetPanoramaOpen = function(id) {
        gtag('event', 'open_streetview', {
            'category': 'geotagger',
            'label': id.toString(),
            'value': 0,
        });
    };
    window.reportGeotaggerMapUnlock = function(id) {
        gtag('event', 'unlock_map', { 'category': 'geotagger', 'label': id.toString(), 'value': 0 });
    };
    window.reportGeotaggerMapLock = function(id) {
        gtag('event', 'lock_map', { 'category': 'geotagger', 'label': id.toString(), 'value': 0 });
    };
    window.reportGeotaggerShowSearch = function(id) {
        gtag('event', 'show_search', {
            'category': 'geotagger',
            'label': id.toString(),
            'value': 0,
        });
    };
    window.reportGeotaggerSearch = function(term) {
        gtag('event', 'search', { 'category': 'geotagger', 'label': term, 'value': 0 });
    };
    window.reportGeotaggerShowDescription = function(id) {
        gtag('event', 'show_description', {
            'category': 'geotagger',
            'label': id.toString(),
            'value': 0,
        });
    };
    window.reportGeotaggerFlip = function(id) {
        gtag('event', 'flip', { 'category': 'geotagger', 'label': id.toString(), 'value': 0 });
    };
    window.reportGeotaggerSkip = function(id) {
        gtag('event', 'skip', { 'category': 'geotagger', 'label': id.toString(), 'value': -25 });
    };
    window.reportGeotaggerSaveLocationOnly = function(id) {
        gtag('event', 'save_location', {
            'category': 'geotagger',
            'label': id.toString(),
            'value': 50,
        });
    };
    window.reportGeotaggerSaveLocationAndDirection = function(id) {
        gtag('event', 'save_location_with_direction', {
            'category': 'geotagger',
            'label': id.toString(),
            'value': 100,
        });
    };
    window.reportGeotaggerShowInstructions = function() {
        gtag('event', 'show_instructions', {
            'category': 'geotagger',
            'label': null,
            'value': 0,
        });
    };
    window.reportGeotaggerHideInstructions = function() {
        gtag('event', 'hide_instructions', {
            'category': 'geotagger',
            'label': null,
            'value': 0,
        });
    };
    window.reportGeotaggerSendFeedback = function(value) {
        gtag('event', 'send_feedback', {
            'category': 'geotagger',
            'label': value.toString(),
            'value': 25,
        });
    };
    window.reportGeotaggerCorrect = function() {
        gtag('event', 'tag_feedback', {
            'category': 'geotagger',
            'label': 'correct',
            'value': 100,
        });
    };
    window.reportGeotaggerIncorrect = function() {
        gtag('event', 'tag_feedback', {
            'category': 'geotagger',
            'label': 'incorrect',
            'value': -25,
        });
    };
    window.reportGeotaggerNewlyMappedPhoto = function() {
        gtag('event', 'tag_feedback', {
            'category': 'geotagger',
            'label': 'first',
            'value': 200,
        });
    };
    window.reportDaterOpen = function() {
        gtag('event', 'click_menu_item', { 'category': 'dater', 'label': 'open', 'value': 0 });
    };
    window.reportCloseDater = function() {
        gtag('event', 'click_menu_item', { 'category': 'dater', 'label': 'close', 'value': 0 });
    };
    window.reportDaterOpenTutorial = function() {
        gtag('event', 'click_menu_item', { 'category': 'dater', 'label': 'open-tutorial', 'value': 0 });
    };
    window.reportDaterOpenComment = function() {
        gtag('event', 'click_menu_item', { 'category': 'dater', 'label': 'open-comment', 'value': 0 });
    };
    window.reportDaterSubmit = function() {
        gtag('event', 'submit', { 'category': 'dater', 'label': 100 });
    };
    window.reportDaterSubmitWithComment = function() {
        gtag('event', 'submit_with_comment', {
            'category': 'dater',
            'label': 200,
        });
    };
    window.reportDaterConfirmSubmit = function() {
        gtag('event', 'submit', {
            'category': 'dater',
            'points': 50,
        });
    };
    window.reportVanalinnadYearChange = function(year) {
        gtag('event', 'old_maps_change_year', {
            'category': isMapview ? 'Map' : 'geotagger',
            'label': year,
            'value': 0,
        });
    };
    window.reportVanalinnadCityChange = function(city) {
        gtag('event', 'old_maps_change_city', {
            'category': isMapview ? 'Map' : 'geotagger',
            'label': city,
            'value': 0,
        });
    };
    window.reportModalVideoStillClick = function() {
        gtag('event', 'still', { 'category': 'video-modal', 'label': null, 'value': 100 });
    };
    window.reportVideoStillClick = function() {
        gtag('event', 'still', { 'category': 'video-permalink', 'label': null, 'value': 100 });
    };
    window.reportVideoModalAnonymousLoginStart = function() {
        gtag('event', 'show_login', {
            'category': 'video-modal',
            'label': null,
            'value': 0,
        });
    };
    window.reportVideoModalOpen = function(id) {
        gtag('event', 'open_video_modal', {
            'category': 'video-modal',
            'label': id.toString(),
            'value': 0,
        });
    };
    window.reportVideoModalSourceLinkClick = function(id) {
        gtag('event', 'click_source_link', {
            'category': 'video-modal',
            'label': id.toString(),
            'value': 0,
        });
    };
    window.reportVideoSourceLinkClick = function(id) {
        gtag('event', 'click_source_link', {
            'category': 'video-permalink',
            'label': id.toString(),
            'value': 0,
        });
    };
    window.reportVideoAlbumLinkClick = function() {
        gtag('event', 'click_album_link', { 'category': 'video-album', 'label': null, 'value': 0 });
    };
    window.reportDonationOneTimeBankLinkClick = function(bank) {
        gtag('event', 'one_time_donation_click', {
            'category': 'General',
            'label': bank,
            'value': 25,
        });
    };
    window.reportDonationStandingBankLinkClick = function(bank) {
        gtag('event', 'standing_donation_click', {
            'category': 'General',
            'label': bank,
            'value': 25,
        });
    };
    window.reportEmailLoginClick = function() {
        gtag('event', 'login_with_email', { 'category': 'Login', 'label': null, 'value': 0 });
    };
    window.reportEmailRegisterClick = function() {
        gtag('event', 'register_with_email', { 'category': 'Login', 'label': null, 'value': 25 });
    };
    window.reportGooglePlusLoginClick = function() {
        gtag('event', 'login_with_google', { 'category': 'Google', 'label': null, 'value': 25 });
    };
})();
