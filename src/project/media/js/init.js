(function () {
    "use strict";
    /*jslint nomen: true*/
    /*global google */
    /*global _gaq */

    window.flipFeedbackURL = "/flip_feedback/";

    window.showScoreboard = function () {
        $('.top .score_container .scoreboard li').not('.you').add('h2').slideDown();
        $('.top .score_container #facebook-connect').slideDown();
        $('.top .score_container #google-plus-connect').slideDown();
    };

    window.hideScoreboard = function () {
        $('.top .score_container .scoreboard li').not('.you').add('h2').slideUp();
        $('.top .score_container #facebook-connect').slideUp();
        $('.top .score_container #google-plus-connect').slideUp();
    };

    window.getMap = function(startPoint, startingZoom, isGameMap) {
        var latLng,
            zoomLevel,
            osmMapType,
            streetViewOptions,
            mapOpts,
            streetPanorama;

        if (startPoint == undefined) {
            latLng = new google.maps.LatLng(59, 26);
            startingZoom = 8;
        } else {
            latLng = new google.maps.LatLng(startPoint[1], startPoint[0]);
        }

        if (typeof startingZoom == "undefined") {
            zoomLevel = 13;
        } else {
            zoomLevel = startingZoom;
        }

        osmMapType = new google.maps.ImageMapType({
            getTileUrl: function (coord, zoom) {
                return "http://tile.openstreetmap.org/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
            },
            tileSize: new google.maps.Size(256, 256),
            isPng: true,
            alt: "OpenStreetMap layer",
            name: "OSM",
            maxZoom: 18
        });

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
            maxZoom: 18,
            scrollwheel: false,
            center: latLng,
            mapTypeControl: true,
            mapTypeControlOptions: {
                mapTypeIds: ["OSM", google.maps.MapTypeId.ROADMAP],
                style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
            },
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

        window.map.mapTypes.set("OSM", osmMapType);
        window.map.setMapTypeId("OSM");

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

    $(document).ready(function () {
        $.jQee("esc", function () {
            $("#close-photo-drawer").click();
            $("#close-location-tools").click();
        });

        $.jQee("shift+r", function () {
            $("#random-photo").click();
        });

        $(".filter-box select").change(function () {
            var uri = new URI(location.href),
                newQ = URI.parseQuery($(this).val()),
                isFilterEmpty = false;

            uri.removeQuery(Object.keys(newQ));
            $.each(newQ, function (i, ii) {
                isFilterEmpty = ii == ""
            });

            if (!isFilterEmpty) {
                uri = uri.addQuery(newQ);
            }

            location.href = uri.toString();
        });
    });
}());