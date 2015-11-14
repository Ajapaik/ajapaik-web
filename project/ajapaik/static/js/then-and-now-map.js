(function () {
    'use strict';
    /* global google */
    /* global getRandomTourURL */
    var map = new google.maps.Map(document.getElementById('map-container'), {
            center: {
                lat: 58.3833,
                lng: 24.5000
            },
            zoom: 15
        }),
        geolocationCallback = function (location) {
            var lat = location.coords.latitude,
                lng = location.coords.longitude,
                latLng = new google.maps.LatLng(lat, lng);
            map.setCenter(latLng);
            $.ajax({
                url: getRandomTourURL,
                data: {
                    lat: lat,
                    lng: lng
                },
                success: function (response) {
                    $.each(response.photos, function (k, v) {
                        new google.maps.Marker({
                            position: new google.maps.LatLng(v.lat, v.lng),
                            map: map,
                            title: v.name
                        });
                    });
                }
            })
        },
        geolocationError = function () {

        },
        getGeolocation = function getLocation(callback) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(callback, geolocationError);
            }
        };
    $(document).ready(function () {
        getGeolocation(geolocationCallback);
    });
}());