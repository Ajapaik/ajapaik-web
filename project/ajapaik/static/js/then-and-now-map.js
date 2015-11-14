(function () {
    'use strict';
    /* global google */
    /* global tour */
    var map = new google.maps.Map(document.getElementById('map-container'), {
        center: {
            lat: 58.3833,
            lng: 24.5000
        },
        zoom: 15
    });
    $(document).ready(function () {
        $.each(tour, function (k, v) {
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