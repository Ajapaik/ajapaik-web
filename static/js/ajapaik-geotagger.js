(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global google */
    /*global saveLocationURL */
    window.Geotagger = function () {
        this.geotagEndpointURL = saveLocationURL;
        this.streetViewOptions = {
            panControl: true,
            panControlOptions: {
                position: google.maps.ControlPosition.LEFT_CENTER
            },
            zoomControl: true,
            zoomControlOptions: {
                position: google.maps.ControlPosition.LEFT_CENTER
            },
            addressControl: false,
            linksControl: true,
            linksControlOptions: {
                position: google.maps.ControlPosition.BOTTOM_CENTER
            },
            enableCloseButton: true,
            visible: false
        };
        this.OSM_MAPTYPE_ID = 'OSM';
        this.mapOpts = {
            zoom: 8,
            center: {
                lat: 59,
                lng: 26
            },
            mapTypeControl: true,
            mapTypeId: this.OSM_MAPTYPE_ID,
            mapTypeControlOptions: {
                mapTypeIds: [google.maps.MapTypeId.ROADMAP, google.maps.MapTypeId.SATELLITE, this.OSM_MAPTYPE_ID],
                position: google.maps.ControlPosition.BOTTOM_CENTER
            },
            panControl: false,
            zoomControlOptions: {
                position: google.maps.ControlPosition.LEFT_CENTER
            },
            streetViewControl: true,
            streetViewControlOptions: {
                position: google.maps.ControlPosition.LEFT_CENTER
            }
        };
    };
    window.Geotagger.prototype = {
        initializeMap: function () {
            this.streetPanorama = new google.maps.StreetViewPanorama(
                document.getElementById('ajp-geotagger-map-canvas'),
                this.streetViewOptions
            );
            this.mapOpts.streetView = this.streetPanorama;
            this.map = new google.maps.Map(document.getElementById('ajp-geotagger-map-canvas'), this.mapOpts);
            this.map.mapTypes.set('OSM', new window.google.maps.ImageMapType({
                getTileUrl: function (coord, zoom) {
                    return 'http://tile.openstreetmap.org/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
                },
                tileSize: new window.google.maps.Size(256, 256),
                name: 'OpenStreetMap',
                maxZoom: 18
            }));
        },
        initializeState: function (state) {
            $('#ajp-geotagger-image-thumb').attr('src', state.thumbSrc);
        }
    };
}());