(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global _gaq */
    /*global isTagger */
    /*global isFiltering */
    $('.cat-change-language-link').click(function (e) {
        e.preventDefault();
        var langCode = $(this).attr('data-lang-code');
        _gaq.push(['_trackEvent', 'navigation', 'click', 'change-language-' + langCode, 1, true]);
        $('#cat-language').val(langCode);
        $('input[name=csrfmiddlewaretoken]').val(window.docCookies.getItem('csrftoken'));
        $('#cat-change-language-form').submit();
    });
    $('#cat-brand').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'logo', 1, true]);
    });
    $('#cat-header-mode').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'album-or-photos-dropdown', 25, false]);
    });
    $('#cat-show-albums-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'show-albums', 25, false]);
    });
    $('#cat-show-pictures-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'show-pictures', 25, false]);
    });
    $('#cat-header-tag-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'tagging', 25, false]);
    });
    $('#cat-header-filter-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'filtering', 25, false]);
    });
    $('#cat-toggle-nav').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'toggle-mobile-nav', 1, true]);
    });
    $('#cat-about-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'about', 25, false]);
    });
    $('#cat-choose-language').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'change-language', 1, true]);
    });
    $('.cat-filtering-button').click(function () {
        _gaq.push(['_trackEvent', 'filtering', 'click', 'toggle-filter-' + $(this).attr('data-name'), 50, false]);
    });
    $('#cat-pager-previous').click(function () {
        _gaq.push(['_trackEvent', 'filtering', 'click', 'pager-previous', 10, false]);
    });
    $('#cat-pager-next').click(function () {
        _gaq.push(['_trackEvent', 'filtering', 'click', 'pager-next', 10, false]);
    });
    $(document).on('click', '.cat-photo-result', function () {
        _gaq.push(['_trackEvent', 'filtering', 'click', 'photo-source-link-' + $(this).attr('data-id'), 10, false]);
    });
    $('.cat-tagger-tag-button').click(function () {
        _gaq.push(['_trackEvent', 'tagging', 'click', 'tag-photo', 100, false]);
    });
    $('#cat-tagger-favorite-button').click(function () {
        _gaq.push(['_trackEvent', 'tagging', 'click', 'favorite-photo-' + $(this).attr('data-id'), 75, false]);
    });
    $('#cat-tagger-info-button').click(function () {
        _gaq.push(['_trackEvent', 'tagging', 'click', 'photo-description-' + $(this).attr('data-id'), 50, false]);
    });
    $(document).on('click', '.cat-album-selection-element', function () {
        if (isTagger) {
            _gaq.push(['_trackEvent', 'tagging', 'click', 'select-album-' + $(this).attr('data-id'), 25, false]);
        } else if (isFiltering) {
            _gaq.push(['_trackEvent', 'filtering', 'click', 'select-album-' + $(this).attr('data-id'), 25, false]);
        }
    });
    $('#cat-tagger-current-photo-link').click(function () {
        _gaq.push(['_trackEvent', 'tagging', 'click', 'photo-source-link-' + $(this).attr('data-id'), 10, false]);
    });
    $('#cat-play-store-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'play-store-link', 100, false]);
    });
    $('#cat-hack-for-fi-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'hack-for-fi-link', 5, false]);
    });
    $('#cat-twitter-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'twitter-link', 25, false]);
    });
    $('#cat-facebook-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'facebook-link', 25, false]);
    });
    $('#cat-puik-twitter-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'puik-twitter-link', 25, false]);
    });
    $(document).on('click', '.cat-album-selection-more-info', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var parent = $(this).parent();
        parent.find('.cat-caption-album-full-info').toggleClass('hidden').toggleClass('cat-force-show');
        parent.find('.cat-caption-album-selection').toggleClass('hidden').toggleClass('cat-force-show');
    });
    $(document).on('click', '.cat-caption-album-full-info', function (e) {
        e.preventDefault();
        e.stopPropagation();
    });
}());