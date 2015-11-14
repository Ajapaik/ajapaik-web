(function () {
    'use strict';
    /* global mapRedirectURL */
    var geolocationCallback = function (location) {
            var lat = location.coords.latitude,
                lng = location.coords.longitude;
            window.location.href = mapRedirectURL + '?lat=' + lat + '&lng=' + lng;
        },
        geolocationError = function () {

        },
        getGeolocation = function getLocation(callback) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(callback, geolocationError);
            }
        };
    $('#frontpage-make-tour-link').click(function () {
        getGeolocation(geolocationCallback);
    });
}());