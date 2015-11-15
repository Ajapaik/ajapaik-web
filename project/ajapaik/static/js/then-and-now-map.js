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
        }),
        infoWindow = new google.maps.InfoWindow();
    $(document).ready(function () {
        map.setCenter(new google.maps.LatLng(startLat, startLng));
        $.each(tourPhotos, function (k, v) {
            var icon;
            if (v.isDone) {
                icon = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png';
            } else {
                icon = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png';
            }
            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(v.lat, v.lng),
                map: map,
                title: v.name,
                url: v.url,
                image: v.image,
                icon: icon
            });
            google.maps.event.addListener(marker, 'click', (function (marker, content, infoWindow) {
                return function () {
                    infoWindow.setContent(content);
                    infoWindow.open(map, marker);
                };
            })(marker, v.name + '<a href="' + v.url + '"><img src="' + v.image + '"></a>', infoWindow));
        });
        var userLocation = new google.maps.Marker({
            clickable: false,
            icon: new google.maps.MarkerImage('//maps.gstatic.com/mapfiles/mobile/mobileimgs2.png',
                new google.maps.Size(22, 22),
                new google.maps.Point(0, 18),
                new google.maps.Point(11, 11)),
            shadow: null,
            zIndex: 999,
            map: map
        });
        if (navigator.geolocation) navigator.geolocation.getCurrentPosition(function (pos) {
            var me = new google.maps.LatLng(pos.coords.latitude, pos.coords.longitude);
            userLocation.setPosition(me);
        }, function (error) {

        });
    });
}());