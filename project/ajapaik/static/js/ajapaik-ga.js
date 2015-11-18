(function () {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    /*global _gaq*/
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
}());