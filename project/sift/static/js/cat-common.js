(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    $('.cat-change-language-link').click(function (e) {
        console.log('asdasd');
        e.preventDefault();
        $('#cat-language').val($(this).attr('data-lang-code'));
        $('#cat-change-language-form').submit();
    });
}());