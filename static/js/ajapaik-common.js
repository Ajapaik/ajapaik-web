var map,
    disableSave = true,
    streetPanorama,
    infoWindow,
    input,
    searchBox,
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
    popoverShown = false,
    panoramaMarker,
    centerMarker,
    setCursorToPanorama,
    setCursorToAuto,
    bypass = false,
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
    firstDragDone = false,
    scoreboardShown = false,
    showScoreboard,
    hideScoreboard,
    updateLeaderboard,
    now,
    paneNow,
    lastTriggeredPane,
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
    photoModalRephotoFullscreenImageUrl,
    photoModalRephotoFullscreenImageSize,
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
        selector: '#ajapaik-map-container',
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
        size: 'auto',
        id: 'ajapaik-tutorial-js-panel'
    },
    comingBackFromGuessLocation = false,
    hideUnlockedAzimuth,
    showUnlockedAzimuth,
    mapviewGameButton,
    getGeolocation,
    myLocationButton,
    closeStreetviewButton,
    albumSelectionDiv,
    handleAlbumChange,
    refreshFacebookCommentsCount,
    originalClosestLink;


(function ($) {
    'use strict';
    albumSelectionDiv = $('#ajapaik-album-selection-menu');
    albumSelectionDiv.justifiedGallery({
        rowHeight: 270,
        margins: 0,
        captions: false
    });

    getMap = function (startPoint, startingZoom, isGameMap, mapType) {
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

        if (isGameMap) {
            mapOpts = {
                zoom: zoomLevel,
                scrollwheel: false,
                center: latLng,
                mapTypeControl: true,
                zoomControl: true,
                panControl: false,
                zoomControlOptions: {
                    position: window.google.maps.ControlPosition.LEFT_CENTER
                },
                streetViewControl: true,
                streetViewControlOptions: {
                    position: window.google.maps.ControlPosition.LEFT_CENTER
                },
                streetView: streetPanorama,
                mapTypeControlOptions: {
                    mapTypeIds: mapTypeIds,
                    position: window.google.maps.ControlPosition.BOTTOM_CENTER
                }
            };
        } else {
            mapOpts = {
                zoom: zoomLevel,
                scrollwheel: true,
                center: latLng,
                mapTypeControl: true,
                panControl: false,
                zoomControl: true,
                zoomControlOptions: {
                    position: window.google.maps.ControlPosition.RIGHT_CENTER
                },
                streetViewControl: true,
                streetViewControlOptions: {
                    position: window.google.maps.ControlPosition.RIGHT_CENTER
                },
                streetView: streetPanorama,
                mapTypeControlOptions: {
                    mapTypeIds: mapTypeIds,
                    position: window.google.maps.ControlPosition.BOTTOM_CENTER
                }
            };
        }

        var allowedMapTypes = {
            roadmap: window.google.maps.MapTypeId.ROADMAP,
            satellite: window.google.maps.MapTypeId.ROADMAP,
            OSM: 'OSM'
        };
        if (allowedMapTypes[mapType]) {
            mapOpts.mapTypeId = allowedMapTypes[mapType];
        } else {
            mapOpts.mapTypeId = allowedMapTypes.OSM;
        }

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

        map.controls[window.google.maps.ControlPosition.BOTTOM_LEFT].push(lockButton);

        if (isGameMap) {
            input = /** @type {HTMLInputElement} */(document.getElementById('pac-input'));
            map.controls[window.google.maps.ControlPosition.TOP_LEFT].push(input);
        } else {
            input = /** @type {HTMLInputElement} */(document.getElementById('pac-input-mapview'));
            map.controls[window.google.maps.ControlPosition.TOP_RIGHT].push(input);
            mapviewGameButton = document.createElement('button');
            $(mapviewGameButton).addClass('btn btn-success btn-lg ajapaik-mapview-game-button ajapaik-zero-border-radius').prop('title', window.gettext('Geotag pictures')).html(window.gettext('Geotag pictures'));
            map.controls[window.google.maps.ControlPosition.BOTTOM_RIGHT].push(mapviewGameButton);
            myLocationButton = document.createElement('button');
            $(myLocationButton).addClass('btn btn-default btn-xs').prop('id', 'ajapaik-mapview-my-location-button').prop('title', window.gettext('Go to my location')).html('<i class="glyphicon ajapaik-icon ajapaik-icon-my-location"></i>');
            map.controls[window.google.maps.ControlPosition.TOP_RIGHT].push(myLocationButton);
            closeStreetviewButton = document.createElement('button');
            $(closeStreetviewButton).addClass('btn btn-default').prop('id', 'ajapaik-mapview-close-streetview-button').html(window.gettext('Close'));
            streetPanorama.controls[window.google.maps.ControlPosition.BOTTOM_RIGHT].push(closeStreetviewButton);
        }


        searchBox = new window.google.maps.places.SearchBox(/** @type {HTMLInputElement} */(input));

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
            if (window.toggleVisiblePaneElements) {
                paneNow = new Date().getTime();
                if (!lastTriggeredPane) {
                    lastTriggeredPane = paneNow - 500;
                    bypass = true;
                }
                if (paneNow - 500 > lastTriggeredPane || bypass) {
                    bypass = false;
                    lastTriggeredPane = paneNow;
                    window.toggleVisiblePaneElements();
                }
            }
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
                    $('#ajapaik-mapview-photo-panel').hide();
                }
                // Currently we are not displaying the save button when Street View is open
                saveLocationButton.hide();
                $('.ajapaik-close-streetview-button').show();
            } else {
                if (!guessLocationStarted) {
                    $('#ajapaik-mapview-photo-panel').show();
                }
                $('.ajapaik-close-streetview-button').hide();
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
            window.syncMapStateToURL();
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

    Math.simpleCalculateMapLineEndPoint = function (azimuth, startPoint, lineLength) {
        azimuth = Math.radians(azimuth);
        var newX = Math.cos(azimuth) * lineLength + startPoint.lat(),
            newY = Math.sin(azimuth) * lineLength + startPoint.lng();
        return new window.google.maps.LatLng(newX, newY);
    };

    Math.calculateMapLineEndPoint = function (bearing, startPoint, distance) {
        var earthRadius = 6371e3,
            angularDistance = distance / earthRadius,
            bearingRadians = Math.radians(bearing),
            startLatRadians = Math.radians(startPoint.lat()),
            startLonRadians = Math.radians(startPoint.lng()),
            endLatRadians = Math.asin(Math.sin(startLatRadians) * Math.cos(angularDistance) +
                Math.cos(startLatRadians) * Math.sin(angularDistance) * Math.cos(bearingRadians)),
            endLonRadians = startLonRadians + Math.atan2(Math.sin(bearingRadians) * Math.sin(angularDistance) *
                Math.cos(startLatRadians), Math.cos(angularDistance) - Math.sin(startLatRadians) *
                Math.sin(endLatRadians));

        return new window.google.maps.LatLng(Math.degrees(endLatRadians), Math.degrees(endLonRadians));
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

    getGeolocation = function getLocation(callback) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(callback);
        }
    };

    showScoreboard = function () {
        $('.ajapaik-navbar').find('.score_container').slideDown();
        scoreboardShown = true;
    };

    hideScoreboard = function () {
        $('.ajapaik-navbar').find('.score_container').slideUp();
        scoreboardShown = false;
    };

    updateLeaderboard = function () {
        var target = $('.score_container');
        if (window.albumId) {
            target.find('.scoreboard').load(window.leaderboardUpdateURL + 'album/' + window.albumId);
        } else {
            target.find('.scoreboard').load(window.leaderboardUpdateURL);
        }
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
        var mapTypeId = map.getMapTypeId(),
            lat = marker.getPosition().lat(),
            lon = marker.getPosition().lng();
        if (mapTypeId === 'roadmap') {
            mapTypeId = 0;
        } else if (mapTypeId === 'hybrid') {
            mapTypeId = 1;
        } else {
            mapTypeId = 2;
        }
        var data = {
                photo: photoId,
                hint_used: hintUsed,
                zoom_level: map.zoom,
                map_type: mapTypeId,
                type: 0,
                origin: origin,
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            };
        if (lat && lon) {
            data.lat = lat;
            data.lon = lon;
        }
        if (degreeAngle && saveDirection) {
            data.azimuth = degreeAngle;
            data.azimuth_line_end_lat = azimuthLineEndPoint[0];
            data.azimuth_line_end_lon = azimuthLineEndPoint[1];
        } else {
            dottedAzimuthLine.setVisible(false);
        }
        if (userFlippedPhoto) {
            data.flip = photoFlipStatus;
        }
        $.ajax({
            url: window.saveLocationURL,
            data: data,
            method: 'POST',
            success: function (resp) {
                saveLocationCallback(resp);
            }
        });
    };
    $(document).on('click', '#ajapaik-header-game-button', function () {
        if (window.isPhotoview && window.albumId && window.photoId) {
            window.location.href = '/game?album=' + window.albumId + '&photo=' + window.photoId;
        } else {
            if (!window.isGame && window.albumId) {
                window.location.href = '/game?album=' + window.albumId;
            }
        }
    });
    $(document).on('click', '#ajapaik-mobile-game-label', function () {
        if (window.isPhotoview && window.albumId && window.photoId) {
            window.location.href = '/game?album=' + window.albumId + '&photo=' + window.photoId;
        } else {
            if (!window.isGame && window.albumId) {
                window.location.href = '/game?album=' + window.albumId;
            }
        }
    });
    $(document).on('click', '#ajapaik-mobile-grid-label', function () {
        if (!window.isFrontpage && window.albumId) {
            if (window.getQueryParameterByName('limitToAlbum') == 0 && window.lastMarkerSet) {
                window.location.href = '/photos?set=' + window.lastMarkerSet;
            } else {
                window.location.href = '/photos/' + window.albumId + '/1';
            }
        }
    });
    $(document).on('click', '#ajapaik-header-grid-button', function () {
        if (!window.isFrontpage && window.albumId) {
            if (window.getQueryParameterByName('limitToAlbum') == 0 && window.lastMarkerSet) {
                window.location.href = '/photos?set=' + window.lastMarkerSet;
            } else {
                window.location.href = '/photos/' + window.albumId + '/1';
            }
        }
    });
    var handleGeolocation = function (position) {
        window.location.href = '/map?lat=' + position.coords.latitude + '&lng=' + position.coords.longitude + '&limitToAlbum=0&zoom=15';
    };
    $(document).on('click', '#ajapaik-header-map-button', function () {
        if (window.albumId) {
            window.location.href = '/map?album=' + window.albumId;
        } else {
            if (window.navigator.geolocation) {
                window.navigator.geolocation.getCurrentPosition(handleGeolocation);
            }
        }
    });
    $(document).on('click', '#ajapaik-mobile-map-label', function () {
        if (window.albumId) {
            window.location.href = '/map?album=' + window.albumId;
        } else {
            if (window.navigator.geolocation) {
                window.navigator.geolocation.getCurrentPosition(handleGeolocation);
            }
        }
    });
    $(document).on('click', '#ajapaik-header-curate-button', function () {
        window.location.href = '/curator/';
    });
    $(document).on('click', '#ajapaik-header-profile-button', function () {
        if (scoreboardShown) {
            hideScoreboard();
        } else {
            showScoreboard();
        }
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
    //refreshFacebookCommentsCount = function (ids) {
    //    var queryString = '',
    //        first = true;
    //    for (var i = 0, l = ids.length; i < l; i += 1) {
    //        if (first) {
    //            queryString += window.location.protocol + '//' + window.location.host + '/foto/' + ids[i] + '/';
    //            first = false;
    //        } else {
    //            queryString += ',' + window.location.protocol + '//' + window.location.host + '/foto/' + ids[i] + '/';
    //        }
    //    }
    //    $.get('http://graph.facebook.com/?ids=' + queryString, function(response) {
    //        window.handleCommentsCountResponse(response);
    //    });
    //};
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
                dottedAzimuthLine.setPath([marker.position, Math.simpleCalculateMapLineEndPoint(degreeAngle, marker.position, 0.01)]);
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
        if (!firstDragDone && !guessResponseReceived) {
            window.alert(window.gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view.'));
            return;
        }
        if (!window.guessResponseReceived) {
            radianAngle = Math.getAzimuthBetweenMouseAndMarker(e, marker);
            azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
            degreeAngle = Math.degrees(radianAngle);
            if (window.isMobile) {
                dottedAzimuthLine.setPath([marker.position, Math.simpleCalculateMapLineEndPoint(degreeAngle, marker.position, 0.01)]);
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
                if (marker.position && e.latLng) {
                    dottedAzimuthLine.setPath([marker.position, e.latLng]);
                    dottedAzimuthLine.setVisible(true);
                }
                if (panoramaMarker) {
                    panoramaMarker.setMap(null);
                }
                var markerImage = {
                    url: '/static/images/material-design-icons/ajapaik_custom_size_panorama.png',
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
        }
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
        firstDragDone = true;
        if (disableSave) {
            disableSave = false;
            saveLocationButton.removeAttr('disabled');
            saveLocationButton.removeClass('btn-default');
            saveLocationButton.addClass('btn-warning');
            saveLocationButton.text(window.gettext('Save location only'));
        }
    };

    mapMarkerDragListenerFunction = function () {
        radianAngle = Math.getAzimuthBetweenTwoMarkers(marker, panoramaMarker);
        degreeAngle = Math.degrees(radianAngle);
        if (saveDirection) {
            dottedAzimuthLine.setPath([marker.position, Math.simpleCalculateMapLineEndPoint(degreeAngle, panoramaMarker.position, 0.01)]);
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
        heatmap.setOptions({radius: 50, dissipating: false});
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
        if (!gameHintUsed && !popoverShown && currentPhotoDescription && !window.isMobile) {
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
    $(document).on('click', '.ajapaik-album-selection-item', function (e) {
        window.previousAlbumId = window.albumId;
        window.albumId = e.target.dataset.id;
        window.albumName = e.target.dataset.name;
        window.currentAlbumPhotoCount = e.target.dataset.photos;
        $('#ajapaik-album-selection-navmenu').offcanvas('toggle');
        window.handleAlbumChange();
    });
    window.openPhotoUploadModal = function () {
        if (window.photoModalCurrentlyOpenPhotoId) {
            $.ajax({
                cache: false,
                url: '/photo_upload_modal/' + window.photoModalCurrentlyOpenPhotoId + '/',
                success: function (result) {
                    var rephotoUploadModal = $('#ajapaik-rephoto-upload-modal');
                    rephotoUploadModal.data('bs.modal', null);
                    rephotoUploadModal.html(result).modal();
                }
            });
        }
    };
    $(document).on('click', '#ajapaik-photo-modal-add-rephoto', function () {
        if (window.isFrontpage) {
            window._gaq.push(['_trackEvent', 'Gallery', 'Photo modal add rephoto click']);
        } else if (window.isMapview) {
            window._gaq.push(['_trackEvent', 'Map', 'Photo modal add rephoto click']);
        }
        window.openPhotoUploadModal();
    });
    $(document).on('click', '#ajapaik-header-menu-button', function () {
        if (window.isFrontpage) {
            window._gaq.push(['_trackEvent', 'Gallery', 'Album selection click']);
        } else if (window.isMapview) {
            window._gaq.push(['_trackEvent', 'Map', 'Album selection click']);
        } else if (window.isGame) {
            window._gaq.push(['_trackEvent', 'Game', 'Album selection click']);
        }
    });
    $(document).on('click', '#ajapaik-photo-modal-share', function () {
        if (window.isFrontpage) {
            window._gaq.push(['_trackEvent', 'Gallery', 'Photo modal share click']);
        } else if (window.isMapview) {
            window._gaq.push(['_trackEvent', 'Map', 'Photo modal share click']);
        }
    });
    $(document).on('click', '#full_leaderboard', function (e) {
        e.preventDefault();
        var url = window.leaderboardFullURL;
        if (window.albumId) {
            url += 'album/' + window.albumId;
        }
        $.ajax({
            url: url,
            success: function (response) {
                var modalWindow = $('#ajapaik-full-leaderboard-modal');
                modalWindow.find('.scoreboard').html(response);
                modalWindow.find('.score_container').show();
                window.hideScoreboard();
                modalWindow.modal();
            }
        });
        window._gaq.push(['_trackEvent', '', 'Full leaderboard']);
    });
    $(document).on('click', '#ajapaik-info-window-leaderboard-link', function (e) {
        e.preventDefault();
        $('#full_leaderboard').click();
    });

    $(document).on('click', '#ajapaik-invert-rephoto-overlay-button', function (e) {
        e.preventDefault();
        var targetDiv = $('#ajapaik-modal-rephoto');
        if (targetDiv.hasClass('ajapaik-photo-bw')) {
            targetDiv.removeClass('ajapaik-photo-bw');
        } else {
            targetDiv.addClass('ajapaik-photo-bw');
        }
    });

    $(document).on('click', '#ajapaik-header-about-button', function (e) {
        var targetDiv = $('#ajapaik-general-info-modal');
        if (window.generalInfoModalURL) {
            $.ajax({
                url: window.generalInfoModalURL,
                success: function (resp) {
                    targetDiv.html(resp).modal();
                }
            });
        }
        if (window.isFrontpage) {
            window._gaq.push(['_trackEvent', 'Gallery', 'General info click']);
        } else if (window.isGame) {
            window._gaq.push(['_trackEvent', 'Game', 'General info click']);
        } else if (window.isMapview) {
            window._gaq.push(['_trackEvent', 'Mapview', 'General info click']);
        }
    });

    $(document).on('click', '#ajapaik-mobile-about-button', function (e) {
        var targetDiv = $('#ajapaik-general-info-modal');
        if (window.generalInfoModalURL) {
            $.ajax({
                url: window.generalInfoModalURL,
                success: function (resp) {
                    targetDiv.html(resp).modal();
                }
            });
        }
        if (window.isFrontpage) {
            window._gaq.push(['_trackEvent', 'Gallery', 'General info click']);
        } else if (window.isGame) {
            window._gaq.push(['_trackEvent', 'Game', 'General info click']);
        } else if (window.isMapview) {
            window._gaq.push(['_trackEvent', 'Mapview', 'General info click']);
        }
    });

    $(document).on('click', '#ajapaik-mobile-about-label', function () {
        $('#ajapaik-mobile-about-button').click();
    });

    $(document).on('click', '#ajapaik-header-album-name', function (e) {
        e.preventDefault();
        var targetDiv = $('#ajapaik-info-modal');
        if (window.albumId && window.infoModalURL) {
            $.ajax({
                url: window.infoModalURL + window.albumId,
                data: {
                    linkToMap: window.linkToMap,
                    linkToGame: window.linkToGame
                },
                success: function (resp) {
                    targetDiv.html(resp);
                    targetDiv.modal().on('shown.bs.modal', function () {
                        window.FB.XFBML.parse();
                    });
                }
            });
        }
        if (window.isFrontpage) {
            window._gaq.push(['_trackEvent', 'Gallery', 'Album info click']);
        } else if (window.isGame) {
            window._gaq.push(['_trackEvent', 'Game', 'Album info click']);
        } else if (window.isMapview) {
            window._gaq.push(['_trackEvent', 'Mapview', 'Album info click']);
        }
    });

    $(document).on('click', '.ajapaik-change-language-link', function (e) {
        e.preventDefault();
        $('#ajapaik-language').val($(this).attr('lang-code'));
        $('#ajapaik-change-language-form').submit();
    });

    $(document).on('click', '#ajapaik-filter-closest-link', function (e) {
        e.preventDefault();
        originalClosestLink = e.target.href;
        getGeolocation(window.handleGeolocation);
    });

    $(document).on('click', '.ajapaik-album-info-modal-album-link', function () {
        if (window.isFrontpage) {
            window._gaq.push(['_trackEvent', 'Gallery', 'Album info album link click']);
        } else if (window.isGame) {
            window._gaq.push(['_trackEvent', 'Game', 'Album info album link click']);
        } else if (window.isMapview) {
            window._gaq.push(['_trackEvent', 'Mapview', 'Album info album link click']);
        }
    });

    $(document).on('click', '.ajapaik-close-streetview-button', function () {
        map.getStreetView().setVisible(false);
    });

    $(document).on('click', '#ajapaik-mapview-close-streetview-button', function () {
        map.getStreetView().setVisible(false);
    });

    hideUnlockedAzimuth = function () {
        if (!saveDirection) {
            dottedAzimuthLine.setVisible(false);
        }
    };

    showUnlockedAzimuth = function () {
        if (!saveDirection) {
            dottedAzimuthLine.setVisible(true);
        }
    };

    $('#ajapaik-guess-panel-container').hover(hideUnlockedAzimuth, showUnlockedAzimuth);

    window.openTutorialPanel = function () {
        tutorialPanelSettings.content = $('#ajapaik-tutorial-js-panel-content').html();
        if (window.isMobile) {
            tutorialPanelSettings.resizable = false;
            tutorialPanelSettings.draggable = false;
        }
        tutorialPanel = $.jsPanel(tutorialPanelSettings);
    };

    $('body').on('jspanelclosed', function closeHandler(event, id) {
        if (id === 'ajapaik-tutorial-js-panel') {
            window.userClosedTutorial = true;
            tutorialPanel = undefined;
            window.docCookies.setItem('ajapaik_closed_tutorial', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
            $('body').off('jspanelclosed', closeHandler);
        }
    });
}(jQuery));