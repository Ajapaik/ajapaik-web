(function () {
    "use strict";
    /*jslint nomen: true*/
    /*global google */
    /*global _gaq */
    /*global $ */
    /*global URI */
    /*global docCookies */

    window.flipFeedbackURL = "/flip_feedback/";

    window.getMap = function (startPoint, startingZoom, isGameMap) {
        var latLng,
            zoomLevel,
            streetViewOptions,
            mapOpts,
            streetPanorama;

        if (!startPoint) {
            latLng = new google.maps.LatLng(59, 26);
            startingZoom = 8;
        } else {
            latLng = new google.maps.LatLng(startPoint[1], startPoint[0]);
        }

        if (!startingZoom) {
            zoomLevel = 13;
        } else {
            zoomLevel = startingZoom;
        }

        streetViewOptions = {
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

        streetPanorama = new google.maps.StreetViewPanorama(document.getElementById("map_canvas"), streetViewOptions);

        mapOpts = {
            zoom: zoomLevel,
            scrollwheel: false,
            center: latLng,
            mapTypeControl: true,
            panControl: true,
            panControlOptions: {
                position: google.maps.ControlPosition.RIGHT_TOP
            },
            zoomControl: true,
            zoomControlOptions: {
                position: google.maps.ControlPosition.RIGHT_TOP
            },
            streetViewControl: true,
            streetViewControlOptions: {
                position: google.maps.ControlPosition.RIGHT_TOP
            },
            streetView: streetPanorama
        };

        //TODO: Remove redundant
        if (document.getElementById("ajapaik-game-map-canvas")) {
            window.map = new google.maps.Map(document.getElementById("ajapaik-game-map-canvas"), mapOpts);
        } else {
            window.map = new google.maps.Map(document.getElementById("map_canvas"), mapOpts);
        }

        if (isGameMap) {
            $("<div/>").addClass("center-marker").appendTo(window.map.getDiv()).click(function () {
                var that = $(this);
                if (!that.data("win")) {
                    that.data("win").bindTo("position", window.map, "center");
                }
                that.data("win").open(window.map);
            });
        }

        google.maps.event.addListener(streetPanorama, "visible_changed", function () {
            if (streetPanorama.getVisible()) {
                if (isGameMap) {
                    _gaq.push(["_trackEvent", "Game", "Opened Street View"]);
                } else {
                    _gaq.push(["_trackEvent", "Map", "Opened Street View"]);
                }
            }
        });

        google.maps.event.addListener(streetPanorama, "pano_changed", function () {
            if (isGameMap) {
                _gaq.push(["_trackEvent", "Game", "Street View Movement"]);
            } else {
                _gaq.push(["_trackEvent", "Map", "Street View Movement"]);
            }
        });
    };
}());