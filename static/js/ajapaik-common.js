var map,
    disableSave = true,
    streetPanorama,
    infoWindow,
    getMap,
    saveLocation,
    saveLocationCallback,
    saveLocationButton,
    saveDirection = false,
    radianAngle,
    degreeAngle,
    azimuthListenerActive = false,
    azimuthLineEndPoint,
    marker,
    popover,
    popoverShown = false,
    panoramaMarker,
    centerMarker,
    setCursorToPanorama,
    setCursorToAuto,
    mapOpts,
    streetViewOptions = {
        panControl: true,
        panControlOptions: {
            position: window.google.maps.ControlPosition.LEFT_CENTER
        },
        zoomControl: true,
        zoomControlOptions: {
            position: window.google.maps.ControlPosition.LEFT_CENTER
        },
        addressControl: false,
        linksControl: true,
        linksControlOptions: {
            position: window.google.maps.ControlPosition.BOTTOM_CENTER
        },
        enableCloseButton: true,
        visible: false
    },
    dottedAzimuthLineSymbol,
    dottedAzimuthLine,
    getQueryParameterByName,
    prepareFullscreen,
    adjustModalMaxHeightAndPosition,
    firstDragDone = false,
    showScoreboard,
    hideScoreboard,
    updateLeaderboard,
    now,
    gameMap,
    isPhotoview,
    gameRedirectURI,
    lastTriggeredWheeling,
    wheelEventFF,
    wheelEventNonFF,
    mapMousemoveListenerFunction,
    mapClickListenerFunction,
    mapIdleListenerFunction,
    mapDragstartListenerFunction,
    mapClickListenerActive = false,
    mapDragstartListenerActive = false,
    mapIdleListenerActive = false,
    mapMousemoveListenerActive = false,
    mapDragendListenerActive = false,
    mapClickListener,
    mapDragstartListener,
    mapGameIdleListener,
    mapMapviewIdleListener,
    mapMapviewClickListener,
    mapBoundsChangedListener,
    mapMousemoveListener,
    mapTypeChangedListener,
    mapDragListener,
    guessLocationStarted = false,
    mapPositionChangedListener,
    streetviewVisibleChangedListener,
    streetviewPanoChangedListener,
    streetviewCloseclickListener,
    mapPanoChangedListener,
    mapDisplayHeatmapWithEstimatedLocation,
    lockButton,
    mapDragendListenerFunction,
    markerLocked = true,
    mapMarkerDragListenerFunction,
    mapMarkerDragendListenerFunction,
    mapMarkerDragListener,
    mapMarkerDragendListener,
    mapMarkerPositionChangedListener,
    windowResizeListenerFunction,
    windowResizeListener,
    realMapElement,
    photoModalCurrentlyOpenPhotoId,
    currentlySelectedRephotoId,
    photoModalFullscreenImageUrl,
    photoModalFullscreenImageSize,
    photoModalCurrentPhotoFlipStatus,
    userFlippedPhoto = false,
    photoModalRephotoArray,
    userClosedRephotoTools = false,
    fullscreenEnabled = false,
    heatmap,
    guessResponseReceived = false,
    gameHintUsed = false,
    currentPhotoDescription = false,
    heatmapEstimatedLocationMarker,
    userClosedTutorial = false,
    tutorialPanel,
    tutorialPanelSettings = {
        selector: 'body',
        position: 'center',
        controls: {
            buttons: 'closeonly',
            iconfont: 'bootstrap'
        },
        bootstrap: 'default',
        title: window.gettext('Tutorial'),
        draggable: {
            handle: '.jsPanel-hdr',
            containment: '#ajapaik-map-container'
        },
        size: {
            height: 'auto'
        },
        id: 'ajapaik-tutorial-js-panel'
    },
    geotagInfoPanel,
    geotagInfoPanelSettings = {
        selector: 'body',
        position: 'center',
        controls: {
            buttons: 'closeonly',
            iconfont: 'bootstrap'
        },
        bootstrap: 'default',
        title: false,
        draggable: {
            handle: '.jsPanel-hdr',
            containment: '#ajapaik-map-container'
        },
        size: {
            height: 'auto'
        },
        id: 'ajapaik-geotag-info-js-panel'
    },
    comingBackFromGuessLocation = false;

