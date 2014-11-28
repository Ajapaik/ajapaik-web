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
                position: google.maps.ControlPosition.LEFT_CENTER
            },
            zoomControl: true,
            zoomControlOptions: {
                position: google.maps.ControlPosition.LEFT_CENTER
            },
            streetViewControl: true,
            streetViewControlOptions: {
                position: google.maps.ControlPosition.LEFT_CENTER
            },
            streetView: streetPanorama
        };

        window.map = new google.maps.Map(document.getElementById("map_canvas"), mapOpts);

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

    window.prepareFullscreen = function() {
        $(".full-box img").load(function () {
            var that = $(this),
                aspectRatio = that.width() / that.height(),
                newWidth = parseInt(screen.height * aspectRatio),
                newHeight = parseInt(screen.width / aspectRatio);
            if (newWidth > screen.width) {
                newWidth = screen.width;
            } else {
                newHeight = screen.height;
            }
            that.css("margin-left", (screen.width - newWidth) / 2 + "px");
            that.css("margin-top", (screen.height - newHeight) / 2 + "px");
            that.css("width", newWidth);
            that.css("height", newHeight);
            that.css("opacity", 1);
        });
    };

    window.QueryString = function () {
        var queryString = {};
        var query = window.location.search.substring(1);
        var vars = query.split("&");
        for (var i = 0; i < vars.length; i++) {
            var pair = vars[i].split("=");
            if (typeof queryString[pair[0]] === "undefined") {
                queryString[pair[0]] = pair[1];
            } else if (typeof queryString[pair[0]] === "string") {
                queryString[pair[0]] = [ queryString[pair[0]], pair[1] ];
            } else {
                queryString[pair[0]].push(pair[1]);
            }
        }
        return queryString;
    };

    $(document).ready(function () {
        $.jQee("esc", function () {
            $("#close-photo-drawer").click();
            $("#close-location-tools").click();
        });

        $.jQee("shift+r", function () {
            $("#random-photo").click();
        });

        $.ajaxSetup({
            headers: { 'X-CSRFToken': docCookies.getItem('csrftoken') }
        });

        $(".filter-box select").change(function () {
            var uri = new URI(location.href),
                newQ = URI.parseQuery($(this).val()),
                isFilterEmpty = false;

            uri.removeQuery(Object.keys(newQ));
            $.each(newQ, function (i, ii) {
                isFilterEmpty = ii == "";
            });

            if (!isFilterEmpty) {
                uri = uri.addQuery(newQ);
            }

            uri.addQuery("fromSelect", 1);

            location.href = uri.toString();
        });
    });
}());