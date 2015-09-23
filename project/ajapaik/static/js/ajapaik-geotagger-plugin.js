(function ($) {
    'use strict';
    /*global google*/
    /*global BigScreen*/
    /*global gettext*/
    /*global interpolate*/
    /*global isMobile*/
    /*global saveLocationURL*/
    /*global difficultyFeedbackURL*/
    /*global docCookies*/
    /*global updateLeaderboard*/
    /*global stopGuessLocation*/
    /*global userIsSocialConnected*/
    var AjapaikGeotagger = function (node, options) {
        var that = this;
        this.node = node;
        // Not used currently
        this.options = $.extend({
        }, options);
        // Inner workings
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
            disableDoubleClickZoom: true,
            scrollwheel: false,
            mapTypeControl: true,
            mapTypeId: this.OSM_MAPTYPE_ID,
            mapTypeControlOptions: {
                mapTypeIds: [google.maps.MapTypeId.ROADMAP, google.maps.MapTypeId.SATELLITE, this.OSM_MAPTYPE_ID],
                position: google.maps.ControlPosition.TOP_RIGHT,
                style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
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
        this.saveAzimuth = false;
        this.drawAzimuthLineOnMouseMove = !isMobile;
        this.hintUsed = false;
        this.feedbackMode = false;
        this.customFFWheelFunctionActive = true;
        this.customNonFFWheelFunctionActive = true;
        this.mapMarkerDragListenerActive = false;
        this.mapMarkerDragendListenerActive = false;
        this.options.mode = 'vantage';
        this.options.markerLocked = true;
        // Listeners
        this.windowResizeListenerFunction = function () {
            if (that.options.markerLocked && !that.fullScreenActive && !that.feedbackMode && !that.drawAzimuthLineOnMouseMove) {
                google.maps.event.trigger(that.map, 'click');
            }
        };
        this.mapMousemoveListenerFunction = function (e) {
            if (!that.feedbackMode && that.firstMoveDone) {
                if (that.drawAzimuthLineOnMouseMove) {
                    that.angleBetweenMouseAndMarker = that.radiansToDegrees(that.getAzimuthBetweenMouseAndMarker(e));
                    that.azimuthLine.icons[0].repeat = '7px';
                    that.panoramaMarker.setVisible(false);
                    that.azimuthLine.setPath([that.realMarker.position,
                        that.simpleCalculateMapLineEndPoint(that.angleBetweenMouseAndMarker,
                            that.realMarker.position, 0.01)]);
                }
            }
        };
        this.mapClickListenerFunction = function (e) {
            if (!that.feedbackMode && that.firstMoveDone) {
                if (that.options.mode === 'vantage') {
                    if (isMobile) {
                        if (that.azimuthLine.visible) {
                            that.azimuthLine.setVisible(false);
                            that.panoramaMarker.setVisible(false);
                            that.saveAzimuth = false;
                            that.drawAzimuthLineOnMouseMove = true;
                            that.azimuthLine.icons[0].repeat = '7px';
                            that.setSaveButtonToLocationOnly();
                        } else {
                            that.azimuthLine.setVisible(true);
                            that.panoramaMarker.setPosition(e.latLng);
                            that.panoramaMarker.setVisible(true);
                            that.saveAzimuth = true;
                            that.angleBetweenMouseAndMarker = that.radiansToDegrees(that.getAzimuthBetweenMouseAndMarker(e));
                            that.angleBetweenMarkerAndPanoramaMarker = that.angleBetweenMouseAndMarker;
                            that.azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
                            that.azimuthLine.setPath([that.realMarker.position, that.panoramaMarker.position]);
                            that.azimuthLine.icons[0].repeat = '2px';
                            //that.setCursorToAuto();
                            that.setSaveButtonToLocationAndAzimuth();
                        }
                    } else {
                        if (that.drawAzimuthLineOnMouseMove) {
                            that.panoramaMarker.setPosition(e.latLng);
                            that.panoramaMarker.setVisible(true);
                            that.saveAzimuth = true;
                            that.drawAzimuthLineOnMouseMove = false;
                            that.angleBetweenMouseAndMarker = that.radiansToDegrees(that.getAzimuthBetweenMouseAndMarker(e));
                            that.angleBetweenMarkerAndPanoramaMarker = that.angleBetweenMouseAndMarker;
                            that.azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
                            that.azimuthLine.setPath([that.realMarker.position, that.panoramaMarker.position]);
                            that.azimuthLine.icons[0].repeat = '2px';
                            //that.setCursorToAuto();
                            that.setSaveButtonToLocationAndAzimuth();
                        } else {
                            that.panoramaMarker.setVisible(false);
                            that.saveAzimuth = false;
                            that.drawAzimuthLineOnMouseMove = true;
                            that.azimuthLine.icons[0].repeat = '7px';
                            that.setSaveButtonToLocationOnly();
                        }
                    }
                }
                that.setCorrectInstructionString();
            }
            if (typeof window.reportGeotaggerMapClick === 'function') {
                window.reportGeotaggerMapClick();
            }
        };
        this.mapIdleListenerFunction = function () {
            if (!that.feedbackMode) {
                if (that.options.markerLocked) {
                    that.realMarker.setPosition(that.map.getCenter());
                }
                if (!isMobile) {
                    that.azimuthLine.setVisible(true);
                }
            }
        };
        this.mapCenterChangedListener = function () {
            if (!that.feedbackMode) {
                if (that.options.markerLocked) {
                    that.realMarker.setPosition(that.map.getCenter());
                }
                if (!isMobile) {
                    that.azimuthLine.setVisible(false);
                }
                that.setCursorToPanorama();
            }
        };
        this.mapDragstartListenerFunction = function () {
            if (!that.feedbackMode) {
                that.drawAzimuthLineOnMouseMove = false;
                that.azimuthLine.setVisible(false);
                that.panoramaMarker.setVisible(false);
                that.saveAzimuth = false;
                that.setCorrectInstructionString();
                if (typeof window.reportGeotaggerMapDragstart === 'function') {
                    window.reportGeotaggerMapDragstart();
                }
            } else {
                if (typeof window.reportGeotaggerMapDragstartFeedback === 'function') {
                    window.reportGeotaggerMapDragstartFeedback();
                }
            }
        };
        this.mapDragendListenerFunction = function () {
            if (!that.feedbackMode) {
                that.firstMoveDone = true;
                that.setSaveButtonToLocationOnly();
                if (that.options.mode === 'vantage') {
                    that.lockButton.show();
                }
                if (that.options.mode === 'vantage' && !isMobile) {
                    that.drawAzimuthLineOnMouseMove = true;
                    that.azimuthLine.setVisible(true);
                }
                if (that.options.markerLocked) {
                    that.realMarker.setPosition(that.map.getCenter());
                }
                that.setCorrectInstructionString();
            }
        };
        this.mapMarkerDragListenerFunction = function () {
            if (!that.feedbackMode) {
                if (that.mapMarkerDragListenerActive) {
                    if (that.panoramaMarker && that.realMarker && that.panoramaMarker.position && that.realMarker.position) {
                        that.angleBetweenMarkerAndPanoramaMarker =
                            that.radiansToDegrees(that.getAzimuthBetweenTwoMarkers(that.realMarker, that.panoramaMarker));
                        that.azimuthLine.setPath([that.realMarker.position,
                            that.simpleCalculateMapLineEndPoint(that.angleBetweenMarkerAndPanoramaMarker,
                                that.panoramaMarker.position, 0.01)]);
                        that.azimuthLine.icons[0].repeat = '7px';
                    }
                }
            }
        };
        this.mapMarkerDragendListenerFunction = function () {
            if (!that.feedbackMode) {
                if (that.mapMarkerDragendListenerActive && !isMobile) {
                    that.azimuthLine.setPath([that.realMarker.position, that.panoramaMarker.position]);
                }
                that.firstMoveDone = true;
                that.azimuthLine.setVisible(true);
                that.azimuthLine.icons[0].repeat = '2px';
            }
            if (typeof window.reportGeotaggerMarkerDragend === 'function') {
                window.reportGeotaggerMarkerDragend();
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
                        that.map.setZoom(that.map.zoom - 1);
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
                        that.map.setZoom(that.map.zoom - 1);
                    }
                }
            }
        };
        // UI
        this.UI = $([
            "<div class='row-fluid ajp-full-height'>",
            "    <div class='col-xs-12 col-sm-12 col-md-9 ajp-full-height ajp-no-padding' id='ajp-geotagger-map-container'>",
            "        <div id='ajp-geotagger-map-canvas'></div>",
            "    </div>",
            "    <div class='col-xs-12 col-sm-12 col-md-3 ajp-no-padding ajp-cols-bottom' id='ajp-geotagger-panel'>",
            "        <div class='col-xs-6 col-sm-6 col-md-12 ajp-no-padding'>",
            "           <a id='ajp-geotagger-full-screen-link'>",
            "               <img id='ajp-geotagger-image-thumb' src='' class='ajp-image-responsive'>",
            "           </a>",
            "           <button type='button' id='ajp-geotagger-flip-button' class='btn btn-default ajp-no-border-radius'>",
            "               <i class='material-icons'>flip</i>",
            "            </button>",
            "        </div>",
            "        <div class='col-xs-6 col-sm-6 col-md-12 ajp-no-padding' id='ajp-geotagger-button-controls'>",
            "            <button type='button' id='ajp-geotagger-description-button' class='btn btn-default ajp-no-border-radius'>",
            "               <i class='material-icons'>subject</i>",
            "            </button>",
            "            <p id='ajp-geotagger-description' class='hidden'></p>",
            "            <p id='ajp-geotagger-source' class='hidden'><a href='' target='_blank' title=''></a></p>",
            "            <div class='col-xs-6 col-sm-6 col-md-12' id='ajp-geotagger-stats-container'>",
            "               <i class='material-icons'>people</i><span id='ajp-geotagger-current-stats'></span>",
            "            </div>",
            "            <div class='col-xs-6 col-sm-6 col-md-12 hidden-sm hidden-xs' id='ajp-geotagger-login-container'>",
            "               <i class='material-icons'>account_circle</i><span id='ajp-geotagger-current-login'></span>",
            "            </div>",
            "        </div>",
            "        <div class='col-xs-6 col-sm-6 col-md-12 ajp-no-padding' id='ajp-geotagger-feedback'>",
            "            <div class='panel'>",
            "                <div class='panel-body'>",
            "                    <p id='ajp-geotagger-feedback-thanks'></p>",
            "                    <p id='ajp-geotagger-feedback-message' class='hidden-xs'></p>",
            "                    <p id='ajp-geotagger-feedback-points'></p>",
            "                    <p id='ajp-geotagger-feedback-difficulty-prompt' class='hidden-xs'></p>",
            "                    <form id='ajp-geotagger-feedback-difficulty-form' class='hidden-xs'>",
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
            "        <div class='col-xs-6 col-sm-6 col-md-12 ajp-no-padding' id='ajp-geotagger-confirm-controls'>",
            "            <div class='btn-group btn-group-justified' role='group' id='ajp-geotagger-game-buttons' aria-label='ajp-geotagger-game-buttons'>",
            "                <div class='btn-group' role='group'>",
            "                    <button type='button' id='ajp-geotagger-skip-button' class='btn btn-default ajp-no-border-radius'>",
            "                        <i class='material-icons'>close</i>",
            "                    </button>",
            "                </div>",
            "                <div class='btn-group' role='group'>",
            "                    <button type='button' id='ajp-geotagger-save-button' class='btn btn-disabled ajp-no-border-radius'>",
            "                        <i class='material-icons'>done</i>",
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
        ].join('\n'));
        // Build UI, initialize map
        $(this.node).html(this.UI);
        var fullScreenElement = $('#ajp-geotagger-full-screen-image'),
            loginDiv = $('#ajp-geotagger-current-login');
        $('#ajp-geotagger-full-screen-link').click(function () {
            if (BigScreen.enabled) {
                fullScreenElement.attr('src', that.options.fullScreenSrc).load(function () {
                    that.prepareFullScreen();
                });
                BigScreen.request(fullScreenElement.get(0));
                that.fullScreenActive = true;
                if (typeof window.reportGeotaggerFullScreenOpen === 'function') {
                    window.reportGeotaggerFullScreenOpen(that.options.currentPhotoId);
                }
            }
        });
        fullScreenElement.click(function () {
            if (BigScreen.enabled) {
                BigScreen.exit();
                that.fullScreenActive = false;
            }
        });
        if (userIsSocialConnected) {
            loginDiv.hide();
            loginDiv.parent().find('i').hide();
        } else {
            loginDiv.text(gettext('You\'re anonymous'));
        }
        $('#ajp-geotagger-login-container').click(function () {
            $('#ajapaik-header-profile-button').click();
        });
        $(window).resize(function () {
            if (that.guessingStarted) {
                if (that.resizeTimer) {
                    clearTimeout(that.resizeTimer);
                }
                that.resizeTimer = setTimeout(that.fitGuessPhotosToContainers(), 500);
            }
        });
        this.initializeMap();
    };
    AjapaikGeotagger.prototype = {
        constructor: AjapaikGeotagger,
        initializeMap: function () {
            var modeSelectionButtonGroup = $([
                    "<div class='btn-group' id='ajp-geotagger-mode-selection' role='group' aria-label='...'>",
                        "<button type='button' id='ajp-geotagger-approximate-mode-button' class='btn btn-default'></button>",
                        "<button type='button' id='ajp-geotagger-vantage-point-mode-button' class='btn btn-default active'></button>",
                        "<button type='button' id='ajp-geotagger-object-mode-button' class='btn btn-default'></button>",
                    "</div>"
                ].join('\n')),
                searchBox = $([
                    "<input id='ajp-geotagger-search-box' type='text' placeholder=''>"
                ].join('\n')),
                feedbackNextButton = $('#ajp-geotagger-feedback-next-button'),
                that = this;
            this.lockButton = $([
                    "<div class='btn btn-default' id='ajp-geotagger-lock-button'></div>"
                ].join('\n'));
            this.mapInstructions = $([
                "<div id='ajp-geotagger-map-instruction-text'>",
                "   <p></p>",
                "   <button id='ajp-geotagger-close-instructions-button' class='btn btn-default'>",
                "       <i class='material-icons'>close</i>",
                "   </button>",
                "</div>"
            ].join('\n'));
            this.mapOpenInstructionsButton = $([
                "<button id='ajp-geotagger-open-instructions-button'>",
                "   <i class='material-icons'>info</i>",
                "</button>"
            ].join('\n'));
            this.mapShowSearchButton = $([
                "<button id='ajp-geotagger-show-search-button'>",
                "   <i class='material-icons'>search</i>",
                "</button>"
            ].join('\n'));
            this.streetPanorama = new google.maps.StreetViewPanorama(
                document.getElementById('ajp-geotagger-map-canvas'),
                this.streetViewOptions
            );
            this.streetPanoramaExtraCloseButton = $([
                "<button class='btn btn-default' id='ajp-extra-close-streetview-button'></button>"
            ].join('\n'));
            this.streetPanoramaExtraCloseButton.html(gettext('Close')).click(function () {
                that.streetPanorama.setVisible(false);
            });
            this.mapOpts.streetView = this.streetPanorama;
            this.map = new google.maps.Map(document.getElementById('ajp-geotagger-map-canvas'), this.mapOpts);
            this.map.mapTypes.set('OSM', new google.maps.ImageMapType({
                getTileUrl: function (coord, zoom) {
                    return 'http://tile.openstreetmap.org/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
                },
                tileSize: new google.maps.Size(256, 256),
                name: 'OSM',
                maxZoom: 18
            }));
            if (isMobile) {
                this.lockButton.addClass('hidden');
            }
            this.lockButton.attr('title', gettext('Toggle map center lock')).click(function () {
                if (that.options.mode === 'vantage') {
                    var $this = $(this);
                    if ($this.hasClass('active')) {
                        that.lockMapToCenter();
                        if (typeof window.reportGeotaggerMapLock === 'function') {
                            window.reportGeotaggerMapLock(that.options.currentPhotoId);
                        }
                    } else {
                        that.unlockMapFromCenter();
                        if (typeof window.reportGeotaggerMapUnlock === 'function') {
                            window.reportGeotaggerMapUnlock(that.options.currentPhotoId);
                        }
                    }
                }
                that.setCorrectInstructionString();
                that.options.firstMoveDone = false;
            });
            this.mapShowSearchButton.click(function () {
                var box = $('#ajp-geotagger-search-box');
                box.toggleClass('hidden');
                google.maps.event.trigger(that.map, 'resize');

                if (typeof window.reportGeotaggerShowSearch === 'function' && !box.hasClass('hidden')) {
                    window.reportGeotaggerShowSearch(that.options.currentPhotoId);
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
            this.mapInstructions.find('p')
                .text(gettext('Grab and drag the MAP so that the marker is where the photographer was standing.'));
            searchBox.attr('placeholder', gettext('Search box')).on('change textInput input', function () {
                that.delayedReportSearch($(this).val());
            }).on('focus', function () {
                window.hotkeysActive = false;
            }).on('blur', function () {
                window.hotkeysActive = true;
            });
            $('#ajp-geotagger-feedback').find('#ajp-geotagger-feedback-thanks').html(gettext('Thank you!'));
            this.map.controls[google.maps.ControlPosition.TOP_CENTER].push(searchBox.get(0));
            this.map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(this.mapInstructions.get(0));
            this.map.controls[google.maps.ControlPosition.BOTTOM_RIGHT].push(this.mapOpenInstructionsButton.get(0));
            this.map.controls[google.maps.ControlPosition.TOP_RIGHT].push(this.mapShowSearchButton.get(0));
            this.streetPanorama.controls[google.maps.ControlPosition.BOTTOM_RIGHT].push(this.streetPanoramaExtraCloseButton.get(0));
            google.maps.event.addListener(this.streetPanorama, 'visible_changed', function () {
                if (that.streetPanorama.getVisible() && typeof window.reportGeotaggerStreetPanoramaOpen === 'function') {
                    window.reportGeotaggerStreetPanoramaOpen(that.options.currentPhotoId);
                }
            });
            this.placesSearchBox = new google.maps.places.SearchBox((searchBox.get(0)));
            google.maps.event.addListener(this.placesSearchBox, 'places_changed', function () {
                var places = that.placesSearchBox.getPlaces();
                if (places.length === 0) {
                    return;
                }
                that.map.setCenter(places[0].geometry.location);
            });
            $('<div/>').attr('id', 'ajp-geotagger-guess-marker').addClass('vantage').appendTo(this.map.getDiv());
            this.descriptionButton = $('#ajp-geotagger-description-button');
            this.description = $('#ajp-geotagger-description');
            this.source = $('#ajp-geotagger-source');
            this.descriptionButton.click(function () {
                that.showDescriptions();
                if (typeof window.reportGeotaggerShowDescription === 'function') {
                    window.reportGeotaggerShowDescription(that.options.currentPhotoId);
                }
            });
            $('#ajp-geotagger-flip-button').click(function (e) {
                e.preventDefault();
                e.stopPropagation();
                $(this).toggleClass('active');
                that.flipImages();
                if (typeof window.reportGeotaggerFlip === 'function') {
                    window.reportGeotaggerFlip(that.options.currentPhotoId);
                }
            });
            $('#ajp-geotagger-skip-button').click(function () {
                that.saveSkip();
                if (typeof(stopGuessLocation) === 'function') {
                    stopGuessLocation();
                }
                if (typeof window.reportGeotaggerSkip === 'function') {
                    window.reportGeotaggerSkip(that.options.currentPhotoId);
                }
            });
            $('#ajp-geotagger-save-button').click(function () {
                that.saveGeotag();
            });
            this.mapInstructions.find('button').click(function () {
                that.hideInstructions();
                if (typeof window.reportGeotaggerHideInstructions === 'function') {
                    window.reportGeotaggerHideInstructions();
                }
            });
            this.mapOpenInstructionsButton.click(function () {
                that.showInstructions();
                google.maps.event.trigger(that.map, 'resize');
                if (typeof window.reportGeotaggerShowInstructions === 'function') {
                    window.reportGeotaggerShowInstructions();
                }
            });
            feedbackNextButton.click(function () {
                var feedbackVal = $("input[name='difficulty']:checked").val();
                $.ajax({
                    type: 'POST',
                    url: difficultyFeedbackURL,
                    data: {
                        photo_id: that.options.currentPhotoId,
                        level: feedbackVal,
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    success: function () {
                        if (typeof(stopGuessLocation) === 'function') {
                            stopGuessLocation();
                        }
                        that.guessingStarted = true;
                    }
                });
                if (typeof window.reportGeotaggerSendFeedback === 'function') {
                    window.reportGeotaggerSendFeedback(feedbackVal);
                }
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
            window.addEventListener('resize', this.windowResizeListenerFunction);
            this.azimuthLine.setMap(this.map);
            this.geotaggerImageThumb = $('#ajp-geotagger-image-thumb');
            this.geotaggerImageThumb.load(function () {
                setTimeout(function () {
                    $(window).trigger('resize');
                }, 0);
            });
            $('#ajp-geotagger-feedback-difficulty-prompt').html(gettext('Depicted location has changed'));
            feedbackNextButton.html(gettext('Continue'));
            var feedbackForm = $('#ajp-geotagger-feedback-difficulty-form');
            feedbackForm.find('span:first-child').text(gettext('a little'));
            feedbackForm.find('span:last-child').text(gettext('a lot'));
            this.map.controls[google.maps.ControlPosition.LEFT_CENTER].push(this.lockButton.get(0));
            this.map.controls[google.maps.ControlPosition.TOP_RIGHT].push(modeSelectionButtonGroup.get(0));
            google.maps.event.addListener(this.map, 'mousemove', this.mapMousemoveListenerFunction);
            google.maps.event.addListener(this.map, 'dragstart', this.mapDragstartListenerFunction);
            google.maps.event.addListener(this.map, 'dragend', this.mapDragendListenerFunction);
            google.maps.event.addListener(this.map, 'center_changed', this.mapCenterChangedListener);
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
            this.lockButton.hide();
            this.lockMapToCenter();
            this.setCursorToAuto();
            this.panoramaMarker.setVisible(false);
            this.azimuthLine.setVisible(false);
            this.options.mode = 'approximate';
            this.setCorrectInstructionString();
        },
        switchToVantagePointMode: function () {
            $('#ajp-geotagger-guess-marker').removeClass('approximate object').addClass('vantage');
            if (this.firstMoveDone) {
                this.lockButton.show();
            }
            this.lockMapToCenter();
            this.setCursorToAuto();
            this.panoramaMarker.setVisible(false);
            this.azimuthLine.setVisible(true);
            this.options.mode = 'vantage';
            this.firstMoveDone = false;
            this.setCorrectInstructionString();
        },
        switchToObjectMode: function () {
            $('#ajp-geotagger-guess-marker').removeClass('vantage approximate').addClass('object');
            this.lockButton.hide();
            this.lockMapToCenter();
            this.panoramaMarker.setVisible(false);
            this.setCursorToAuto();
            this.azimuthLine.setVisible(false);
            this.options.mode = 'object';
            this.setCorrectInstructionString();
        },
        initializeGeotaggerState: function (options) {
            this.geotaggerImageThumb.attr('src', options.thumbSrc).removeClass('ajp-photo-flipped');
            $('#ajp-geotagger-full-screen-image').removeClass('ajp-photo-flipped');
            this.description.html(options.description).addClass('hidden');
            this.source.addClass('hidden').find('a').attr('title', options.sourceName + ' ' + options.sourceKey)
                .attr('href', options.sourceURL).html(options.sourceName + ' ' + options.sourceKey);
            $('#ajp-geotagger-current-stats').html(options.uniqueGeotagCount).show();
            $('#ajp-geotagger-feedback').hide();
            $('#ajp-geotagger-flip-button').removeClass('active');
            $('#ajp-geotagger-button-controls').show();
            $('#ajp-geotagger-confirm-controls').show();
            $('#ajp-geotagger-map-instruction-text').find('p').text(gettext('Grab and drag the MAP so that the marker is where the photographer was standing.'));
            this.options.currentPhotoId = options.photoId;
            this.options.fullScreenSrc = options.fullScreenSrc;
            this.options.fullScreenWidth = options.fullScreenWidth;
            this.options.fullScreenHeight = options.fullScreenHeight;
            this.options.isMapview = options.isMapview;
            this.options.isGame = options.isGame;
            this.options.isGallery = options.isGallery;
            this.options.markerLocked = options.markerLocked;
            this.streetPanorama.setVisible(false);
            this.azimuthLine.setVisible(false);
            if (options.markerLocked) {
                this.lockMapToCenter();
            } else {
                this.unlockMapFromCenter();
            }
            this.firstMoveDone = false;
            this.setSaveButtonToInitial();
            this.options.tutorialClosed = options.tutorialClosed;
            if (options.tutorialClosed) {
                this.hideInstructions();
            } else {
                this.showInstructions();
            }
            this.hintUsed = options.hintUsed;
            if (options.hintUsed) {
                this.showDescriptions();
            } else {
                this.descriptionButton.show();
            }
            this.angleBetweenMouseAndMarker = null;
            this.angleBetweenMarkerAndPanoramaMarker = null;
            this.azimuthLineEndPoint = null;
            this.saveAzimuth = false;
            this.drawAzimuthLineOnMouseMove = !isMobile;
            if (this.heatmap) {
                this.heatmap.setMap(null);
            }
            if (this.playerGuessMarker) {
                this.playerGuessMarker.setVisible(false);
            }
            if (this.feedbackEstimatedLocationMarker) {
                this.feedbackEstimatedLocationMarker.setVisible(false);
            }
            $('#ajp-geotagger-guess-marker').show();
            if (isMobile) {
                $('#ajp-geotagger-search-box').addClass('hidden');
            } else {
                $('#ajp-geotagger-show-search-button').hide();
            }
            this.feedbackMode = false;
            this.guessingStarted = true;
            google.maps.event.trigger(this.map, 'resize');
            this.map.setCenter(new google.maps.LatLng(options.startLat, options.startLng));
            this.map.setZoom(16);
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
                draggingCursor: 'url(/static/images/material-design-icons/ajapaik_custom_size_panorama.svg) 18 18, auto'
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
            this.firstMoveDone = false;
            this.lockButton.removeClass('active');
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
            this.azimuthLine.setVisible(false);
            this.panoramaMarker.setVisible(false);
            this.saveAzimuth = false;
            this.setCorrectInstructionString();
        },
        unlockMapFromCenter: function () {
            $('#ajp-geotagger-guess-marker').hide();
            this.firstMoveDone = false;
            this.lockButton.addClass('active');
            this.realMarker.setVisible(true);
            this.realMarker.set('draggable', true);
            this.map.set('scrollwheel', true);
            this.customFFWheelFunctionActive = false;
            this.customNonFFWheelFunctionActive = false;
            this.mapMarkerDragListenerActive = true;
            this.mapMarkerDragendListenerActive = true;
            this.setCursorToAuto();
            this.options.markerLocked = false;
            this.azimuthLine.setVisible(false);
            this.panoramaMarker.setVisible(false);
            this.saveAzimuth = false;
            this.setCorrectInstructionString();
        },
        setCorrectInstructionString: function () {
            var element = $('#ajp-geotagger-map-instruction-text').find('p');
            if (this.options.mode === 'vantage') {
                if (this.options.markerLocked) {
                    if (this.saveAzimuth) {
                        element.text(gettext('Click the green button to save both the location and the direction of the view. Click on the map to unlock the direction, drag map to correct the location.'));
                    } else {
                        if (this.firstMoveDone) {
                            element.text(gettext('Click on the map to lock the direction of the view or click yellow button to save only the location.'));
                        } else {
                            element.text(gettext('Grab and drag the MAP so that the marker is where the photographer was standing.'));
                        }
                    }
                } else {
                    if (this.saveAzimuth) {
                        element.text(gettext('Click the green button to save both the location and the direction of the view. Click on the map to unlock the direction, drag MARKER to correct the location.'));
                    } else if (this.firstMoveDone) {
                        element.text(gettext('Click on the map to lock the direction of the view or click yellow button to save only the location.'));
                    } else {
                        element.text(gettext('Now you can drag the MARKER where the photographer was standing and the MAP separately.'));
                    }
                }
            } else if (this.options.mode === 'approximate') {
                element.text(gettext('Drag the map so that the circle covers the approximate location, click save when ready.'));
            } else {
                element.text(gettext('Drag the map so that the marker is on top of the object you see on the picture, click save when ready.'));
            }
            google.maps.event.trigger(this.map, 'resize');
        },
        flipImages: function () {
            this.geotaggerImageThumb.toggleClass('ajp-photo-flipped');
            $('#ajp-geotagger-full-screen-image').toggleClass('ajp-photo-flipped');
        },
        fitGuessPhotosToContainers: function () {
            var newMargin,
                targetParent = this.geotaggerImageThumb.parent().parent(),
                confirmControls = $('#ajp-geotagger-confirm-controls'),
                buttonControls = $('#ajp-geotagger-button-controls'),
                geotaggerPanel = $('#ajp-geotagger-panel'),
                thumbHeight = this.geotaggerImageThumb.height();
            if (window.matchMedia("(min-width: 992px)").matches) {
                confirmControls.removeClass('col-xs-offset-6 col-sm-offset-6');
                targetParent.css('width', geotaggerPanel.width()).css('height', 'auto');
                newMargin = geotaggerPanel.height() - buttonControls.height() - thumbHeight - 41;
                if (newMargin > 0) {
                    confirmControls.css('margin-top', newMargin + 'px');
                }
                geotaggerPanel.css('max-height', '100%').css('height', '100%');
            } else {
                geotaggerPanel.css('max-height', '30%').css('height', '100%');
                targetParent.css('height', geotaggerPanel.height() + 'px').css('width', '50%');
                newMargin = thumbHeight - buttonControls.height() - 41;
                if (newMargin > 0) {
                    confirmControls.css('margin-top', newMargin + 'px');
                }
                // On small screens, don't constrain whole interface to screen height
                geotaggerPanel.css('max-height', '100%').css('height', 'auto');
                if (thumbHeight < buttonControls.height()) {
                    confirmControls.addClass('col-xs-offset-6 col-sm-offset-6');
                } else {
                    confirmControls.removeClass('col-xs-offset-6 col-sm-offset-6');
                }
            }
        },
        showInstructions: function () {
            docCookies.setItem('ajapaik_closed_geotagger_instructions', false, 'Fri, 31 Dec 9999 23:59:59 GMT', '/',
                document.domain, false);
            this.mapInstructions.show();
            this.mapOpenInstructionsButton.hide();
            google.maps.event.trigger(this.map, 'resize');
        },
        hideInstructions: function () {
            docCookies.setItem('ajapaik_closed_geotagger_instructions', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/',
                document.domain, false);
            this.mapInstructions.hide();
            this.mapOpenInstructionsButton.show();
        },
        showDescriptions: function () {
            this.descriptionButton.hide();
            this.description.removeClass('hidden');
            this.source.removeClass('hidden');
            this.hintUsed = true;
            this.fitGuessPhotosToContainers();
        },
        setSaveButtonToInitial: function () {
            $('#ajp-geotagger-save-button').removeClass('btn-warning btn-success').addClass('btn-disabled');
        },
        setSaveButtonToLocationOnly: function () {
            $('#ajp-geotagger-save-button').removeClass('btn-disabled btn-success').addClass('btn-warning');
        },
        setSaveButtonToLocationAndAzimuth: function () {
            $('#ajp-geotagger-save-button').removeClass('btn-disabled btn-warning').addClass('btn-success');
        },
        saveSkip: function () {
            $('#ajp-geotagger-game-buttons').hide();
            $.ajax({
                type: 'POST',
                url: saveLocationURL,
                data: {
                    photo: this.options.currentPhotoId,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success: function () {
                    $('#ajp-geotagger-game-buttons').show();
                },
                error: function () {
                    $('#ajp-geotagger-game-buttons').show();
                },
                dataType: 'json'
            });
        },
        saveGeotag: function () {
            $('#ajp-geotagger-game-buttons').hide();
            this.feedbackMode = true;
            this.mapMarkerDragListenerActive = false;
            this.mapMarkerDragendListenerActive = false;
            var mapTypeId = this.map.getMapTypeId(),
                lat = this.realMarker.getPosition().lat(),
                lon = this.realMarker.getPosition().lng(),
                that = this,
                data = {
                    lat: lat,
                    lon: lon,
                    type: 0,
                    zoom_level: this.map.getZoom(),
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
                if (typeof window.reportGeotaggerSaveLocationAndDirection === 'function') {
                    window.reportGeotaggerSaveLocationAndDirection(that.options.currentPhotoId);
                }
            } else {
                if (typeof window.reportGeotaggerSaveLocationOnly === 'function') {
                    window.reportGeotaggerSaveLocationOnly(that.options.currentPhotoId);
                }
            }
            $.ajax({
                type: 'POST',
                url: saveLocationURL,
                data: data,
                success: function (response) {
                    var playerGuessLatlng = that.realMarker.getPosition();
                    updateLeaderboard();
                    $('input[name="difficulty"]').prop('checked', false);
                    that.lockButton.hide();
                    $('#ajp-geotagger-button-controls').hide();
                    $('#ajp-geotagger-confirm-controls').hide();
                    $('#ajp-geotagger-feedback-points').html(gettext('Points awarded') + ': ' + response.current_score);
                    $('#ajp-geotagger-feedback-message').html(response.feedback_message);
                    $('#ajp-geotagger-feedback').show();
                    $('#ajp-geotagger-current-stats').hide();
                    that.fitGuessPhotosToContainers();
                    if (response.heatmap_points) {
                        that.displayFeedbackHeatmap(response);
                        that.realMarker.setVisible(false);
                        $('#ajp-geotagger-guess-marker').hide();
                        that.playerGuessMarker.setPosition(playerGuessLatlng);
                        that.playerGuessMarker.setVisible(true);
                    }
                    // TODO: Let's try not to couple geotagger with everything else like last time
                    window.photoModalGeotaggingUserCount = response.new_geotag_count;
                    window.photoModalPhotoLat = response.estimated_location[0];
                    window.photoModalPhotoLng = response.estimated_location[1];
                    window.photoModalPhotoAzimuth = response.azimuth;
                    $('#ajp-geotagger-game-buttons').show();
                    if (response.current_score > 0 && typeof window.reportGeotaggerCorrect === 'function') {
                        window.reportGeotaggerCorrect();
                    }
                    if (parseInt(response.current_score === 0 && typeof window.reportGeotaggerIncorrect === 'function')) {
                        window.reportGeotaggerIncorrect();
                    }
                    if (typeof window.reportGeotaggerNewlyMappedPhoto && response.new_geotag_count === 1 &&
                        response.estimated_location[0] && response.estimated_location[1]) {
                        window.reportGeotaggerNewlyMappedPhoto();
                    }
                },
                error: function () {
                    $('#ajp-geotagger-game-buttons').show();
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
                this.feedbackEstimatedLocationMarker.setVisible(true);
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
        },
        delayedReportSearch: function (term) {
            if (this.searchReportTimeout) {
                clearTimeout(this.searchReportTimeout);
            }
            this.searchReportTimeout = setTimeout(function () {
                if (typeof window.reportGeotaggerSearch === 'function') {
                    window.reportGeotaggerSearch(term);
                }
            }, 2000);
        }
    };
    $.fn.AjapaikGeotagger = function (options) {
        return this.each(function () {
            $(this).data('AjapaikGeotagger', new AjapaikGeotagger(this, options));
        });
    };
}(jQuery));