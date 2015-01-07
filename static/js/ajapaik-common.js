var map,
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
    mapClickListener,
    mapDragstartListener,
    mapGameIdleListener,
    mapMapviewIdleListener,
    mapBoundsChangedListener,
    mapMousemoveListener,
    mapDragListener,
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
    photoModalFullscreenImageUrl,
    photoModalFullscreenImageSize,
    photoModalRephotoArray,
    userClosedRephotoTools = false,
    heatmap,
    heatmapEstimatedLocationMarker;

(function ($) {
    'use strict';

    if ($(window).height() >= 320) {
        $(window).resize(adjustModalMaxHeightAndPosition).trigger('resize');
    }

    getMap = function (startPoint, startingZoom, isGameMap) {
        var latLng,
            zoomLevel;

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

        mapOpts = {
            zoom: zoomLevel,
            scrollwheel: false,
            center: latLng,
            mapTypeControl: true,
            panControl: true,
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
            streetView: streetPanorama
        };

        map = new window.google.maps.Map(document.getElementById('ajapaik-map-canvas'), mapOpts);

        lockButton = document.createElement('button');
        $(lockButton).addClass('btn').addClass('btn-default').addClass('ajapaik-marker-center-lock-button').css('display', 'none');

        map.controls[window.google.maps.ControlPosition.RIGHT_TOP].push(lockButton);

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
                    _gaq.push(['_trackEvent', 'Game', 'Opened Street View']);
                } else {
                    _gaq.push(['_trackEvent', 'Map', 'Opened Street View']);
                }
                // Currently we are not displaying the save button when Street View is open
                saveLocationButton.hide();
            }
        });

        streetviewPanoChangedListener = window.google.maps.event.addListener(streetPanorama, 'pano_changed', function () {
            if (isGameMap) {
                _gaq.push(['_trackEvent', 'Game', 'Street View Movement']);
            } else {
                _gaq.push(['_trackEvent', 'Map', 'Street View Movement']);
            }
        });

        streetviewCloseclickListener = window.google.maps.event.addListener(streetPanorama, 'closeclick', function () {
            // Closing Street View from the X button must also show the save button again
            saveLocationButton.show();
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
        scoreContainer.find('#google-plus-connect').slideDown();
    };

    hideScoreboard = function () {
        var scoreContainer = $('#ajapaik-header').find('.score_container');
        scoreContainer.find('.scoreboard li').not('.you').add('h2').slideUp();
        scoreContainer.find('#facebook-connect').slideUp();
        scoreContainer.find('#google-plus-connect').slideUp();
    };

    updateLeaderboard = function () {
        $('.score_container').find('.scoreboard').load(leaderboardUpdateURL);
    };

    saveLocationCallback = function (resp) {
        var message = '',
            hideFeedback = false,
            heatmapPoints,
            currentScore,
            tagsWithAzimuth,
            newEstimatedLocation;
        if (resp.is_correct == true) {
            message = gettext('Looks right!');
            hideFeedback = false;
            _gaq.push(['_trackEvent', 'Game', 'Correct coordinates']);
            if (resp.azimuth_false) {
                message = gettext('The location seems right, but not the azimuth.');
            }
            if (resp.azimuth_uncertain) {
                message = gettext('The location seems right, but the azimuth is yet uncertain.');
            }
            if (resp['azimuth_uncertain'] && resp['azimuth_tags'] < 2) {
                message = gettext('The location seems right, your azimuth was first.');
            }
        } else if (resp['location_is_unclear']) {
            message = gettext('Correct location is not certain yet.');
            _gaq.push(['_trackEvent', 'Game', 'Coordinates uncertain']);
        } else if (resp['is_correct'] == false) {
            message = gettext('Other users have different opinion.');
            hideFeedback = true;
            _gaq.push(['_trackEvent', 'Game', 'Wrong coordinates']);
        } else {
            message = gettext('Your guess was first.');
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
        if (resp.new_estimated_location) {
            newEstimatedLocation = resp.new_estimated_location;
        }
        window.handleGuessResponse({feedbackMessage: message, hideFeedback: hideFeedback,
            heatmapPoints: heatmapPoints, currentScore: currentScore, tagsWithAzimuth: tagsWithAzimuth,
            newEstimatedLocation: newEstimatedLocation});
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
        if (degreeAngle) {
            data.azimuth = degreeAngle;
        }
        if (azimuthLineEndPoint) {
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
        var uri = new URI(location.href),
            newQ = {city: $(this).val()},
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

        location.href = uri.toString();
    });

    // Firefox and Opera cannot handle modal taking over focus
    $.fn.modal.Constructor.prototype.enforceFocus = function () {
        $.noop();
    };

    // Our own custom zooming functions to fix the otherwise laggy zooming for mobile
    wheelEventFF = function (e) {
        console.log("wheel event FF");
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
        console.log("wheel event non FF");
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
        console.log("resize");
        if (markerLocked) {
            mapMousemoveListener = window.google.maps.event.addListener(map, 'mousemove', mapMousemoveListenerFunction);
            mapMousemoveListenerActive = true;
            dottedAzimuthLine.setVisible(false);
            if (panoramaMarker) {
                panoramaMarker.setVisible(false);
            }
        }
    };

    mapMousemoveListenerFunction = function (e) {
        console.log("mousemove");
        // The mouse is moving, therefore we haven't locked on a direction
        saveLocationButton.removeAttr('disabled');
        saveLocationButton.removeClass('btn-default');
        saveLocationButton.addClass('btn-warning');
        saveLocationButton.text(window.gettext('Save location only'));
        saveDirection = false;
        if (e) {
            radianAngle = Math.getAzimuthBetweenMouseAndMarker(e, marker);
            degreeAngle = Math.degrees(radianAngle);
        }
        if (panoramaMarker) {
            panoramaMarker.setMap(null);
        }
        setCursorToPanorama();
        if (!window.isMobile) {
            dottedAzimuthLine.setPath([marker.position, Math.calculateMapLineEndPoint(degreeAngle, marker.position, 0.05)]);
            dottedAzimuthLine.setMap(map);
            dottedAzimuthLine.icons = [
                {icon: dottedAzimuthLineSymbol, offset: '0', repeat: '7px'}
            ];
            dottedAzimuthLine.setVisible(true);
        } else {
            dottedAzimuthLine.setVisible(false);
        }
    };

    mapClickListenerFunction = function (e) {
        console.log("click");
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
            saveLocationButton.removeAttr('disabled');
            saveLocationButton.removeClass('btn-default');
            saveLocationButton.removeClass('btn-warning');
            saveLocationButton.addClass('btn-success');
            saveLocationButton.text(window.gettext('Save location and direction'));
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
            // TODO: What was this about? : )
            mapBoundsChangedListener = window.google.maps.event.addListener(map, 'bounds_changed', function () {

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
        console.log("idle");
        if (firstDragDone) {
            if (markerLocked) {
                console.log("set center");
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
        console.log("dragstart");
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
            saveLocationButton.removeAttr('disabled');
            saveLocationButton.removeClass('btn-default');
            saveLocationButton.addClass('btn-warning');
            saveLocationButton.text(window.gettext('Save location only'));
            azimuthListenerActive = false;
            dottedAzimuthLine.setVisible(false);
            mapMousemoveListenerActive = false;
            window.google.maps.event.clearListeners(map, 'mousemove');
        }
    };

    mapDragendListenerFunction = function () {
        console.log("dragend");
        if (markerLocked) {
            marker.setPosition(map.getCenter());
        }
    };

    mapMarkerDragListenerFunction = function () {
        console.log("marker drag");
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
        console.log("marker dragend");
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
        var totalHeatmapGeotags = 0,
            totalHeatmapGeotagsWithAzimuth = 0,
            latLngBounds = new window.google.maps.LatLngBounds(),
            newLatLng,
            heatmapPoints = [],
            inputHeatmapPoints,
            inputEstimatedLocation,
            i;
        if (heatmapData.heatmap_points) {
            inputHeatmapPoints = heatmapData.heatmap_points;
        } else {
            inputHeatmapPoints = heatmapData.heatmapPoints;
        }
        for (i = 0; i < inputHeatmapPoints.length; i += 1) {
            if (inputHeatmapPoints[i][2]) {
                totalHeatmapGeotagsWithAzimuth += 1;
            }
            totalHeatmapGeotags += 1;
            newLatLng = new window.google.maps.LatLng(inputHeatmapPoints[i][0], inputHeatmapPoints[i][1]);
            heatmapPoints.push(newLatLng);
            latLngBounds.extend(newLatLng);
        }
        if (heatmapData.tagsWithAzimuth) {
            totalHeatmapGeotagsWithAzimuth = heatmapData.tagsWithAzimuth;
        }
        window.mapInfoPanelGeotagCountElement.html(totalHeatmapGeotags);
        window.mapInfoPanelAzimuthCountElement.html(totalHeatmapGeotagsWithAzimuth);
        heatmapPoints = new window.google.maps.MVCArray(heatmapPoints);
        if (heatmap) {
            heatmap.setMap(null);
        }
        heatmap = new window.google.maps.visualization.HeatmapLayer({
            data: heatmapPoints
        });
        heatmap.setMap(window.map);
        heatmap.setOptions({radius: 50, dissipating: true});
        if (heatmapData.estimated_location) {
            inputEstimatedLocation = heatmapData.estimated_location;
        } else {
            inputEstimatedLocation = heatmapData.estimatedLocation;
        }
        if (inputEstimatedLocation) {
            heatmapEstimatedLocationMarker = new window.google.maps.Marker({
                position: new window.google.maps.LatLng(inputEstimatedLocation[0], inputEstimatedLocation[1]),
                map: window.map,
                title: window.gettext("The peoples' guess"),
                draggable: false,
                icon: '/static/images/ajapaik_marker_35px.png'
            });
        }
        if (heatmapEstimatedLocationMarker) {
            window.map.setCenter(heatmapEstimatedLocationMarker.getPosition());
            //window.marker.setPosition(heatmapEstimatedLocationMarker.getPosition());
            //window.map.setZoom(17);
        } else {
            window.map.fitBounds(latLngBounds);
        }
        marker.setPosition(map.getCenter());
    };

    $(document).on('click', '.ajapaik-marker-center-lock-button', function () {
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
            window.google.maps.event.clearListeners(window.marker, 'drag');
            window.google.maps.event.clearListeners(window.marker, 'dragend');
            window.azimuthListenerActive = false;
            window.map.setCenter(window.marker.position);
            window.setCursorToPanorama();
            window.markerLocked = true;
        } else {
            t.addClass('active');
            window.centerMarker.hide();
            window.marker.setVisible(true);
            window.marker.set('draggable', true);
            window.map.set('scrollwheel', true);
            window.realMapElement.removeEventListener('mousewheel', window.wheelEventNonFF, true);
            window.realMapElement.removeEventListener('DOMMouseScroll', window.wheelEventFF, true);
            mapMarkerDragListener = window.google.maps.event.addListener(window.marker, 'drag', window.mapMarkerDragListenerFunction);
            mapMarkerDragendListener = window.google.maps.event.addListener(window.marker, 'dragend', window.mapMarkerDragendListenerFunction);
            window.setCursorToAuto();
            window.markerLocked = false;
        }
    });
}(jQuery));