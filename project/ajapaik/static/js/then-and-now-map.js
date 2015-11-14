(function () {
    'use strict';
    /* global google */
    /* global tourPhotos */
    /* global startLat */
    /* global startLng */
    var map = new google.maps.Map(document.getElementById('map-container'), {
        center: {
            lat: 58.3833,
            lng: 24.5000
        },
        zoom: 15
    });
    $(document).ready(function () {
        map.setCenter(new google.maps.LatLng(startLat, startLng));
        $.each(tourPhotos, function (k, v) {
            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(v.lat, v.lng),
                map: map,
                title: v.name,
                url: v.url,
                animation: google.maps.Animation.DROP
            });
            google.maps.event.addListener(marker, 'click', function() {
                window.location.href = marker.url;
            });
        });
    });
}());