(function ($) {
    'use strict';

    if ($(window).height() >= 320) {
        $(window).resize(adjustModalMaxHeightAndPosition).trigger('resize');
    }

    getMap = function (startPoint, startingZoom, isGameMap) {
        var latLng,
            zoomLevel,
            mapTypeIds;

        gameMap = isGameMap;

        if (!startPoint) {
            latLng = new window.google.maps.LatLng(59, 26);
            startingZoom = 8;
        } else {
            latLng = startPoint;
        }

        if (!startingZoom) {
            zoomLevel = 13;
        } else {
            zoomLevel = startingZoom;
        }

        streetPanorama = new window.google.maps.StreetViewPanorama(document.getElementById('ajapaik-map-canvas'), streetViewOptions);

        mapTypeIds = [];
        for (var type in window.google.maps.MapTypeId) {
            if (window.google.maps.MapTypeId.hasOwnProperty(type)) {
                mapTypeIds.push(window.google.maps.MapTypeId[type]);
            }

        }
        mapTypeIds.push('OSM');

        mapOpts = {
            zoom: zoomLevel,
            scrollwheel: false,
            center: latLng,
            mapTypeControl: true,
            panControl: false,
            panControlOptions: {
                position: window.google.maps.ControlPosition.RIGHT_TOP
            },
            zoomControl: true,
            zoomControlOptions: {
                position: window.google.maps.ControlPosition.RIGHT_TOP
            },
            streetViewControl: true,
            streetViewControlOptions: {
                position: window.google.maps.ControlPosition.RIGHT_TOP
            },
            streetView: streetPanorama,
            mapTypeControlOptions: {
                mapTypeIds: mapTypeIds,
                position: window.google.maps.ControlPosition.BOTTOM_CENTER
            }
        };

        map = new window.google.maps.Map(document.getElementById('ajapaik-map-canvas'), mapOpts);

        map.mapTypes.set('OSM', new google.maps.ImageMapType({
            getTileUrl: function (coord, zoom) {
                return 'http://tile.openstreetmap.org/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
            },
            tileSize: new google.maps.Size(256, 256),
            name: 'OpenStreetMap',
            maxZoom: 18
        }));

        lockButton = document.createElement('button');
        $(lockButton).addClass('btn').addClass('btn-default').addClass('ajapaik-marker-center-lock-button');

        map.controls[window.google.maps.ControlPosition.RIGHT_TOP].push(lockButton);

        var input = /** @type {HTMLInputElement} */(document.getElementById('pac-input'));
        map.controls[window.google.maps.ControlPosition.TOP_RIGHT].push(input);

        var searchBox = new google.maps.places.SearchBox(/** @type {HTMLInputElement} */(input));

        window.google.maps.event.addListener(searchBox, 'places_changed', function () {
            var places = searchBox.getPlaces();
            if (places.length === 0) {
                return;
            }
            map.setCenter(places[0].geometry.location);
        });

        window.google.maps.event.addListener(map, 'bounds_changed', function () {
            var bounds = map.getBounds();
            searchBox.setBounds(bounds);
        });

        if (isGameMap) {
            $('<div/>').addClass('center-marker').appendTo(map.getDiv()).click(function () {
                var that = $(this);
                if (!that.data('win')) {
                    that.data('win').bindTo('position', map, 'center');
                }
                that.data('win').open(map);
            });
        }

        streetviewVisibleChangedListener = window.google.maps.event.addListener(streetPanorama, 'visible_changed', function () {
            if (streetPanorama.getVisible()) {
                if (isGameMap) {
                    window._gaq.push(['_trackEvent', 'Game', 'Opened Street View']);
                } else {
                    window._gaq.push(['_trackEvent', 'Map', 'Opened Street View']);
                }
                // Currently we are not displaying the save button when Street View is open
                saveLocationButton.hide();
                $('#ajapaik-map-button-container').show();
                $('.ajapaik-close-streetview-button').show().parent().show();
            } else {
                if (!guessLocationStarted) {
                    $('#ajapaik-map-button-container').hide();
                } else {
                    $('#ajapaik-map-button-container').show();
                }
                $('.ajapaik-close-streetview-button').hide().parent().hide();
                saveLocationButton.show();
            }
        });

        streetviewPanoChangedListener = window.google.maps.event.addListener(streetPanorama, 'pano_changed', function () {
            if (isGameMap) {
                window._gaq.push(['_trackEvent', 'Game', 'Street View Movement']);
            } else {
                window._gaq.push(['_trackEvent', 'Map', 'Street View Movement']);
            }
        });

        streetviewCloseclickListener = window.google.maps.event.addListener(streetPanorama, 'closeclick', function () {
            // Closing Street View from the X button must also show the save button again
            saveLocationButton.show();
        });

        mapTypeChangedListener = window.google.maps.event.addListener(map, 'maptypeid_changed', function () {
            if (isGameMap) {
                window._gaq.push(['_trackEvent', 'Game', 'Map type changed']);
            } else {
                window._gaq.push(['_trackEvent', 'Map', 'Map type changed']);
            }
        });
    };

    Math.getAzimuthBetweenMouseAndMarker = function (e, marker) {
        var x = e.latLng.lat() - marker.position.lat(),
            y = e.latLng.lng() - marker.position.lng();
        return Math.atan2(y, x);
    };

    Math.getAzimuthBetweenTwoMarkers = function (marker1, marker2) {
        if (marker1 && marker2) {
            var x = marker2.position.lat() - marker1.position.lat(),
                y = marker2.position.lng() - marker1.position.lng();
            return Math.atan2(y, x);
        }
        return false;
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
        return new window.google.maps.LatLng(newX, newY);
    };

    dottedAzimuthLineSymbol = {
        path: window.google.maps.SymbolPath.CIRCLE,
        strokeOpacity: 1,
        strokeWeight: 1.5,
        strokeColor: 'red',
        scale: 0.75
    };

    dottedAzimuthLine = new window.google.maps.Polyline({
        geodesic: false,
        strokeOpacity: 0,
        icons: [
            {
                icon: dottedAzimuthLineSymbol,
                offset: '0',
                repeat: '7px'
            }
        ],
        visible: false,
        clickable: false
    });


    getQueryParameterByName = function (name) {
        var match = new RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
        return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
    };

    prepareFullscreen = function (width, height, customSelector) {
        if (!customSelector) {
            customSelector = '#ajapaik-full-screen-image';
        }
        var that = $(customSelector),
            aspectRatio = width / height,
            newWidth = parseInt(screen.height * aspectRatio, 10),
            newHeight = parseInt(screen.width / aspectRatio, 10);
        if (newWidth > screen.width) {
            newWidth = screen.width;
        } else {
            newHeight = screen.height;
        }
        that.css('margin-left', (screen.width - newWidth) / 2 + 'px');
        that.css('margin-top', (screen.height - newHeight) / 2 + 'px');
        that.css('width', newWidth);
        that.css('height', newHeight);
        that.css('opacity', 1);
    };

    // Modal centering code from http://codepen.io/dimbslmh/pen/mKfCc
    adjustModalMaxHeightAndPosition = function () {
        $('.modal').each(function () {
            if ($(this).hasClass('in') === false) {
                $(this).show();
            }
            var contentHeight = $(window).height() - 60,
                headerHeight = $(this).find('.modal-header').outerHeight() || 2,
                footerHeight = $(this).find('.modal-footer').outerHeight() || 2;

            $(this).find('.modal-content').css({
                'max-height': function () {
                    return contentHeight;
                }
            });

            $(this).find('.modal-body').css({
                'max-height': function () {
                    return contentHeight - (headerHeight + footerHeight);
                }
            });

            $(this).find('.modal-dialog').addClass('modal-dialog-center').css({
                'margin-top': function () {
                    return -($(this).outerHeight() / 2);
                },
                'margin-left': function () {
                    return -($(this).outerWidth() / 2);
                }
            });
            if ($(this).hasClass('in') === false) {
                $(this).hide();
            }
        });
    };

    showScoreboard = function () {
        var scoreContainer = $('#ajapaik-header').find('.score_container');
        scoreContainer.find('.scoreboard li').not('.you').add('h2').slideDown();
        scoreContainer.find('#facebook-connect').slideDown();
        scoreContainer.find('#facebook-connected').slideDown();
        scoreContainer.find('#google-plus-connect').slideDown();
    };

    hideScoreboard = function () {
        var scoreContainer = $('#ajapaik-header').find('.score_container');
        scoreContainer.find('.scoreboard li').not('.you').add('h2').slideUp();
        scoreContainer.find('#facebook-connect').slideUp();
        scoreContainer.find('#facebook-connected').slideUp();
        scoreContainer.find('#google-plus-connect').slideUp();
    };

    updateLeaderboard = function () {
        $('.score_container').find('.scoreboard').load(window.leaderboardUpdateURL);
    };

    saveLocationCallback = function (resp) {
        var message = resp.feedback_message,
            hideFeedback = false,
            heatmapPoints,
            currentScore = 0,
            tagsWithAzimuth = 0,
            newEstimatedLocation,
            confidence = 0;
        if (resp.is_correct) {
            hideFeedback = false;
            if (gameMap) {
                window._gaq.push(['_trackEvent', 'Game', 'Correct coordinates']);
            } else {
                window._gaq.push(['_trackEvent', 'Map', 'Correct coordinates']);
            }
        } else if (resp.location_is_unclear) {
            if (gameMap) {
                window._gaq.push(['_trackEvent', 'Game', 'Coordinates uncertain']);
            } else {
                window._gaq.push(['_trackEvent', 'Map', 'Coordinates uncertain']);
            }
        } else if (!resp.is_correct) {
            hideFeedback = true;
            if (gameMap) {
                window._gaq.push(['_trackEvent', 'Game', 'Wrong coordinates']);
            } else {
                window._gaq.push(['_trackEvent', 'Map', 'Wrong coordinates']);
            }
        }
        if (resp.heatmap_points) {
            heatmapPoints = resp.heatmap_points;
        }
        if (resp.azimuth_tags) {
            tagsWithAzimuth = resp.azimuth_tags;
        }
        if (resp.current_score) {
            currentScore = resp.current_score;
        }
        if (resp.estimated_location) {
            newEstimatedLocation = resp.estimated_location;
        }
        if (resp.confidence) {
            confidence = resp.confidence;
        }
        window.handleGuessResponse({feedbackMessage: message, hideFeedback: hideFeedback,
            heatmapPoints: heatmapPoints, currentScore: currentScore, tagsWithAzimuth: tagsWithAzimuth,
            newEstimatedLocation: newEstimatedLocation, confidence: confidence});
    };

    saveLocation = function (marker, photoId, photoFlipStatus, hintUsed, userFlippedPhoto, degreeAngle, azimuthLineEndPoint, origin) {
        var lat = marker.getPosition().lat(),
            lon = marker.getPosition().lng(),
            data = {
                photo_id: photoId,
                hint_used: hintUsed,
                zoom_level: map.zoom,
                origin: origin,
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            };
        if (degreeAngle && saveDirection) {
            data.azimuth = degreeAngle;
        } else {
            dottedAzimuthLine.setVisible(false);
        }
        if (azimuthLineEndPoint && saveDirection) {
            data.azimuth_line_end_point = azimuthLineEndPoint;
        }
        if (lat && lon) {
            data.lat = lat;
            data.lon = lon;
        }
        if (userFlippedPhoto) {
            data.flip = photoFlipStatus;
        }
        $.ajax({
            url: saveLocationURL,
            data: data,
            method: 'POST',
            success: function (resp) {
                saveLocationCallback(resp);
            }
        });
    };

    $('.filter-box select').change(function () {
        var uri = new window.URI(location.href),
            newQ = {area: $(this).val()},
            isFilterEmpty = false;
        uri.removeQuery(Object.keys(newQ));
        $.each(newQ, function (i, ii) {
            ii = String(ii);
            isFilterEmpty = ii === '';
        });

        if (!isFilterEmpty) {
            uri = uri.addQuery(newQ);
        }

        uri = uri.addQuery({fromSelect: 1});

        if (isPhotoview) {
            uri = new window.URI('/game');
            uri.addQuery(newQ);
            gameRedirectURI = uri.toString();
        } else {
            window.location.href = uri.toString();
        }
    });

    $(document).on('click', '#ajapaik-header-map-button', function () {
        window.location.href = '/map?area=' + window.areaId;
    });

    $(document).on('click', '#ajapaik-header-game-button', function () {
        window.location.href = '/game?area=' + window.areaId;
    });

    // Firefox and Opera cannot handle modal taking over focus
    $.fn.modal.Constructor.prototype.enforceFocus = function () {
        $.noop();
    };

    // Our own custom zooming functions to fix the otherwise laggy zooming for mobile
    wheelEventFF = function (e) {
        now = new Date().getTime();
        if (!lastTriggeredWheeling) {
            lastTriggeredWheeling = now - 250;
        }
        if (now - 250 > lastTriggeredWheeling) {
            lastTriggeredWheeling = now;
            if (e.detail < 0) {
                map.setZoom(map.zoom + 1);
            } else {
                if (map.zoom > 14) {
                    map.setZoom(map.zoom - 1);
                }
            }
        }
    };

    wheelEventNonFF = function (e) {
        now = new Date().getTime();
        if (!lastTriggeredWheeling) {
            lastTriggeredWheeling = now - 100;
        }
        if (now - 100 > lastTriggeredWheeling) {
            lastTriggeredWheeling = now;
            if (e.wheelDelta > 0) {
                map.setZoom(map.zoom + 1);
            } else {
                if (map.zoom > 14) {
                    map.setZoom(map.zoom - 1);
                }
            }
        }
    };

    windowResizeListenerFunction = function () {
        if (markerLocked && !fullscreenEnabled && !guessResponseReceived) {
            mapMousemoveListener = window.google.maps.event.addListener(map, 'mousemove', mapMousemoveListenerFunction);
            mapMousemoveListenerActive = true;
            dottedAzimuthLine.setVisible(false);
            if (panoramaMarker) {
                panoramaMarker.setVisible(false);
            }
        }
    };

    mapMousemoveListenerFunction = function (e) {
        // The mouse is moving, therefore we haven't locked on a direction
        saveDirection = false;
        if (!disableSave) {
            saveLocationButton.removeAttr('disabled');
            saveLocationButton.removeClass('btn-default');
            saveLocationButton.addClass('btn-warning');
            saveLocationButton.text(window.gettext('Save location only'));
        }
        if (e && marker.position) {
            radianAngle = Math.getAzimuthBetweenMouseAndMarker(e, marker);
            degreeAngle = Math.degrees(radianAngle);
        }
        if (panoramaMarker) {
            panoramaMarker.setMap(null);
        }
        if (firstDragDone) {
            setCursorToPanorama();
        }
        if (marker.position) {
            if (!window.isMobile && firstDragDone) {
                dottedAzimuthLine.setPath([marker.position, Math.calculateMapLineEndPoint(degreeAngle, marker.position, 0.05)]);
                dottedAzimuthLine.setMap(map);
                dottedAzimuthLine.icons = [
                    {icon: dottedAzimuthLineSymbol, offset: '0', repeat: '7px'}
                ];
                dottedAzimuthLine.setVisible(true);
            } else {
                dottedAzimuthLine.setVisible(false);
            }
        }
    };

    mapClickListenerFunction = function (e) {
        if (infoWindow !== undefined) {
            centerMarker.show();
            infoWindow.close();
            infoWindow = undefined;
        }
        radianAngle = Math.getAzimuthBetweenMouseAndMarker(e, marker);
        azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
        degreeAngle = Math.degrees(radianAngle);
        if (window.isMobile) {
            dottedAzimuthLine.setPath([marker.position, Math.calculateMapLineEndPoint(degreeAngle, marker.position, 0.05)]);
            dottedAzimuthLine.setMap(map);
            dottedAzimuthLine.icons = [
                {icon: dottedAzimuthLineSymbol, offset: '0', repeat: '7px'}
            ];
            dottedAzimuthLine.setVisible(true);
        }
        if (azimuthListenerActive) {
            mapMousemoveListenerActive = false;
            window.google.maps.event.clearListeners(map, 'mousemove');
            saveDirection = true;
            if (!disableSave) {
                saveLocationButton.removeAttr('disabled');
                saveLocationButton.removeClass('btn-default');
                saveLocationButton.removeClass('btn-warning');
                saveLocationButton.addClass('btn-success');
                saveLocationButton.text(window.gettext('Save location and direction'));
            }
            dottedAzimuthLine.icons[0].repeat = '2px';
            dottedAzimuthLine.setPath([marker.position, e.latLng]);
            dottedAzimuthLine.setVisible(true);
            if (panoramaMarker) {
                panoramaMarker.setMap(null);
            }
            var markerImage = {
                url: '/static/images/material-design-icons/ajapaik_custom_size_panorama.svg',
                origin: new window.google.maps.Point(0, 0),
                anchor: new window.google.maps.Point(18, 18),
                scaledSize: new window.google.maps.Size(36, 36)
            };
            panoramaMarker = new window.google.maps.Marker({
                map: map,
                draggable: false,
                position: e.latLng,
                icon: markerImage
            });
            setCursorToAuto();
        } else {
            if (!mapMousemoveListenerActive) {
                mapMousemoveListener = window.google.maps.event.addListener(map, 'mousemove', mapMousemoveListenerFunction);
                mapMousemoveListenerActive = true;
                window.google.maps.event.trigger(map, 'mousemove', e);
            }
        }
        azimuthListenerActive = !azimuthListenerActive;
    };

    mapIdleListenerFunction = function () {
        if (firstDragDone) {
            if (markerLocked) {
                azimuthListenerActive = true;
                marker.setPosition(map.getCenter());
            }
            if (!mapMousemoveListenerActive && !saveDirection) {
                mapMousemoveListener = window.google.maps.event.addListener(map, 'mousemove', mapMousemoveListenerFunction);
                mapMousemoveListenerActive = true;
            }
        }
    };

    mapDragstartListenerFunction = function () {
        if (markerLocked) {
            centerMarker = $('.center-marker');
            saveDirection = false;
            if (panoramaMarker) {
                panoramaMarker.setMap(null);
            }
            setCursorToPanorama();
            dottedAzimuthLine.setVisible(false);
            if (infoWindow !== undefined) {
                centerMarker.show();
                infoWindow.close();
                infoWindow = undefined;
            }
            if (!disableSave) {
                saveLocationButton.removeAttr('disabled');
                saveLocationButton.removeClass('btn-default');
                saveLocationButton.addClass('btn-warning');
                saveLocationButton.text(window.gettext('Save location only'));
            }
            azimuthListenerActive = false;
            dottedAzimuthLine.setVisible(false);
            mapMousemoveListenerActive = false;
            window.google.maps.event.clearListeners(map, 'mousemove');
        }
    };

    mapDragendListenerFunction = function () {
        if (markerLocked) {
            marker.setPosition(map.getCenter());
        }
    };

    mapMarkerDragListenerFunction = function () {
        radianAngle = Math.getAzimuthBetweenTwoMarkers(marker, panoramaMarker);
        degreeAngle = Math.degrees(radianAngle);
        if (saveDirection) {
            dottedAzimuthLine.setPath([marker.position, Math.calculateMapLineEndPoint(degreeAngle, panoramaMarker.position, 0.05)]);
            dottedAzimuthLine.icons = [
                {icon: dottedAzimuthLineSymbol, offset: '0', repeat: '7px'}
            ];
        } else {
            dottedAzimuthLine.setVisible(false);
        }
    };

    mapMarkerDragendListenerFunction = function () {
        if (saveDirection) {
            dottedAzimuthLine.setPath([marker.position, panoramaMarker.position]);
            dottedAzimuthLine.icons[0].repeat = '2px';
        } else {
            dottedAzimuthLine.setVisible(false);
        }
    };

    setCursorToPanorama = function () {
        map.setOptions({draggableCursor: 'url(/static/images/material-design-icons/ajapaik_custom_size_panorama.svg) 18 18, auto', draggingCursor: 'auto'});
    };

    setCursorToAuto = function () {
        map.setOptions({draggableCursor: 'auto', draggingCursor: 'auto'});
    };

    mapDisplayHeatmapWithEstimatedLocation = function (heatmapData) {
        var latLngBounds = new window.google.maps.LatLngBounds(),
            newLatLng,
            heatmapPoints = [],
            i;
        if (heatmapEstimatedLocationMarker) {
            heatmapEstimatedLocationMarker.setMap(null);
        }
        heatmapEstimatedLocationMarker = undefined;
        for (i = 0; i < heatmapData.heatmapPoints.length; i += 1) {
            newLatLng = new window.google.maps.LatLng(heatmapData.heatmapPoints[i][0], heatmapData.heatmapPoints[i][1]);
            heatmapPoints.push(newLatLng);
            latLngBounds.extend(newLatLng);
        }
        window.mapInfoPanelGeotagCountElement.html(heatmapData.heatmapPoints.length);
        window.mapInfoPanelAzimuthCountElement.html(heatmapData.tagsWithAzimuth);
        //window.mapInfoPanelConfidenceElement.html(heatmapData.confidence.toFixed(2));
        if (heatmapData.newEstimatedLocation && heatmapData.newEstimatedLocation[0] && heatmapData.newEstimatedLocation[1]) {
            heatmapEstimatedLocationMarker = new window.google.maps.Marker({
                position: new window.google.maps.LatLng(heatmapData.newEstimatedLocation[0], heatmapData.newEstimatedLocation[1]),
                map: window.map,
                title: window.gettext("Median guess"),
                draggable: false,
                icon: '/static/images/ajapaik_marker_35px_transparent.png'
            });
        }
        if (heatmapEstimatedLocationMarker) {
            window.map.setCenter(heatmapEstimatedLocationMarker.getPosition());
        } else {
            window.map.fitBounds(latLngBounds);
        }
        marker.setZIndex(window.google.maps.Marker.MAX_ZINDEX + 1);
        heatmapPoints = new window.google.maps.MVCArray(heatmapPoints);
        if (heatmap) {
            heatmap.setMap(null);
        }
        heatmap = new window.google.maps.visualization.HeatmapLayer({
            data: heatmapPoints
        });
        heatmap.setMap(window.map);
        heatmap.setOptions({radius: 50, dissipating: true});
    };

    $(document).on('click', '.ajapaik-marker-center-lock-button', function () {
        if (firstDragDone) {
            var t = $(this);
            window.centerMarker = $('.center-marker');
            if (t.hasClass('active')) {
                t.removeClass('active');
                window.centerMarker.show();
                window.marker.setVisible(false);
                window.marker.set('draggable', false);
                window.map.set('scrollwheel', false);
                window.realMapElement.addEventListener('mousewheel', window.wheelEventNonFF, true);
                window.realMapElement.addEventListener('DOMMouseScroll', window.wheelEventFF, true);
                window.google.maps.event.removeListener(mapMarkerDragListener);
                window.google.maps.event.removeListener(mapMarkerDragendListener);
                window.azimuthListenerActive = false;
                window.map.setCenter(window.marker.position);
                window.setCursorToPanorama();
                window.markerLocked = true;
            } else {
                t.addClass('active');
                window.centerMarker.hide();
                window.marker.setVisible(true);
                window.marker.setMap(map);
                window.marker.set('draggable', true);
                window.map.set('scrollwheel', true);
                window.realMapElement.removeEventListener('mousewheel', window.wheelEventNonFF, true);
                window.realMapElement.removeEventListener('DOMMouseScroll', window.wheelEventFF, true);
                mapMarkerDragListener = window.google.maps.event.addListener(window.marker, 'drag', window.mapMarkerDragListenerFunction);
                mapMarkerDragendListener = window.google.maps.event.addListener(window.marker, 'dragend', window.mapMarkerDragendListenerFunction);
                window.setCursorToAuto();
                window.markerLocked = false;
            }
        }
    });

    $(document).on('click', '.ajapaik-show-tutorial-button', function () {
        if (!gameHintUsed && !popoverShown && currentPhotoDescription) {
            $('[data-toggle="popover"]').popover('show');
            popoverShown = true;
        } else if (!gameHintUsed && popoverShown && currentPhotoDescription) {
            $('[data-toggle="popover"]').popover('hide');
            popoverShown = false;
        }
        if (!tutorialPanel) {
            window.openTutorialPanel();
        } else {
            tutorialPanel.close();
            tutorialPanel = undefined;
        }
    });

    $(document).on('click', '.ajapaik-header-info-button', function () {
        if (!geotagInfoPanel) {
            window.openGeotagInfoPanel();
        } else {
            geotagInfoPanel.close();
            geotagInfoPanel = undefined;
        }
    });

    $(document).on('click', '.ajapaik-close-streetview-button', function () {
        map.getStreetView().setVisible(false);
    });

    window.openTutorialPanel = function () {
        tutorialPanelSettings.content = $('#ajapaik-tutorial-js-panel-content').html();
        if (window.isMobile) {
            tutorialPanelSettings.resizable = false;
            tutorialPanelSettings.draggable = false;
        }
        tutorialPanel = $.jsPanel(tutorialPanelSettings);
    };

    window.openGeotagInfoPanel = function () {
        geotagInfoPanelSettings.content = $('#ajapaik-geotag-js-panel-content').html();
        if (window.isMobile) {
            geotagInfoPanelSettings.resizable = false;
            geotagInfoPanelSettings.draggable = false;
        }
        geotagInfoPanel = $.jsPanel(geotagInfoPanelSettings);
    };

    $('body').on('jspanelclosed', function closeHandler(event, id) {
        if (id === 'ajapaik-tutorial-js-panel') {
            $('[data-toggle="popover"]').popover('hide');
            popoverShown = false;
            window.userClosedTutorial = true;
            tutorialPanel = undefined;
            window.docCookies.setItem('ajapaik_closed_tutorial', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
            //$('body').off('jspanelclosed', closeHandler);
        } else if (id === 'ajapaik-geotag-info-js-panel') {
            geotagInfoPanel = undefined;
            window.docCookies.setItem('ajapaik_closed_geotag_info_' + window.areaId, true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
            //$('body').off('jspanelclosed', closeHandler);
        }
    });
}(jQuery));