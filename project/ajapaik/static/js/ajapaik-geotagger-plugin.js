(function ($) {
    'use strict';
    /*global google */
    /*global BigScreen */
    /*global gettext */
    /*global interpolate */
    /*global isMobile */
    /*global saveLocationURL */
    /*global docCookies */
    /*global updateLeaderboard */
    var AjapaikGeotagger = function (node, options) {
        var that = this;
        this.node = node;
        this.options = $.extend({
        }, options);
        // Default settings
        if (!this.options.mode) {
            this.options.mode = 'vantage';
        }
        this.customFFWheelFunctionActive = true;
        this.customNonFFWheelFunctionActive = true;
        this.mapMarkerDragListenerActive = false;
        this.mapMarkerDragendListenerActive = false;
        if (this.options.markerLocked === undefined) {
            this.options.markerLocked = true;
        } else if (this.options.markerLocked === false) {
            this.customFFWheelFunctionActive = false;
            this.customNonFFWheelFunctionActive = false;
            this.mapMarkerDragListenerActive = true;
            this.mapMarkerDragendListenerActive = true;
        }
        // (mostly static) settings
        this.OSM_MAPTYPE_ID = 'OSM';
        this.azimuthLineSymbol = {
            path: google.maps.SymbolPath.CIRCLE,
            strokeOpacity: 1,
            strokeWeight: 1.5,
            strokeColor: 'red',
            scale: 0.75
        };
        this.azimuthLine = new google.maps.Polyline({
            geodesic: false,
            strokeOpacity: 0,
            icons: [
                {
                    icon: this.azimuthLineSymbol,
                    offset: '0',
                    repeat: '7px'
                }
            ],
            visible: false,
            clickable: false
        });
        this.mapOpts = {
            zoom: 14,
            center: {
                lat: 59,
                lng: 26
            },
            scrollwheel: false,
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
        // State
        this.firstMoveDone = false;
        this.angleBetweenMouseAndMarker = null;
        this.angleBetweenMarkerAndPanoramaMarker = null;
        this.azimuthLineEndPoint = null;
        this.saveAzimuth = false;
        this.drawAzimuthLineOnMouseMove = !isMobile;
        this.hintUsed = false;
        this.heatmap = null;
        // Listeners
        this.mapMousemoveListenerFunction = function (e) {
            if (that.drawAzimuthLineOnMouseMove) {
                that.angleBetweenMouseAndMarker = that.radiansToDegrees(that.getAzimuthBetweenMouseAndMarker(e));
                that.azimuthLine.icons[0].repeat = '7px';
                that.panoramaMarker.setVisible(false);
                that.azimuthLine.setPath([that.realMarker.position,
                    that.simpleCalculateMapLineEndPoint(that.angleBetweenMouseAndMarker,
                        that.realMarker.position, 0.01)]);
            }
        };
        this.mapClickListenerFunction = function (e) {
            if (that.options.mode === 'vantage') {
                if (that.drawAzimuthLineOnMouseMove) {
                    that.drawAzimuthLineOnMouseMove = false;
                    that.saveAzimuth = true;
                    that.angleBetweenMouseAndMarker = that.radiansToDegrees(that.getAzimuthBetweenMouseAndMarker(e));
                    that.angleBetweenMarkerAndPanoramaMarker = that.angleBetweenMouseAndMarker;
                    that.azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
                    that.panoramaMarker.setPosition(e.latLng);
                    that.panoramaMarker.setVisible(true);
                    that.setCursorToAuto();
                    that.azimuthLine.icons[0].repeat = '2px';
                    that.setSaveButtonToLocationAndAzimuth();
                    that.azimuthLine.setPath([that.realMarker.position, that.panoramaMarker.position]);
                } else {
                    that.setSaveButtonToLocationOnly();
                    that.panoramaMarker.setVisible(false);
                    that.saveAzimuth = false;
                    that.drawAzimuthLineOnMouseMove = true;
                    that.azimuthLine.icons[0].repeat = '7px';
                }
            }
        };
        this.mapIdleListenerFunction = function () {
            if (that.options.markerLocked) {
                that.realMarker.setPosition(that.map.getCenter());
            }
        };
        this.mapDragstartListenerFunction = function () {
            that.drawAzimuthLineOnMouseMove = false;
            that.azimuthLine.setVisible(false);
        };
        this.mapDragListenerFunction = function () {
            if (that.options.markerLocked) {
                that.realMarker.setPosition(that.map.getCenter());
            }
        };
        this.mapDragendListenerFunction = function () {
            that.firstMoveDone = true;
            that.setSaveButtonToLocationOnly();
            if (that.options.mode === 'vantage') {
                $('#ajp-geotagger-lock-button').show();
            }
            if (that.options.mode === 'vantage') {
                that.drawAzimuthLineOnMouseMove = true;
                that.azimuthLine.setVisible(true);
            }
            if (that.options.markerLocked) {
                that.realMarker.setPosition(that.map.getCenter());
            }
        };
        this.mapMarkerDragListenerFunction = function () {
            if (that.mapMarkerDragListenerActive) {
                that.angleBetweenMarkerAndPanoramaMarker =
                    that.radiansToDegrees(that.getAzimuthBetweenTwoMarkers(that.realMarker, that.panoramaMarker));
                that.azimuthLine.setPath([that.realMarker.position,
                    that.simpleCalculateMapLineEndPoint(that.angleBetweenMarkerAndPanoramaMarker,
                        that.panoramaMarker.position, 0.01)]);
            }
        };
        this.mapMarkerDragendListenerFunction = function () {
            if (that.mapMarkerDragendListenerActive) {
                that.azimuthLine.setPath([that.realMarker.position, that.panoramaMarker.position]);
            }
        };
        this.wheelFunctionFF = function (e) {
            if (that.customFFWheelFunctionActive) {
                var now = new Date().getTime();
                if (!that.lastTriggeredWheelingFF) {
                    that.lastTriggeredWheelingFF = now - 250;
                }
                if (now - 250 > that.lastTriggeredWheelingFF) {
                    that.lastTriggeredWheelingFF = now;
                    if (e.detail < 0) {
                        that.map.setZoom(that.map.zoom + 1);
                    } else {
                        if (that.map.zoom > 14) {
                            that.map.setZoom(that.map.zoom - 1);
                        }
                    }
                }
            }
        };
        this.wheelFunctionNonFF = function (e) {
            if (that.customNonFFWheelFunctionActive) {
                var now = new Date().getTime();
                if (!that.lastTriggeredWheelingNonFF) {
                    that.lastTriggeredWheelingNonFF = now - 100;
                }
                if (now - 100 > that.lastTriggeredWheelingNonFF) {
                    that.lastTriggeredWheelingNonFF = now;
                    if (e.wheelDelta > 0) {
                        that.map.setZoom(that.map.zoom + 1);
                    } else {
                        if (that.map.zoom > 14) {
                            that.map.setZoom(that.map.zoom - 1);
                        }
                    }
                }
            }
        };
        this.UI = $([
            "<div class='row-fluid ajp-full-height'>",
            "    <div class='col-xs-12 col-sm-9 ajp-full-height ajp-no-padding' id='ajp-geotagger-map-container'>",
            "        <div id='ajp-geotagger-map-canvas'></div>",
            "    </div>",
            "    <div class='col-xs-12 col-sm-3 ajp-no-padding' id='ajp-geotagger-panel'>",
            "        <div class='col-xs-6 col-sm-12 ajp-no-padding'>",
            "            <a id='ajp-geotagger-full-screen-link'>",
            "                <img id='ajp-geotagger-image-thumb' class='ajp-full-width' src=''>",
            "            </a>",
            "        </div>",
            "        <div class='col-xs-6 col-sm-12 ajp-no-padding'>",
            "            <p id='ajp-geotagger-description' class='hidden'></p>",
            "        </div>",
            "        <div class='col-xs-6 col-sm-12 ajp-no-padding' id='ajp-geotagger-button-controls'>",
            "            <div class='btn-group btn-group-justified' role='group' aria-label='ajp-geotagger-image-buttons'>",
            "                <div class='btn-group' role='group'>",
            "                    <button type='button' id='ajp-geotagger-flip-button' class='btn btn-default ajp-no-border-radius'>",
            "                        <i class='material-icons'>flip</i>",
            "                    </button>",
            "                </div>",
            "                <div class='btn-group' role='group'>",
            "                    <button type='button' id='ajp-geotagger-description-button' class='btn btn-default ajp-no-border-radius'>",
            "                        <i class='material-icons'>description</i>",
            "                    </button>",
            "                </div>",
            "            </div>",
            "            <br/>",
            "            <div class='btn-group btn-group-justified' role='group' aria-label='ajp-geotagger-game-buttons'>",
            "                <div class='btn-group' role='group'>",
            "                    <button type='button' id='ajp-geotagger-skip-button' class='btn btn-default ajp-no-border-radius'>",
            "                        <i class='material-icons'>skip_next</i>",
            "                    </button>",
            "                </div>",
            "                <div class='btn-group' role='group'>",
            "                    <button type='button' id='ajp-geotagger-save-button' class='btn btn-disabled ajp-no-border-radius'>",
            "                        <i class='material-icons'>done</i>",
            "                    </button>",
            "                </div>",
            "            </div>",
            "        </div>",
            "        <div class='col-xs-6 col-sm-12 ajp-no-padding'>",
            "            <p id='ajp-geotagger-current-stats'></p>",
            "        </div>",
            "        <div class='col-xs-6 col-sm-12 ajp-no-padding' id='ajp-geotagger-feedback'>",
            "            <div class='panel panel-primary'>",
            "                <div class='panel-heading'>",
            "                    <div class='panel-title'></div>",
            "                </div>",
            "                <div class='panel-body'>",
            "                    <p id='ajp-geotagger-feedback-message'></p>",
            "                    <p id='ajp-geotagger-feedback-points'></p>",
            "                    <p id='ajp-geotagger-feedback-difficulty-prompt'></p>",
            "                    <form id='ajp-geotagger-feedback-difficulty-form'>",
            "                        <span></span>",
            "                        <input type='radio' name='difficulty' value='1'>",
            "                        <input type='radio' name='difficulty' value='2'>",
            "                        <input type='radio' name='difficulty' value='3'>",
            "                        <span></span>",
            "                    </form>",
            "                    <div class='col-xs-12 col-sm-12 col-lg-offset-6 col-lg-6 col-md-12'>",
            "                        <button class='btn btn-primary btn-block' id='ajp-geotagger-feedback-next-button'></button>",
            "                    </div>",
            "                </div>",
            "            </div>",
            "        </div>",
            "    </div>",
            "</div>",
            "<div id='ajp-geotagger-full-screen-box'>",
            "    <div id='ajp-geotagger-full-screen-container'>",
            "       <img src='' id='ajp-geotagger-full-screen-image'>",
            "    </div>",
            "</div>"
        ].join("\n"));
        // Build UI, initialize map
        $(this.node).html(this.UI);
        var fullScreenElement = $('#ajp-geotagger-full-screen-image');
        $('#ajp-geotagger-full-screen-link').click(function () {
            if (BigScreen.enabled) {
                fullScreenElement.attr('src', that.options.fullScreenSrc).load(function () {
                    that.prepareFullScreen();
                });
                BigScreen.request(fullScreenElement.get(0));
            }
        });
        fullScreenElement.click(function () {
            if (BigScreen.enabled) {
                BigScreen.exit();
            }
        });
        this.initializeMap();
    };
    AjapaikGeotagger.prototype = {
        constructor: AjapaikGeotagger,
        initializeMap: function () {
            var lockButton = $([
                    "<div class='btn btn-default' id='ajp-geotagger-lock-button'></div>"
                ].join("\n")),
                modeSelectionButtonGroup = $([
                    "<div class='btn-group' id='ajp-geotagger-mode-selection' role='group' aria-label='...'>",
                        "<button type='button' id='ajp-geotagger-approximate-mode-button' class='btn btn-default'></button>",
                        "<button type='button' id='ajp-geotagger-vantage-point-mode-button' class='btn btn-default active'></button>",
                        "<button type='button' id='ajp-geotagger-object-mode-button' class='btn btn-default'></button>",
                    "</div>"
                ].join("\n")),
                searchBox = $([
                    "<input id='ajp-geotagger-search-box' type='text' placeholder=''>"
                ].join("\n")),
                that = this;
            this.streetPanorama = new google.maps.StreetViewPanorama(
                document.getElementById('ajp-geotagger-map-canvas'),
                this.streetViewOptions
            );
            this.mapOpts.streetView = this.streetPanorama;
            this.map = new google.maps.Map(document.getElementById('ajp-geotagger-map-canvas'), this.mapOpts);
            this.map.mapTypes.set('OSM', new google.maps.ImageMapType({
                getTileUrl: function (coord, zoom) {
                    return 'http://tile.openstreetmap.org/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
                },
                tileSize: new google.maps.Size(256, 256),
                name: 'OpenStreetMap',
                maxZoom: 18
            }));
            lockButton.attr('title', gettext('Toggle map center lock')).click(function () {
                if (that.firstMoveDone && that.options.mode === 'vantage') {
                    var $this = $(this);
                    if ($this.hasClass('active')) {
                        $this.removeClass('active');
                        that.lockMapToCenter();
                    } else {
                        $this.addClass('active');
                        that.unlockMapFromCenter();
                    }
                }
            });
            modeSelectionButtonGroup.find('#ajp-geotagger-approximate-mode-button')
                .attr('title', gettext('Approximate')).html(gettext('Approximate')).click(function () {
                    var $this = $(this);
                    that.switchToApproximateMode();
                    $this.parent().find('.btn').removeClass('active');
                    $this.addClass('active');
                });
            modeSelectionButtonGroup.find('#ajp-geotagger-vantage-point-mode-button')
                .attr('title', gettext('Vantage point')).html(gettext('Vantage point')).click(function () {
                    var $this = $(this);
                    that.switchToVantagePointMode();
                    $this.parent().find('.btn').removeClass('active');
                    $this.addClass('active');
                });
            modeSelectionButtonGroup.find('#ajp-geotagger-object-mode-button')
                .attr('title', gettext('Object')).html(gettext('Object')).click(function () {
                    var $this = $(this);
                    that.switchToObjectMode();
                    $this.parent().find('.btn').removeClass('active');
                    $this.addClass('active');
                });
            searchBox.attr('placeholder', gettext('Search box'));
            $('#ajp-geotagger-feedback').find('.panel-title').html(gettext('Thank you!'));
            this.map.controls[google.maps.ControlPosition.TOP_LEFT].push(searchBox.get(0));
            this.placesSearchBox = new google.maps.places.SearchBox((searchBox.get(0)));
            google.maps.event.addListener(this.placesSearchBox, 'places_changed', function () {
                var places = that.placesSearchBox.getPlaces();
                if (places.length === 0) {
                    return;
                }
                that.map.setCenter(places[0].geometry.location);
            });
            $('<div/>').attr('id', 'ajp-geotagger-guess-marker').addClass('vantage').appendTo(this.map.getDiv());
            $('#ajp-geotagger-description-button').click(function () {
                that.hintUsed = true;
                $('#ajp-geotagger-description').toggleClass('hidden');
            });
            $('#ajp-geotagger-flip-button').click(function () {
                $(this).toggleClass('active');
                that.flipImages();
            });
            $('#ajp-geotagger-skip-button').click(function () {
                that.saveSkip();
            });
            $('#ajp-geotagger-save-button').click(function () {
                that.saveGeotag();
            });
            this.realMarker = new google.maps.Marker({
                draggable: false,
                position: new google.maps.LatLng(that.options.startLat, that.options.startLng),
                visible: false,
                map: this.map,
                icon: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg'
            });
            var panoramaMarkerImage = {
                url: '/static/images/material-design-icons/ajapaik_custom_size_panorama.png',
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(18, 18),
                scaledSize: new google.maps.Size(36, 36)
            };
            this.panoramaMarker = new google.maps.Marker({
                map: this.map,
                draggable: false,
                visible: false,
                icon: panoramaMarkerImage
            });
            this.feedbackEstimatedLocationMarker = new google.maps.Marker({
                map: this.map,
                title: gettext('Median guess'),
                draggable: false,
                icon: '/static/images/ajapaik_marker_35px_transparent.png'
            });
            var playerMarkerImage = {
                url: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.png',
                size: new google.maps.Size(24, 33),
                scaledSize: new google.maps.Size(24, 33),
                anchor: new google.maps.Point(12, 33)
            };
            this.playerGuessMarker = new google.maps.Marker({
                map: this.map,
                title: gettext('Your guess'),
                draggable: false,
                icon: playerMarkerImage
            });
            this.mapInner = $('#ajp-geotagger-map-canvas').get(0);
            this.mapInner.addEventListener('mousewheel', this.wheelFunctionNonFF, true);
            this.mapInner.addEventListener('DOMMouseScroll', this.wheelFunctionFF, true);
            this.azimuthLine.setMap(this.map);
            $('#ajp-geotagger-feedback-difficulty-prompt').html(gettext('Depicted location has changed'));
            $('#ajp-geotagger-feedback-next-button').html(gettext('Continue'));
            var feedbackForm = $('#ajp-geotagger-feedback-difficulty-form');
            feedbackForm.find('span:first-child').text(gettext('little'));
            feedbackForm.find('span:last-child').text(gettext('much'));
            this.map.controls[google.maps.ControlPosition.LEFT_CENTER].push(lockButton.get(0));
            this.map.controls[google.maps.ControlPosition.TOP_CENTER].push(modeSelectionButtonGroup.get(0));
            google.maps.event.addListener(this.map, 'mousemove', this.mapMousemoveListenerFunction);
            google.maps.event.addListener(this.map, 'dragstart', this.mapDragstartListenerFunction);
            google.maps.event.addListener(this.map, 'dragend', this.mapDragendListenerFunction);
            google.maps.event.addListener(this.map, 'drag', this.mapDragListenerFunction);
            google.maps.event.addListener(this.map, 'idle', this.mapIdleListenerFunction);
            google.maps.event.addListener(this.map, 'click', this.mapClickListenerFunction);
            google.maps.event.addListener(this.realMarker, 'drag', this.mapMarkerDragListenerFunction);
            google.maps.event.addListener(this.realMarker, 'dragend', this.mapMarkerDragendListenerFunction);
        },
        prepareFullScreen: function () {
            var image = $('#ajp-geotagger-full-screen-image'),
                aspectRatio = this.options.fullScreenWidth / this.options.fullScreenHeight,
                newWidth = parseInt(screen.height * aspectRatio, 10),
                newHeight = parseInt(screen.width / aspectRatio, 10);
            if (newWidth > screen.width) {
                newWidth = screen.width;
            } else {
                newHeight = screen.height;
            }
            image.css('margin-left', (screen.width - newWidth) / 2 + 'px');
            image.css('margin-top', (screen.height - newHeight) / 2 + 'px');
            image.css('width', newWidth);
            image.css('height', newHeight);
            image.css('opacity', 1);
        },
        // FIXME: Getting less and less DRY
        switchToApproximateMode: function () {
            $('#ajp-geotagger-guess-marker').removeClass('vantage object').addClass('approximate');
            $('#ajp-geotagger-lock-button').hide();
            this.lockMapToCenter();
            this.setCursorToAuto();
            this.panoramaMarker.setVisible(false);
            this.azimuthLine.setVisible(false);
            this.options.mode = 'approximate';
        },
        switchToVantagePointMode: function () {
            $('#ajp-geotagger-guess-marker').removeClass('approximate object').addClass('vantage');
            if (this.firstMoveDone) {
                $('#ajp-geotagger-lock-button').show();
            }
            this.lockMapToCenter();
            this.setCursorToAuto();
            this.panoramaMarker.setVisible(false);
            this.azimuthLine.setVisible(true);
            this.options.mode = 'vantage';
        },
        switchToObjectMode: function () {
            $('#ajp-geotagger-guess-marker').removeClass('vantage approximate').addClass('object');
            $('#ajp-geotagger-lock-button').hide();
            this.lockMapToCenter();
            this.panoramaMarker.setVisible(false);
            this.setCursorToAuto();
            this.azimuthLine.setVisible(false);
            this.options.mode = 'object';
        },
        initializeGeotaggerState: function (options) {
            var fmt = gettext('Unique geotags from %(users)s users, %(azimuthUsers)s with azimuth'),
                statString = interpolate(fmt, {
                    users: options.uniqueGeotagCount,
                    azimuthUsers: options.uniqueGeotagWithAzimuthCount
                }, true);
            $('#ajp-geotagger-image-thumb').attr('src', options.thumbSrc);
            $('#ajp-geotagger-description').html(options.description);
            $('#ajp-geotagger-current-stats').html(statString);
            this.map.setCenter(new google.maps.LatLng(options.startLat, options.startLng));
            this.options.currentPhotoId = options.photoId;
            this.options.fullScreenSrc = options.fullScreenSrc;
            this.options.fullScreenWidth = options.fullScreenWidth;
            this.options.fullScreenHeight = options.fullScreenHeight;
            this.options.isMapview = options.isMapview;
            this.options.isGame = options.isGame;
            this.options.isGallery = options.isGallery;
        },
        radiansToDegrees: function (rad) {
            var ret = rad * (180 / Math.PI);
            if (ret < 0) {
                ret += 360;
            }
            return ret;
        },
        degreesToRadians: function (deg) {
            return deg * Math.PI / 180;
        },
        getAzimuthBetweenMouseAndMarker: function (mouseEvent) {
            var x = mouseEvent.latLng.lat() - this.realMarker.position.lat(),
                y = mouseEvent.latLng.lng() - this.realMarker.position.lng();
            return Math.atan2(y, x);
        },
        getAzimuthBetweenTwoMarkers: function (marker1, marker2) {
            var x = marker2.position.lat() - marker1.position.lat(),
                y = marker2.position.lng() - marker1.position.lng();
            return Math.atan2(y, x);
        },
        getAzimuthBetweenTwoPoints: function (x1, y1, x2, y2) {
            // TODO: Simplify, no need for multiple such functions
        },
        simpleCalculateMapLineEndPoint: function (azimuth, startPoint, lineLength) {
            azimuth = this.degreesToRadians(azimuth);
            var newX = (Math.cos(azimuth) * lineLength) + startPoint.lat(),
                newY = (Math.sin(azimuth) * lineLength) + startPoint.lng();
            return new google.maps.LatLng(newX, newY);
        },
        setCursorToPanorama: function () {
            this.map.setOptions({
                draggableCursor: 'url(/static/images/material-design-icons/ajapaik_custom_size_panorama.svg) 18 18, auto',
                draggingCursor: 'auto'
            });
        },
        setCursorToAuto: function () {
            this.map.setOptions({
                draggableCursor: 'auto',
                draggingCursor: 'auto'
            });
        },
        lockMapToCenter: function () {
            $('#ajp-geotagger-guess-marker').show();
            this.realMarker.setVisible(false);
            this.realMarker.set('draggable', false);
            this.map.set('scrollwheel', false);
            this.customFFWheelFunctionActive = true;
            this.customNonFFWheelFunctionActive = true;
            this.mapMarkerDragListenerActive = false;
            this.mapMarkerDragendListenerActive = false;
            this.map.setCenter(this.realMarker.position);
            this.setCursorToPanorama();
            this.options.markerLocked = true;
        },
        unlockMapFromCenter: function () {
            $('#ajp-geotagger-guess-marker').hide();
            this.realMarker.setVisible(true);
            this.realMarker.set('draggable', true);
            this.map.set('scrollwheel', true);
            this.customFFWheelFunctionActive = false;
            this.customNonFFWheelFunctionActive = false;
            this.mapMarkerDragListenerActive = true;
            this.mapMarkerDragendListenerActive = true;
            this.setCursorToAuto();
            this.options.markerLocked = false;
        },
        flipImages: function () {
            $('#ajp-geotagger-image-thumb').toggleClass('ajp-photo-flipped');
            $('#ajp-geotagger-full-screen-image').toggleClass('ajp-photo-flipped');
        },
        setSaveButtonToLocationOnly: function () {
            $('#ajp-geotagger-save-button').removeClass('btn-disabled btn-success').addClass('btn-warning');
        },
        setSaveButtonToLocationAndAzimuth: function () {
            $('#ajp-geotagger-save-button').removeClass('btn-disabled btn-warning').addClass('btn-success');
        },
        saveSkip: function () {
            $.ajax({
                type: 'POST',
                url: saveLocationURL,
                data: {
                    photo: this.options.currentPhotoId,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                dataType: 'json'
            });
        },
        saveGeotag: function () {
            var mapTypeId = this.map.getMapTypeId(),
                lat = this.realMarker.getPosition().lat(),
                lon = this.realMarker.getPosition().lng(),
                that = this,
                data = {
                    lat: lat,
                    lon: lon,
                    type: 0,
                    photo: this.options.currentPhotoId,
                    hint_used: this.hintUsed,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                };
            if (mapTypeId === 'roadmap') {
                data.map_type = 0;
            } else if (mapTypeId === 'hybrid') {
                data.map_type = 1;
            } else {
                data.map_type = 2;
            }
            if (this.options.isGame) {
                data.origin = 0;
            } else if (this.options.isGallery) {
                data.origin = 2;
            } else if (this.options.isMapview) {
                data.origin = 1;
            }
            if (that.saveAzimuth) {
                data.azimuth = this.angleBetweenMarkerAndPanoramaMarker;
                data.azimuth_line_end_lat = this.azimuthLineEndPoint[0];
                data.azimuth_line_end_lon = this.azimuthLineEndPoint[1];
            }
            $.ajax({
                type: 'POST',
                url: saveLocationURL,
                data: data,
                success: function (response) {
                    var playerGuessLatlng = that.realMarker.getPosition();
                    updateLeaderboard();
                    $('input[name="difficulty"]').prop('checked', false);
                    $('#ajp-geotagger-lock-button').hide();
                    $('#ajp-geotagger-button-controls').hide();
                    $('#ajp-geotagger-feedback-points').html(gettext('Points awarded') + ': ' + response.current_score);
                    $('#ajp-geotagger-feedback-message').html(response.feedback_message);
                    $('#ajp-geotagger-feedback').show();
                    if (response.heatmap_points) {
                        that.displayFeedbackHeatmap(response);
                        that.realMarker.setVisible(false);
                        $('#ajp-geotagger-guess-marker').hide();
                        that.playerGuessMarker.setPosition(playerGuessLatlng);
                    }
                },
                dataType: 'json'
            });
        },
        displayFeedbackHeatmap: function (responseData) {
            var latLngBounds = new google.maps.LatLngBounds(),
                newLatLng,
                heatmapPoints = [],
                i;
            this.heatmap = null;
            for (i = 0; i < responseData.heatmap_points.length; i += 1) {
                newLatLng = new google.maps.LatLng(responseData.heatmap_points[i][0], responseData.heatmap_points[i][1]);
                heatmapPoints.push(newLatLng);
                latLngBounds.extend(newLatLng);
            }
            if (responseData.estimated_location && responseData.estimated_location[0] &&
                responseData.estimated_location[1]) {
                this.feedbackEstimatedLocationMarker.setPosition(
                    new google.maps.LatLng(responseData.estimated_location[0], responseData.estimated_location[1]));
                this.map.setCenter(this.feedbackEstimatedLocationMarker.getPosition());
            } else {
                this.map.fitBounds(latLngBounds);
            }
            this.realMarker.setZIndex(google.maps.Marker.MAX_ZINDEX + 1);
            heatmapPoints = new google.maps.MVCArray(heatmapPoints);
            this.heatmap = new google.maps.visualization.HeatmapLayer({
                data: heatmapPoints
            });
            this.heatmap.setMap(this.map);
            this.heatmap.setOptions({
                radius: 50, dissipating: true
            });
        }
    };
    $.fn.AjapaikGeotagger = function (options) {
        return this.each(function () {
            $(this).data('AjapaikGeotagger', new AjapaikGeotagger(this, options));
        });
    };
}(jQuery));