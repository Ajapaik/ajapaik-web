(function () {
    'use strict';
    /* global console */
    /* global google */
    /* global getMarkersURL */
    /* global currentUserID */
    /* global marker1 */
    /* global marker2 */
    /* global marker3 */
    /* global alert */
    /* global gettext */
    /* global isOrderedTour */
    /* global isFixedTour */
    var map,
        bounds,
        currentLatLng,
        mapCenter,
        infoWindow = new google.maps.InfoWindow(),
        geolocationCallback = function (location) {
            var lat = location.coords.latitude,
                lng = location.coords.longitude;
            getMapMarkers(lat, lng);
        },
        geolocationError = function () {
            console.log(gettext('Unable to get location data'));
            getMapMarkers(null, null);
        },
        getGeolocation = function getLocation(callback) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(callback, geolocationError);
            }
        },
        getMapMarkers = function (lat, lng) {
            $.ajax({
                url: getMarkersURL,
                cache: false,
                data: {
                    lat: lat,
                    lng: lng
                },
                success: function (response) {
                    bounds = new google.maps.LatLngBounds();
                    $.each(response, function (k, v) {
                        bounds.extend(new google.maps.LatLng(v.lat, v.lon));
                    });
                    bounds.extend(new google.maps.LatLng(lat, lng));
                    mapCenter = bounds.getCenter();
                    if (!map) {
                        map = new google.maps.Map(document.getElementById('map-container'), {
                            center: mapCenter,
                            mapTypeControlOptions: {
                                position: google.maps.ControlPosition.BOTTOM_RIGHT
                            },
                            zoom: 15
                        });
                        if (isFixedTour) {
                            map.fitBounds(bounds);
                        }
                        var userMarker = new google.maps.Marker({
                            clickable: false,
                            icon: marker3,
                            shadow: null,
                            zIndex: 999,
                            map: map
                        });
                        if (navigator.geolocation) {
                            navigator.geolocation.getCurrentPosition(function (pos) {
                                var userPosition = new google.maps.LatLng(pos.coords.latitude, pos.coords.longitude);
                                userMarker.setPosition(userPosition);
                            }, function () {
                                alert(gettext('Unable to get location data'));
                            });
                        }
                    }
                    map.fitBounds(bounds);
                    $.each(response, function (k, v) {
                        var icon;
                        if ((v.usersCompleted && v.usersCompleted.indexOf(currentUserID)) || (v.groupsCompleted)) {
                            icon = marker2;
                        } else {
                            icon = marker1;
                        }
                        currentLatLng = new google.maps.LatLng(v.lat, v.lon);
                        var marker = new google.maps.Marker({
                            position: currentLatLng,
                            map: map,
                            title: v.description,
                            url: v.permaURL,
                            image: v.imageURL,
                            icon: icon
                        });
                        if (isOrderedTour) {
                            marker.setLabel({
                                text: 1 + v.order + ''
                            });
                        }
                        google.maps.event.addListener(marker, 'click', (function (marker, content, infoWindow) {
                            return function () {
                                infoWindow.setContent(content);
                                infoWindow.open(map, marker);
                            };
                        })(marker, v.description + '<a href="' + v.permaURL + '"><img src="' + v.imageURL + '"></a>', infoWindow));
                    });
                }
            });
        };
    $(document).ready(function () {
        getGeolocation(geolocationCallback);
    });
}());