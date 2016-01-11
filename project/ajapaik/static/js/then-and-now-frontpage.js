(function () {
    'use strict';
    /* global mapRedirectURL */
    /* global newTourURL */
    /* global myToursURL */
    /* global gettext */
    /* global alert */
    var tourIdInput = $('#tan-frontpage-tour-id-input'),
        tourId;
    $('#tan-frontpage-make-tour-button').click(function () {
        window.location = newTourURL;
    });
    $('#tan-frontpage-tour-id-submit').click(function (e) {
        e.preventDefault();
        tourId = tourIdInput.val();
        window.location = mapRedirectURL + tourId + '/';
    });
    $('#tan-frontpage-my-tours-button').click(function () {
        window.location = myToursURL;
    });
}());