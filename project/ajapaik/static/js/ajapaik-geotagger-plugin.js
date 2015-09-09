(function ($) {
    'use strict';
    /*global google */
    /*global BigScreen */
    /*global gettext */
    /*global isMobile */
    /*global console */
    var AjapaikGeotagger = function (node, options) {
        var that = this;
        this.node = node;
        this.options = $.extend({
        }, options);
        if (!this.options.mode) {
            this.options.mode = 'vantage';
        }
        if (this.options.markerLocked === undefined) {
            this.options.markerLocked = true;
        }
        this.OSM_MAPTYPE_ID = 'OSM';
        this.firstMoveDone = false;
        this.mapMousemoveListenerActive = false;
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
        this.mapMousemoveListenerFunction = function (e) {
            if (that.realMarker && e && !isMobile && that.firstMoveDone && that.options.mode === 'vantage' &&
                that.mapMousemoveListenerActive) {
                console.log('activated mouse move listener');
                var radianAngle = that.getAzimuthBetweenMouseAndMarker(e),
                    degangle = that.radiansToDegrees(radianAngle);
                that.azimuthLine.setPath([that.realMarker.position,
                    that.simpleCalculateMapLineEndPoint(degangle, that.realMarker.position, 0.01)]);
            }
        };
        this.mapClickListenerFunction = function (e) {
            //if (!window.guessResponseReceived) {
            //    radianAngle = Math.getAzimuthBetweenMouseAndMarker(e, marker);
            //    azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
            //    degreeAngle = Math.degrees(radianAngle);
            //    if (window.isMobile) {
            //        azimuthLine.setPath([marker.position, Math.simpleCalculateMapLineEndPoint(degreeAngle, marker.position, 0.01)]);
            //        azimuthLine.setMap(map);
            //        azimuthLine.icons = [
            //            {icon: azimuthLineSymbol, offset: '0', repeat: '7px'}
            //        ];
            //        azimuthLine.setVisible(true);
            //    }
            //    if (azimuthListenerActive) {
            //        mapMousemoveListenerActive = false;
            //        window.google.maps.event.clearListeners(map, 'mousemove');
            //        saveDirection = true;
            //        if (!disableSave) {
            //            saveLocationButton.removeAttr('disabled');
            //            saveLocationButton.removeClass('btn-default');
            //            saveLocationButton.removeClass('btn-warning');
            //            saveLocationButton.addClass('btn-success');
            //            saveLocationButton.text(window.gettext('Save location and direction'));
            //        }
            //        azimuthLine.icons[0].repeat = '2px';
            //        if (marker.position && e.latLng) {
            //            azimuthLine.setPath([marker.position, e.latLng]);
            //            azimuthLine.setVisible(true);
            //        }
            //        if (panoramaMarker) {
            //            panoramaMarker.setMap(null);
            //        }
            //        var markerImage = {
            //            url: '/static/images/material-design-icons/ajapaik_custom_size_panorama.png',
            //            origin: new window.google.maps.Point(0, 0),
            //            anchor: new window.google.maps.Point(18, 18),
            //            scaledSize: new window.google.maps.Size(36, 36)
            //        };
            //        panoramaMarker = new window.google.maps.Marker({
            //            map: map,
            //            draggable: false,
            //            position: e.latLng,
            //            icon: markerImage
            //        });
            //        setCursorToAuto();
            //    } else {
            //        if (!mapMousemoveListenerActive) {
            //            mapMousemoveListener = window.google.maps.event.addListener(map, 'mousemove', mapMousemoveListenerFunction);
            //            mapMousemoveListenerActive = true;
            //            window.google.maps.event.trigger(map, 'mousemove', e);
            //        }
            //    }
            //    azimuthListenerActive = !azimuthListenerActive;
            //}
        };
        this.mapIdleListenerFunction = function () {
            console.log('activated map idle listener');
        };
        this.mapDragstartListenerFunction = function () {
            console.log('activated map dragstart listener');
            that.azimuthLine.setVisible(false);
        };
        this.mapDragListenerFunction = function () {
            console.log('activated map drag listener');
            that.realMarker.setPosition(that.map.getCenter());
        };
        this.mapDragendListenerFunction = function () {
            console.log('activated map dragend listener');
            that.firstMoveDone = true;
            that.mapMousemoveListenerActive = true;
            that.azimuthLine.setVisible(true);
            that.realMarker.setPosition(that.map.getCenter());
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
                    that.Private('prepareFullScreen');
                });
                BigScreen.request(fullScreenElement.get(0));
            }
        });
        fullScreenElement.click(function () {
            if (BigScreen.enabled) {
                BigScreen.exit();
            }
        });
        this.Private('initializeMap');
    }, Private = {
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
            lockButton.attr('title', gettext('Toggle map center lock'));
            modeSelectionButtonGroup.find('#ajp-geotagger-approximate-mode-button')
                .attr('title', gettext('Approximate')).html(gettext('Approximate')).click(function () {
                    var $this = $(this);
                    that.Private('switchToApproximateMode');
                    $this.parent().find('.btn').removeClass('active');
                    $this.addClass('active');
                });
            modeSelectionButtonGroup.find('#ajp-geotagger-vantage-point-mode-button')
                .attr('title', gettext('Vantage point')).html(gettext('Vantage point')).click(function () {
                    var $this = $(this);
                    that.Private('switchToVantagePointMode');
                    $this.parent().find('.btn').removeClass('active');
                    $this.addClass('active');
                });
            modeSelectionButtonGroup.find('#ajp-geotagger-object-mode-button')
                .attr('title', gettext('Object')).html(gettext('Object')).click(function () {
                    var $this = $(this);
                    that.Private('switchToObjectMode');
                    $this.parent().find('.btn').removeClass('active');
                    $this.addClass('active');
                });
            searchBox.attr('placeholder', gettext('Search box'));
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
            this.realMarker = new google.maps.Marker({
                draggable: false,
                position: new google.maps.LatLng(that.options.startLat, that.options.startLng),
                visible: false,
                map: this.map,
                icon: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg'
            });
            this.azimuthLine.setMap(this.map);
            this.map.controls[google.maps.ControlPosition.LEFT_CENTER].push(lockButton.get(0));
            this.map.controls[google.maps.ControlPosition.TOP_CENTER].push(modeSelectionButtonGroup.get(0));
            google.maps.event.addListener(this.map, 'mousemove', this.mapMousemoveListenerFunction);
            google.maps.event.addListener(this.map, 'dragstart', this.mapDragstartListenerFunction);
            google.maps.event.addListener(this.map, 'dragend', this.mapDragendListenerFunction);
            google.maps.event.addListener(this.map, 'drag', this.mapDragListenerFunction);
            google.maps.event.addListener(this.map, 'idle', this.mapIdleListenerFunction);
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
        switchToApproximateMode: function () {
            $('#ajp-geotagger-guess-marker').removeClass('vantage object').addClass('approximate');
            this.options.mode = 'approximate';
        },
        switchToVantagePointMode: function () {
            $('#ajp-geotagger-guess-marker').removeClass('approximate object').addClass('vantage');
            this.options.mode = 'vantage';
        },
        switchToObjectMode: function () {
            $('#ajp-geotagger-guess-marker').removeClass('vantage approximate').addClass('object');
            this.options.mode = 'object';
        }
    };
    AjapaikGeotagger.prototype = {
        constructor: AjapaikGeotagger,
        Private: function () {
            var args = Array.prototype.slice.call(arguments),
                fn = args.shift();
            if (typeof Private[fn] === 'function') {
                Private[fn].apply(this, args);
            }
        },
        initializeGeotaggerState: function (options) {
            $('#ajp-geotagger-image-thumb').attr('src', options.thumbSrc);
            this.map.setCenter(new google.maps.LatLng(options.startLat, options.startLng));
            this.options.currentPhotoId = options.photoId;
            this.options.fullScreenSrc = options.fullScreenSrc;
            this.options.fullScreenWidth = options.fullScreenWidth;
            this.options.fullScreenHeight = options.fullScreenHeight;
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
        simpleCalculateMapLineEndPoint: function (azimuth, startPoint, lineLength) {
            azimuth = this.degreesToRadians(azimuth);
            var newX = (Math.cos(azimuth) * lineLength) + startPoint.lat(),
                newY = (Math.sin(azimuth) * lineLength) + startPoint.lng();
            return new google.maps.LatLng(newX, newY);
        }
    };
    $.fn.AjapaikGeotagger = function (options) {
        return this.each(function () {
            $(this).data('AjapaikGeotagger', new AjapaikGeotagger(this, options));
        });
    };
}(jQuery));