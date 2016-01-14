(function () {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    /*global _gaq*/
    /*global isMapview*/
    // Geotagger events
    window.reportGeotaggerMapClick = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'click', 'map', 0, false]);
    };
    window.reportGeotaggerMapDragstart = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'map-drag-start', 'geotagging', 0, false]);
    };
    window.reportGeotaggerMapDragstartFeedback = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'map-drag-start', 'feedback', 0, false]);
    };
    window.reportGeotaggerMarkerDragend = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'marker-drag-end', null, 0, false]);
    };
    window.reportGeotaggerFullScreenOpen = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'open-full-screen', id.toString(), 0, false]);
    };
    window.reportGeotaggerStreetPanoramaOpen = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'open-street-view', id.toString(), 0, false]);
    };
    window.reportGeotaggerMapUnlock = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'unlock', id.toString(), 0, false]);
    };
    window.reportGeotaggerMapLock = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'lock', id.toString(), 0, false]);
    };
    window.reportGeotaggerShowSearch = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'show-search', id.toString(), 0, false]);
    };
    window.reportGeotaggerSearch = function (term) {
        _gaq.push(['_trackEvent', 'geotagger', 'search', term, 0, false]);
    };
    window.reportGeotaggerShowDescription = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'show-description', id.toString(), 0, false]);
    };
    window.reportGeotaggerFlip = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'flip', id.toString(), 0, false]);
    };
    window.reportGeotaggerSkip = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'skip', id.toString(), -25, false]);
    };
    window.reportGeotaggerSaveLocationOnly = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'save-location-only', id.toString(), 50, false]);
    };
    window.reportGeotaggerSaveLocationAndDirection = function (id) {
        _gaq.push(['_trackEvent', 'geotagger', 'save-location-and-direction', id.toString(), 100, false]);
    };
    window.reportGeotaggerShowInstructions = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'show-instructions', null, 0, false]);
    };
    window.reportGeotaggerHideInstructions = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'hide-instructions', null, 0, false]);
    };
    window.reportGeotaggerSendFeedback = function (value) {
        _gaq.push(['_trackEvent', 'geotagger', 'send-feedback', value.toString(), 25, false]);
    };
    window.reportGeotaggerCorrect = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'tag-feedback', 'correct', 100, false]);
    };
    window.reportGeotaggerIncorrect = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'tag-feedback', 'incorrect', -25, false]);
    };
    window.reportGeotaggerNewlyMappedPhoto = function () {
        _gaq.push(['_trackEvent', 'geotagger', 'tag-feedback', 'first', 200, false]);
    };
    window.reportDaterOpen = function () {
        _gaq.push(['_trackEvent', 'dater', 'menus', 'open', 0, false]);
    };
    window.reportCloseDater = function () {
        _gaq.push(['_trackEvent', 'dater', 'menus', 'close', 0, false]);
    };
    window.reportDaterOpenTutorial = function () {
        _gaq.push(['_trackEvent', 'dater', 'menus', 'open-tutorial', 0, false]);
    };
    window.reportDaterOpenComment = function () {
        _gaq.push(['_trackEvent', 'dater', 'menus', 'open-comment', 0, false]);
    };
    window.reportDaterSubmit = function () {
        _gaq.push(['_trackEvent', 'dater', 'action', 'submit', 100, false]);
    };
    window.reportDaterSubmitWithComment = function () {
        _gaq.push(['_trackEvent', 'dater', 'action', 'submit-with-comment', 200, false]);
    };
    window.reportDaterConfirmSubmit = function () {
        _gaq.push(['_trackEvent', 'dater', 'action', 'submit-confirmation', 50, false]);
    };
    window.reportVanalinnadYearChange = function (year) {
        if (isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'old-maps-change-year', year, 0, false]);
        } else {
            _gaq.push(['_trackEvent', 'geotagger', 'old-maps-change-year', year, 0, false]);
        }
    };
    window.reportVanalinnadCityChange = function (city) {
        if (isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'old-maps-change-city', city, 0, false]);
        } else {
            _gaq.push(['_trackEvent', 'geotagger', 'old-maps-change-city', city, 0, false]);
        }
    };
    window.reportModalVideoStillClick = function () {
        _gaq.push(['_trackEvent', 'video-modal', 'still', null, 100, false]);
    };
    window.reportVideoviewVideoStillClick = function () {
        _gaq.push(['_trackEvent', 'video-permalink', 'still', null, 100, false]);
    };
    window.reportVideoModalAnonymousLoginStart = function () {
        _gaq.push(['_trackEvent', 'video-modal', 'anonymous-login-start', null, 0, false]);
    };
    window.reportVideoModalOpen = function (id) {
        _gaq.push(['_trackEvent', 'video-modal', 'modal-open', id.toString(), 0, false]);
    };
    window.reportVideoModalSourceLinkClick = function (id) {
        _gaq.push(['_trackEvent', 'video-modal', 'source-click', id.toString(), 0, false]);
    };
    window.reportVideoviewSourceLinkClick = function (id) {
        _gaq.push(['_trackEvent', 'video-permalink', 'source-click', id.toString(), 0, false]);
    };
    window.reportVideoviewAlbumLinkClick = function () {
        _gaq.push(['_trackEvent', 'video-permalink', 'album-link', null, 0, false]);
    };
    window.reportDonationLinkClick = function () {
        _gaq.push(['_trackEvent', 'General', 'donation-modal-link-click', null, 10, false]);
    };
    window.reportDonationOneTimeBankLinkClick = function (bank) {
        _gaq.push(['_trackEvent', 'General', 'donation-one-time-bank-link-click', bank, 25, false]);
    };
    window.reportDonationStandingBankLinkClick = function (bank) {
        _gaq.push(['_trackEvent', 'General', 'donation-standing-bank-link-click', bank, 25, false]);
    };
    window.reportDonationHeaderCloseClick = function () {
        _gaq.push(['_trackEvent', 'General', 'donation-header-close-click', null, 0, false]);
    };
    window.reportEmailLoginClick = function () {
        _gaq.push(['_trackEvent', 'Login', 'email', null, 0, false]);
    };
    window.reportEmailRegisterClick = function () {
        _gaq.push(['_trackEvent', 'Login', 'register-email', null, 25, false]);
    };
    window.reportGooglePlusLoginClick = function () {
        _gaq.push(['_trackEvent', 'Google', 'login', null, 25, false]);
    };
}());