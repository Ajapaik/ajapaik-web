(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global google */
    window.getAzimuthBetweenMouseAndMarker = function (e, marker) {
        var x = e.latLng.lat() - marker.position.lat(),
            y = e.latLng.lng() - marker.position.lng();
        return Math.atan2(y, x);
    };
    Math.degrees = function (rad) {
        var ret = rad * (180 / Math.PI);
        if (ret < 0) {
            ret += 360;
        }
        return ret;
    };
    Math.radians = function (degrees) {
        return degrees * Math.PI / 180;
    };
    Math.calculateMapLineEndPoint = function (azimuth, startPoint, lineLength) {
        azimuth = Math.radians(azimuth);
        var newX = Math.cos(azimuth) * lineLength + startPoint.lat(),
            newY = Math.sin(azimuth) * lineLength + startPoint.lng();
        return new google.maps.LatLng(newX, newY);
    };
    window.dottedAzimuthLineSymbol = {
        path: google.maps.SymbolPath.CIRCLE,
        strokeOpacity: 1,
        strokeWeight: 1.5,
        strokeColor: 'red',
        scale: 0.75
    };
    window.dottedAzimuthLine = new google.maps.Polyline({
        geodesic: true,
        strokeOpacity: 0,
        icons: [
            {
                icon: window.dottedAzimuthLineSymbol,
                offset: '0',
                repeat: '7px'
            }
        ],
        visible: false,
        clickable: false
    });
}());