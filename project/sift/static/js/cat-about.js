(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global filterURL */
    /*global taggerURL */
    $(document).ready(function () {
        $('.cat-header-tag-link').click(function () {
            location.href = taggerURL;
        });
        $('.cat-header-filter-link').click(function () {
            location.href = filterURL;
        });
    });
}());