(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global _gaq */
    /*global isTagger */
    /*global isFiltering */
    /*global curatorURL */
    var reportPermalinkFavoritingError = function () {
        _gaq.push(['_trackEvent', 'permalink', 'error', 'favorite', -1000, true]);
    };
    $('.cat-change-language-link').click(function (e) {
        e.preventDefault();
        var langCode = $(this).attr('data-lang-code');
        _gaq.push(['_trackEvent', 'navigation', 'click', 'change-language-' + langCode, 1, true]);
        $('#cat-language').val(langCode);
        $('input[name=csrfmiddlewaretoken]').val(window.docCookies.getItem('csrftoken'));
        $('#cat-change-language-form').submit();
    });
    $('.cat-header-curator-link').click(function () {
        location.href = curatorURL;
    });
    $('#cat-brand').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'logo', 0, true]);
    });
    $('#cat-header-mode').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'album-or-photos-dropdown', 0, false]);
    });
    $('#cat-show-albums-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'show-albums', 0, false]);
    });
    $('#cat-show-pictures-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'show-pictures', 0, false]);
    });
    $('.cat-header-tag-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'tagging', 0, false]);
    });
    $('.cat-header-filter-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'filtering', 0, false]);
    });
    $('#cat-header-facebook-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'facebook-link', 10, false]);
    });
    $('#cat-header-play-store-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'play-store-link', 100, false]);
    });
    $('#cat-toggle-nav').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'toggle-mobile-nav', 0, true]);
    });
    $('#cat-about-link').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'about', 0, false]);
    });
    $('#cat-choose-language').click(function () {
        _gaq.push(['_trackEvent', 'navigation', 'click', 'change-language', 0, true]);
    });
    $('.cat-filtering-button').click(function () {
        _gaq.push(['_trackEvent', 'filtering', 'click', 'toggle-filter-' + $(this).attr('data-name'), 0, false]);
    });
    $('#cat-pager-previous').click(function () {
        _gaq.push(['_trackEvent', 'filtering', 'click', 'pager-previous', 0, false]);
    });
    $('#cat-pager-next').click(function () {
        _gaq.push(['_trackEvent', 'filtering', 'click', 'pager-next', 0, false]);
    });
    $(document).on('click', '.cat-photo-result', function () {
        _gaq.push(['_trackEvent', 'filtering', 'click', 'photo-permalink-' + $(this).attr('data-id'), 0, false]);
    });
    $('.cat-tagger-tag-button').click(function () {
        _gaq.push(['_trackEvent', 'tagging', 'click', 'tag-photo', 100, false]);
    });
    $('#cat-tagger-favorite-button').click(function () {
        _gaq.push(['_trackEvent', 'tagging', 'click', 'favorite-photo-' + $(this).attr('data-id'), 25, false]);
    });
    $('#cat-tagger-info-button').click(function () {
        _gaq.push(['_trackEvent', 'tagging', 'click', 'photo-description-' + $(this).attr('data-id'), 0, false]);
    });
    $(document).on('click', '.cat-album-selection-element', function () {
        if (isTagger) {
            _gaq.push(['_trackEvent', 'tagging', 'click', 'select-album-' + $(this).attr('data-id'), 0, false]);
        } else if (isFiltering) {
            _gaq.push(['_trackEvent', 'filtering', 'click', 'select-album-' + $(this).attr('data-id'), 0, false]);
        }
    });
    $('#cat-tagger-current-photo-link').click(function () {
        _gaq.push(['_trackEvent', 'tagging', 'click', 'photo-permalink-' + $(this).attr('data-id'), 0, false]);
    });
    $('#cat-play-store-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'play-store-link', 100, false]);
    });
    $('#cat-hack-for-fi-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'hack-for-fi-link', 0, false]);
    });
    $('#cat-twitter-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'twitter-link', 10, false]);
    });
    $('#cat-facebook-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'facebook-link', 10, false]);
    });
    $('#cat-puik-twitter-link').click(function () {
        _gaq.push(['_trackEvent', 'about', 'click', 'puik-twitter-link', 10, false]);
    });
    $('#cat-permalink-full-screen-link').click(function () {
        _gaq.push(['_trackEvent', 'permalink', 'click', 'full-screen', 10, false]);
    });
    $('#cat-permalink-favorite-button').click(function () {
        _gaq.push(['_trackEvent', 'permalink', 'click', 'favorite-photo-' + $(this).attr('data-id'), 25, false]);
    });
    $('#cat-permalink-source-link').click(function () {
        _gaq.push(['_trackEvent', 'permalink', 'click', 'source-link-' + $(this).attr('data-id'), 0, false]);
    });
    $('.cat-permalink-filter-album-link').click(function () {
        _gaq.push(['_trackEvent', 'permalink', 'click', 'filter-album-' + $(this).attr('data-id'), 10, false]);
    });
    $('.cat-permalink-tag-album-link').click(function () {
        _gaq.push(['_trackEvent', 'permalink', 'click', 'tag-album-' + $(this).attr('data-id'), 10, false]);
    });
    $('.cat-tagger-tag-link').click(function () {
        _gaq.push(['_trackEvent', 'permalink', 'click', 'tag-link-' + $(this).attr('data-tag'), 10, false]);
    });
    $('.fb-like').click(function () {
        if (isTagger) {
            _gaq.push(['_trackEvent', 'tagging', 'click', 'facebook-like-' + $(this).attr('data-cat-id'), 100, false]);
        } else {
            _gaq.push(['_trackEvent', 'permalink', 'click', 'facebook-like-' + $(this).attr('data-cat-id'), 100, false]);
        }
    });
    $(document).on('click', '.cat-album-selection-more-info', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var parent = $(this).parent();
        parent.find('.cat-caption-album-full-info').toggleClass('hidden').toggleClass('cat-force-show');
        parent.find('.cat-caption-album-selection').toggleClass('hidden').toggleClass('cat-force-show');
    });
    String.prototype.capitalizeFirstLetter = function () {
        return this.charAt(0).toUpperCase() + this.slice(1);
    };
}());