(function () {
    'use strict';
    /* global alert */
    /* global gettext */
    /* global getPhotosURL */
    /* global currentUserID */
    /* global isFixedTour */
    /* global tmpl */
    var galleryContainer = $('#tan-gallery-container'),
        geolocationCallback = function (location) {
            var lat = location.coords.latitude,
                lng = location.coords.longitude;
            getPhotos(lat, lng);
        },
        geolocationError = function () {
            alert(gettext('Unable to get location data'));
        },
        getGeolocation = function getLocation(callback) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(callback, geolocationError);
            }
        },
        getPhotos = function (lat, lng) {
            $.ajax({
                url: getPhotosURL,
                cache: false,
                data: {
                    lat: lat,
                    lng: lng
                },
                success: function (response) {
                    $.each(response, function (k, v) {
                        v.isDone = !!((v.usersCompleted && v.usersCompleted.indexOf(currentUserID) > -1) || (v.groupsCompleted));
                        v.isDoneByCurrentUser = !!(v.usersCompleted && v.usersCompleted.indexOf(currentUserID) > -1);
                        galleryContainer.append(tmpl('tan-gallery-photo-template', v));
                    });
                    galleryContainer.justifiedGallery();
                }
            });
        };
    $(document).ready(function () {
        if (isFixedTour) {
            getPhotos();
        } else {
            getGeolocation(geolocationCallback);
        }
    });
}());