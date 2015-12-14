(function () {
    'use strict';
    /* global mapRedirectURL */
    /* global gettext */
    /* global alert */
    var geolocationCallback = function (location) {
            var lat = location.coords.latitude,
                lng = location.coords.longitude;
            window.location = mapRedirectURL + '?lat=' + lat + '&lng=' + lng;
        },
        geolocationError = function () {
            alert(gettext('Unable to get location data'));
        },
        getGeolocation = function getLocation(callback) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(callback, geolocationError);
            }
        },
        albumIdInput = $('#tan-frontpage-album-id-input'),
        albumId;
    $('#tan-frontpage-make-tour-button').click(function () {
        getGeolocation(geolocationCallback);
    });
    $('#tan-frontpage-album-id-submit').click(function (e) {
        e.preventDefault();
        albumId = albumIdInput.val();
        window.location = mapRedirectURL + '?album=' + albumId;
    });
}());