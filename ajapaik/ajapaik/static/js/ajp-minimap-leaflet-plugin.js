(function () {
    'use strict';
    /*global $*/
    /*global L*/

    var AjapaikMinimap = function (node, options) {
        var that = this;
        this.node = node;

        this.options = $.extend({}, options);
        // Do not show map if isMobile is true
        if (options.isMobile) {
            return;
        }
        // Create map only if we have coordinates
        if (options.latitude && options.longitude) {
            this.UI = $([
                '<div id="ajp-minimap-disabled-overlay"></div>',
                '<div id="ajp-photo-modal-map-canvas"></div>',
                '<div id="ajp-photo-modal-map-textbox"></div>',
            ].join('\n'));

            $(this.node).html(this.UI);
            $(this.node).css('z-index', '99');
            $(this.node).show();
            this.initializeMap();
        }
    };
    AjapaikMinimap.prototype = {
        constructor: AjapaikMinimap,
        initializeMap: function () {
            var that = this;
            that.mapCanvas = that.UI.find('#ajp-photo-modal-map-canvas');
            var map = L.map('ajp-photo-modal-map-canvas', { fullscreenControl: true });

            // OSM layer
            var osmUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
            var osmAttrib = 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
            var osm = new L.TileLayer(osmUrl, {minZoom: 5, maxZoom: 18, attribution: osmAttrib});

            that.initialMapCenter = {
                lat: that.options.latitude,
                lng: that.options.longitude
            };
            // Show map layers
            map.addLayer(osm);
            map.setView(that.initialMapCenter, 16);

            // Draw pointer and markerline if we know direction
            if (that.options.azimuth) {
                var marker = this.getMarkerArrow(that.initialMapCenter, that.options);
                marker.addTo(map);

                var markerline = this.getMarkerLine(that.initialMapCenter, that.options);
                map.addLayer(markerline);
            } else {
                var marker = this.getMarker(that.initialMapCenter);
                marker.addTo(map);
            }

            // Top right corner user count
            if (typeof (that.options.geotaggingUserCount) !== 'undefined') {
                var geotaggingUserCount = this.getGeotaggingUserCountButton(that.options);
                geotaggingUserCount.addTo(map);
            }
            // global reference to map for ajp-common-nogooglemaps.js
            window.ajapaikminimap = map;

            // add helper text
            var coordinatelink = this.getCoordinateLink(that.initialMapCenter);
            $('#ajp-photo-modal-map-textbox').append(coordinatelink);

            // In modal view map doesn't know it's size until elements are created
            setTimeout(function () {
                map.invalidateSize();

                // overwrite L.easybutton look and feel
                $('span.ajp-minimap-geotagging-user-text').css('padding-left', '1.2em');
                $('span.ajp-minimap-geotagging-user-text').parent().parent().css('cursor', 'default');
                $('span.ajp-minimap-geotagging-user-text').parent().parent().css('pointer-events', 'none');
                $('span.ajp-minimap-geotagging-user-text').parent().parent().css('width', '4.5em');
                $('span.ajp-minimap-geotagging-user-text').parent().parent().parent().css('background-color', 'white');
            }, 500);

            // For slow networks (500 ms failed in train)
            setTimeout(function () {
                map.invalidateSize();
            }, 1000);

        },
        getCoordinateLink: function (point) {
            var link = $('<a>');
            var url = 'https://www.openstreetmap.org/?mlat=' + point.lat + '&mlon=' + point.lng + '#map=15/' + point.lat + '/' + point.lng;
            link.attr('href', url);
            link.text(point.lat + '° N ' + point.lng + '° E');
            return link;
        },

        getMarkerArrow: function (point, options) {
            var pointerIcon = new L.icon({
                iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Ic_navigation_48px.svg',
                iconSize: [48, 48], // size of the icon
                iconAnchor: [24, 24], // point of the icon which will correspond to marker's location
                popupAnchor: [-3, -26] // point from which the popup should open relative to the iconAnchor
            });

            var azimuth_fixed = this.ajapaikAzimuthToLeafletAzimuth(point, options.azimuth);
            var markerOptions = {
                icon: pointerIcon,
                rotationAngle: azimuth_fixed
            };

            return L.marker(point, markerOptions);
        },

        getMarker: function (point, options) {
            var pointerIcon = new L.icon({
                iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/9/92/Ic_location_on_48px.svg',
                iconSize: [48, 48], // size of the icon
                iconAnchor: [24, 48], // point of the icon which will correspond to marker's location
                popupAnchor: [-3, -26] // point from which the popup should open relative to the iconAnchor
            });
            return L.marker(point, {icon: pointerIcon});
        },

        ajapaikAzimuthToLeafletAzimuth: function(point, azimuth) {
            var destinationPoint_ajapaik = this.simpleCalculateMapLineEndPoint(point, azimuth, 0.2);
            var azimuth_ajapaik = this.radiansToDegrees(this.getAzimuthBetweenTwoPoints(point, destinationPoint_ajapaik));

            var destinationPoint_leaflet = L.GeometryUtil.destination(point, azimuth, 1000);
            var azimuth_leaflet = this.radiansToDegrees(this.getAzimuthBetweenTwoPoints(point, destinationPoint_leaflet));

            var azimuth_fixed = azimuth_ajapaik - (azimuth_leaflet - azimuth_ajapaik);
            return azimuth_fixed;
        },

        // copied from ajp-geotagger-plugin.js
        getAzimuthBetweenTwoPoints: function (p1, p2) {
            var x = p2.lat - p1.lat,
                y = p2.lng - p1.lng;
            return Math.atan2(y, x);
        },

        // copied from ajp-geotagger-plugin.js
        radiansToDegrees: function (rad) {
            var ret = rad * (180 / Math.PI);
            if (ret < 0) {
                ret += 360;
            }
            return ret;
        },

        // copied from ajp-geotagger-plugin.js
        degreesToRadians: function (deg) {
            return deg * Math.PI / 180;
        },

        // modified from ajp-geotagger-plugin.js
        simpleCalculateMapLineEndPoint: function (startPoint, azimuth, lineLength) {
            azimuth = this.degreesToRadians(azimuth);
            var newLat = (Math.cos(azimuth) * lineLength) + startPoint.lat,
                newLng = (Math.sin(azimuth) * lineLength) + startPoint.lng;

            return L.latLng(newLat, newLng)
        },

        getMarkerLine: function (startingPoint, options) {
            var destinationPoint = this.simpleCalculateMapLineEndPoint(startingPoint, options.azimuth, 0.2);
            var pointList = [startingPoint, destinationPoint];
            var markerline = new L.Polyline(
                pointList,
                {
                    color: 'red',
                    weight: 3,
                    opacity: 0.5,
                    smoothFactor: 1,
                    dashArray: '7,7'
                });
            return markerline;
        },
        getGeotaggingUserCountButton: function (options) {
            var e = $('<span>');
            e.addClass('ajp-minimap-geotagging-user-text');
            e.css('font-size', '150%');
            e.text(options.geotaggingUserCount);

            if (options.geotaggingUserCount == 1) e.addClass('ajp-minimap-geotagging-user-single-person');
            else if (options.geotaggingUserCount > 1) e.addClass('ajp-minimap-geotagging-user-multiple-people');
            if (options.userHasGeotaggedThisPhoto == 1) e.addClass('ajp-minimap-geotagging-user-active')

            // create temporary div to get the outerhtml
            var html_value = $('<div>').append(e).html();
            var button = L.easyButton(html_value, function () {
            });
            button.disable();
            return button;
        }
    };

    // FIXME: Supports only one minimap. 
    $.fn.AjapaikMinimap = function (options) {
        return this.each(function () {
            $(this).data('AjapaikMinimap', new AjapaikMinimap(this, options));
        });
    };
}());

// Helper function for Reading global variables from ajapaik/ajapaik/templates/photo/_photo_modal.html

function get_photoviewModalOptions() {
    var options = {};
    if (window.photoModalPhotoLat && window.photoModalPhotoLng) {
        options = {
            latitude: window.photoModalPhotoLat,
            longitude: window.photoModalPhotoLng,
            azimuth: window.photoModalPhotoAzimuth
        };
    } else if (window.photoModalExtraLat && window.photoModalExtraLng) {
        options = {
            latitude: window.photoModalExtraLat,
            longitude: window.photoModalExtraLng,
            azimuth: null
        };
    }

    options.geotaggingUserCount = 0;
    if (window.photoModalGeotaggingUserCount) {
        options.geotaggingUserCount = parseInt(window.photoModalGeotaggingUserCount);
    }

    options.userHasGeotaggedThisPhoto = 0;
    if (window.photoModalUserHasGeotaggedThisPhoto) {
        options.userHasGeotaggedThisPhoto = 1;
    }
    options.isMobile = window.isMobile;
    options.title = window.title;
    options.description = window.description;

    return options;
}
