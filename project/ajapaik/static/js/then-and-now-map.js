(function () {
    'use strict';
    /* global google */
    /* global tourPhotos */
    /* global startLat */
    /* global startLng */
    /* global marker1 */
    /* global marker2 */
    /* global marker3 */
    /* global isOrderedTour */
    var map = new google.maps.Map(document.getElementById('map-container'), {
            center: {
                lat: 58.3833,
                lng: 24.5000
            },
            zoom: 15
        }),
        infoWindow = new google.maps.InfoWindow();
    $(document).ready(function () {
        var bounds = new google.maps.LatLngBounds(),
            currentLatLng;
        $.each(tourPhotos, function (k, v) {
            var icon;
            if (v.isDone) {
                icon = marker2;
            } else {
                icon = marker1;
            }
            currentLatLng = new google.maps.LatLng(v.lat, v.lng);
            bounds.extend(currentLatLng);
            var marker = new google.maps.Marker({
                position: currentLatLng,
                map: map,
                title: v.name,
                url: v.url,
                image: v.image,
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
            })(marker, v.name + '<a href="' + v.url + '"><img src="' + v.image + '"></a>', infoWindow));
        });
        map.fitBounds(bounds);
        var userLocation = new google.maps.Marker({
            clickable: false,
            icon: marker3,
            shadow: null,
            zIndex: 999,
            map: map
        });
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (pos) {
                var me = new google.maps.LatLng(pos.coords.latitude, pos.coords.longitude);
                userLocation.setPosition(me);
            }, function (error) {

            });
        }
    });
}());