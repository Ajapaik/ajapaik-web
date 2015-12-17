(function () {
    'use strict';
    /* global mapRedirectURL */
    /* global randomTourURL */
    /* global gettext */
    /* global alert */
    var geolocationCallback = function (location) {
            var lat = location.coords.latitude,
                lng = location.coords.longitude;
            $.ajax({
                url: randomTourURL,
                data: {
                    lat: lat,
                    lng: lng
                },
                success: function (response) {
                    window.location = mapRedirectURL + response.tour + '/';
                }
            });
        },
        geolocationError = function () {
            alert(gettext('Unable to get location data'));
        },
        getGeolocation = function getLocation(callback) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(callback, geolocationError);
            }
        },
        tourIdInput = $('#tan-frontpage-tour-id-input'),
        tourId;
    $('#tan-frontpage-make-tour-button').click(function () {
        getGeolocation(geolocationCallback);
    });
    $('#tan-frontpage-tour-id-submit').click(function (e) {
        e.preventDefault();
        tourId = tourIdInput.val();
        window.location = mapRedirectURL + tourId + '/';
    });
}());