(function ($) {
    'use strict';

    var photoId,
        currentMapBounds,
        ne,
        sw,
        p,
        photoPanel,
        icon,
        lastRequestedPaneMarkersIds,
        i = 0,
        j = 0,
        maxIndex = 2,
        lastHighlightedMarker,
        lastSelectedPaneElement,
        markerIdsWithinBounds,
        refreshPane,
        lineLength = 0.01,
        lastSelectedMarkerId,
        currentlySelectedMarkerId,
        targetPaneElement,
        markerTemp,
        mc,
        currentMapDataRequest,
        currentPaneDataRequest,
        clusteringEndedListener,
        justifiedGallerySettings = {
            waitThumbnailsLoad: false,
            rowHeight: 120,
            margins: 3,
            sizeRangeSuffixes: {
                'lt100': '',
                'lt240': '',
                'lt320': '',
                'lt500': '',
                'lt640': '',
                'lt1024': ''
            }
        },
        openPhotoDrawer,
        photoDrawerOpen = false,
        toggleVisiblePaneElements,
        markerClustererSettings = {
            minimumClusterSize: 2,
            maxZoom: 17
        },
        setCorrectMarkerIcon,
        blackMarkerIcon20 = '/static/images/ajapaik_marker_20px.png',
        blackMarkerIcon20Transparent = '/static/images/ajapaik_marker_20px_transparent.png',
        blackMarkerIcon35 = '/static/images/ajapaik_marker_35px.png',
        blueMarkerIcon20 = '/static/images/ajapaik_marker_20px_blue.png',
        blueMarkerIcon20Transparent = '/static/images/ajapaik_marker_20px_blue_transparent.png',
        blueMarkerIcon35 = '/static/images/ajapaik_marker_35px_blue.png',
        ffWheelListener,
        markers = [],
        nonFFWheelListener,
        guessPhotoPanel,
        guessPhotoPanelContent,
        //currentPhotoWidth,
        noticeDiv,
        feedbackPanel,
        markerIdToHighlightAfterPageLoad,
        targetTopToScrollToAfterPaneLoad,
        updateBoundingEdge,
        maxGalleryWidth = $(window).width() * 0.2,
        maxGalleryHeight = $('#ajapaik-map-canvas').height(),
        galleryPanelSettings = {
            selector: '#ajapaik-map-container',
            title: false,
            position: 'top left',
            size: { height: function () {
                return maxGalleryHeight;
            }, width: function () {
                return maxGalleryWidth;
            }},
            draggable: false,
            removeHeader: true,
            overflow: { horizontal: 'hidden', vertical: 'auto' },
            id: 'ajapaik-mapview-photo-panel'
        },
        guessPhotoPanelSettings = {
            selector: '#ajapaik-map-container',
            controls: {buttons: false},
            title: false,
            removeHeader: true,
            draggable: {
                handle: '.jsPanel-content',
                containment: '#ajapaik-map-container'
            },
            size: 'auto',
            id: 'ajapaik-mapview-guess-photo-js-panel'
        };


    window.loadPhoto = function (id) {
        // TODO: No double request, this could get logged in /foto/ anyway
        //$.post('/log_user_map_action/', {user_action: 'opened_drawer', photo_id: id}, function () {
        //    $.noop();
        //});
        photoId = id;
        $.ajax({
            cache: false,
            url: '/foto/' + id + '/',
            success: function (result) {
                openPhotoDrawer(result);
                if (window.FB !== undefined) {
                    window.FB.XFBML.parse();
                }
            }
        });
    };

    openPhotoDrawer = function (content) {
        photoDrawerOpen = true;
        window.syncMapStateToURL();
        var fullScreenImage = $('#ajapaik-mapview-full-screen-image');
        $('#ajapaik-photo-modal').html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
            $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
            fullScreenImage.prop('src', window.photoModalFullscreenImageUrl);
            window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1]);
            window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1], '#ajapaik-mapview-full-screen-image');
            $('#ajapaik-mapview-guess-photo-description').html(window.currentPhotoDescription);
        });
    };

    updateBoundingEdge = function (edge) {
        var scale = Math.pow(2, window.map.getZoom()),
            projection = window.map.getProjection(),
            edgePixelCoordinates = projection.fromLatLngToPoint(edge),
            currentPaneWidth = $('#ajapaik-mapview-photo-panel').width();
        if (!currentPaneWidth) {
            currentPaneWidth = $(window).width() / 5;
        }
        edgePixelCoordinates.x = (edgePixelCoordinates.x * scale + currentPaneWidth + 50) / scale;
        return projection.fromPointToLatLng(edgePixelCoordinates);
    };

    window.syncMapStateToURL = function () {
        var historyReplacementString = '/map/';
        if (currentlySelectedMarkerId) {
            historyReplacementString += 'photo/' + currentlySelectedMarkerId + '/';
        }
        if (window.currentlySelectedRephotoId) {
            historyReplacementString += 'rephoto/' + window.currentlySelectedRephotoId + '/';
        }
        if (window.areaId) {
            historyReplacementString += '?area=' + window.areaId;
        }
        if (window.map) {
            historyReplacementString += '&lat=' + window.map.getCenter().lat();
            historyReplacementString += '&lng=' + window.map.getCenter().lng();
            historyReplacementString += '&zoom=' + window.map.zoom;
        }
        if (photoDrawerOpen || window.guessLocationStarted) {
            historyReplacementString += '&photoModalOpen=1';
        }
        window.History.replaceState(null, window.title, historyReplacementString);
    };

    window.startGuessLocation = function () {
        if (!window.guessLocationStarted) {
            if (window.map.zoom < 17) {
                window.map.setZoom(17);
            }
            window.userFlippedPhoto = false;
            window.guessLocationStarted = true;
            window.dottedAzimuthLine.setVisible(false);
            window.google.maps.event.trigger(window.map, 'resize');
            window.map.set('scrollwheel', false);
            nonFFWheelListener = window.realMapElement.addEventListener('mousewheel', window.wheelEventNonFF, false);
            ffWheelListener = window.realMapElement.addEventListener('DOMMouseScroll', window.wheelEventFF, false);
            window.marker = new window.google.maps.Marker({
                map: window.map,
                draggable: false,
                visible: false,
                icon: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg'
            });
            window.mapDragendListener = window.google.maps.event.addListener(window.map, 'dragend', window.mapDragendListenerFunction);
            window.windowResizeListener = window.google.maps.event.addDomListener(window, 'resize', window.windowResizeListenerFunction);
            $('<div/>').addClass('center-marker').appendTo(window.map.getDiv()).click(function () {
                var that = $(this);
                if (!that.data('win')) {
                    that.data('win').bindTo('position', window.map, 'center');
                }
                that.data('win').open(window.map);
            });
            if (window.map) {
                if (!window.mapClickListenerActive) {
                    window.mapClickListener = window.google.maps.event.addListener(window.map, 'click', window.mapClickListenerFunction);
                    window.mapClickListenerActive = true;
                }
                if (!window.mapIdleListenerActive) {
                    window.mapGameIdleListener = window.google.maps.event.addListener(window.map, 'idle', window.mapIdleListenerFunction);
                    window.mapIdleListenerActive = true;
                }
                if (!window.mapDragstartListenerActive) {
                    window.mapDragstartListener = window.google.maps.event.addListener(window.map, 'dragstart', window.mapDragstartListenerFunction);
                    window.mapDragstartListenerActive = true;
                }
                if (!window.mapMousemoveListenerActive) {
                    window.mapMousemoveListener = window.google.maps.event.addListener(window.map, 'mousemove', window.mapMousemoveListenerFunction);
                    window.mapMousemoveListenerActive = true;
                }
            }
            window.mapDragListener = window.google.maps.event.addListener(window.map, 'drag', function () {
                window.firstDragDone = true;
                if (window.guessLocationStarted) {
                    $('.ajapaik-marker-center-lock-button').show();
                }
            });
            window.mapMarkerPositionChangedListener = window.google.maps.event.addListener(window.marker, 'position_changed', function () {
                window.disableSave = false;
            });
            $('#ajapaik-photo-modal').modal('toggle');
            guessPhotoPanelContent = $('#ajapaik-mapview-guess-photo-js-panel-content');
            guessPhotoPanelContent.find('img').prop('src', window.currentPhotoURL);
            if (!window.isMobile) {
                $('.ajapaik-flip-photo-overlay-button').hide();
                $('.ajapaik-fullscreen-overlay-button').hide();
            }
            //currentPhotoWidth = $('#ajapaik-mapview-guess-photo-container').find('img').width();
            guessPhotoPanelSettings.content = guessPhotoPanelContent.html();
            if (window.isMobile) {
                guessPhotoPanelSettings.resizable = false;
                guessPhotoPanelSettings.draggable = false;
            }
            guessPhotoPanel = $.jsPanel(guessPhotoPanelSettings);
            guessPhotoPanel.on('jspanelloaded', function () {
                $('#ajapaik-mapview-guess-photo-js-panel').find('img').show();
            });
            //guessPhotoPanel.find('img').show();
            if (photoPanel) {
                photoPanel.close();
            }
            $('#ajapaik-mapview-map-info-panel').show();
            $('#ajapaik-map-button-container').show();
            if (mc) {
                mc.clearMarkers();
            }
            $.ajax({
                url: '/heatmap_data/',
                data: {photo_id: photoId},
                cache: false,
                success: function (response) {
                    var transformedResponse = {
                        currentScore: response.current_score,
                        heatmapPoints: response.heatmap_points,
                        newEstimatedLocation: response.estimated_location,
                        tagsWithAzimuth: response.azimuth_tags,
                        confidence: response.confidence
                    };
                    window.mapDisplayHeatmapWithEstimatedLocation(transformedResponse);
                }
            });
            if (!window.userClosedTutorial) {
                window.openTutorialPanel();
            }
            window._gaq.push(['_trackEvent', 'Map', 'Specify location']);
        }
    };

    window.handleGuessResponse = function (guessResponse) {
        window.centerMarker.hide();
        window.marker.setVisible(true);
        window.google.maps.event.removeListener(window.mapMousemoveListener);
        window.mapMousemoveListenerActive = false;
        window.google.maps.event.removeListener(window.mapClickListener);
        window.mapClickListenerActive = false;
        window.google.maps.event.removeListener(window.mapDragstartListener);
        window.mapDragstartListenerActive = false;
        window.google.maps.event.removeListener(window.mapGameIdleListener);
        window.mapIdleListenerActive = false;
        window.google.maps.event.removeListener(window.mapMarkerDragListener);
        window.google.maps.event.removeListener(window.mapMarkerDragendListener);
        window.google.maps.event.removeListener(window.mapDragendListener);
        window.google.maps.event.removeListener(window.windowResizeListener);
        window.guessResponseReceived = true;
        noticeDiv = $('#ajapaik-mapview-feedback-js-panel-content');
        noticeDiv.find('#ajapaik-mapview-guess-feedback-points-gained').text(window.gettext('Points awarded') + ': ' + guessResponse.currentScore);
        setTimeout(function () {
            feedbackPanel = $.jsPanel({
                selector: '#ajapaik-map-container',
                content: noticeDiv.html(),
                controls: {
                    buttons: false
                },
                title: false,
                header: false,
                removeHeader: true,
                size: {
                    width: function () {
                        return $(window).width() / 3;
                    },
                    height: 'auto'
                },
                draggable: false,
                resizable: false,
                id: 'ajapaik-mapview-feedback-panel'
            }).css('top', 'auto').css('left', 'auto');
        }, 0);
        if (guessResponse.heatmapPoints && guessResponse.newEstimatedLocation) {
            window.mapDisplayHeatmapWithEstimatedLocation(guessResponse);
        }
    };

    window.stopGuessLocation = function () {
        if (!window.markerLocked) {
            $('.ajapaik-marker-center-lock-button')[0].click();
        }
        window.marker.setMap(null);
        window.comingBackFromGuessLocation = true;
        if (window.heatmap) {
            window.heatmap.setMap(null);
        }
        if (window.heatmapEstimatedLocationMarker) {
            window.heatmapEstimatedLocationMarker.setMap(null);
        }
        if (window.panoramaMarker) {
            window.panoramaMarker.setMap(null);
        }
        guessPhotoPanel.close();
        if (feedbackPanel) {
            feedbackPanel.close();
        }
        if (photoPanel) {
            photoPanel.close();
            photoPanel = undefined;
        }
        lastRequestedPaneMarkersIds = undefined;
        window.map.set('scrollwheel', true);
        window.realMapElement.removeEventListener('mousewheel', nonFFWheelListener);
        window.realMapElement.removeEventListener('DOMMouseScroll', ffWheelListener);
        $('.center-marker').hide();
        window.google.maps.event.removeListener(window.mapMousemoveListener);
        window.mapMousemoveListenerActive = false;
        window.google.maps.event.removeListener(window.mapClickListener);
        window.mapClickListenerActive = false;
        window.google.maps.event.removeListener(window.mapDragstartListener);
        window.mapDragstartListenerActive = false;
        window.google.maps.event.removeListener(window.mapGameIdleListener);
        window.mapIdleListenerActive = false;
        window.google.maps.event.removeListener(window.mapMarkerDragListener);
        window.google.maps.event.removeListener(window.mapMarkerDragendListener);
        window.google.maps.event.removeListener(window.mapDragendListener);
        window.google.maps.event.removeListener(window.windowResizeListener);
        //$('#ajapaik-photo-modal').modal('toggle');
        $('#ajapaik-mapview-map-info-panel').hide();
        $('#ajapaik-map-button-container').hide();
        window.setCursorToAuto();
        window.dottedAzimuthLine.setMap(null);
        window.guessLocationStarted = false;
        toggleVisiblePaneElements();
    };

    window.closePhotoDrawer = function () {
        $('#ajapaik-photo-modal').modal('toggle');
        photoDrawerOpen = false;
        window.syncMapStateToURL();
        $('.filter-box').show();
    };

    window.uploadCompleted = function (response) {
        $('#ajapaik-rephoto-upload-modal').modal('toggle');
        if (response && response.new_id) {
            window.currentlySelectedRephotoId = response.new_id;
            window.syncMapStateToURL();
            window.location.reload();
        }
    };

    toggleVisiblePaneElements = function () {
        if (window.map && !window.guessLocationStarted) {
            window.dottedAzimuthLine.setVisible(false);
            if (!window.comingBackFromGuessLocation) {
                window.deselectMarker();
            } else {
                markerIdToHighlightAfterPageLoad = currentlySelectedMarkerId;
                window.comingBackFromGuessLocation = false;
            }
            if (window.urlParamsInitialized) {
                currentlySelectedMarkerId = false;
            }
            window.syncMapStateToURL();
            currentMapBounds = window.map.getBounds();
            ne = currentMapBounds.getNorthEast();
            sw = currentMapBounds.getSouthWest();
            if (currentMapDataRequest) {
                currentMapDataRequest.abort();
            }
            $('.ajapaik-marker-center-lock-button').hide();
            sw = updateBoundingEdge(sw);
            currentMapDataRequest = $.post('/map_data/', { sw_lat: sw.lat(), sw_lon: sw.lng(), ne_lat: ne.lat(), ne_lon: ne.lng(), zoom: window.map.zoom, csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')}, function (response) {
                if (mc) {
                    mc.clearMarkers();
                }
                markers.length = 0;
                for (j = 0; j < response.length; j += 1) {
                    p = response[j];
                    if (p[4]) {
                        icon = blueMarkerIcon20;
                    } else {
                        icon = blackMarkerIcon20;
                    }
                    var marker = new google.maps.Marker({
                        id: p[0],
                        icon: icon,
                        rephotoCount: p[4],
                        position: new google.maps.LatLng(p[3], p[2]),
                        zIndex: 1,
                        azimuth: p[7],
                        map: null
                    });
                    (function (id) {
                        window.google.maps.event.addListener(marker, 'click', function () {
                            window.highlightSelected(id, true);
                        });
                    })(p[0]);
                    markers.push(marker);
                }
                if (window.map.zoom > 17) {
                    markerClustererSettings.gridSize = 1;
                } else {
                    markerClustererSettings.gridSize = 60;
                }
                if (mc && mc.clusters_) {
                    mc.clusters_.length = 0;
                }
                mc = new MarkerClusterer(window.map, markers, markerClustererSettings);
                markerIdsWithinBounds = [];
                clusteringEndedListener = window.google.maps.event.addListener(mc, 'clusteringend', function () {
                    var clusters = mc.clusters_,
                        currentMarkers;
                    for (var i = 0; i < clusters.length; i += 1) {
                        currentMarkers = clusters[i].markers_;
                        if (currentMarkers.length === 1) {
                            for (var j = 0; j < currentMarkers.length; j += 1) {
                                markerIdsWithinBounds.push(currentMarkers[j].id);
                            }
                        }
                    }
                    refreshPane(markerIdsWithinBounds);
                });
            });
        }
    };

    refreshPane = function (markerIdsWithinBounds) {
        if (!lastRequestedPaneMarkersIds || lastRequestedPaneMarkersIds.length === 0 || lastRequestedPaneMarkersIds.sort().join(',') !== markerIdsWithinBounds.sort().join(',')) {
            if (currentPaneDataRequest) {
                currentPaneDataRequest.abort();
            }
            currentPaneDataRequest = $.post('/pane_contents/', { marker_ids: markerIdsWithinBounds, csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')}, function (response) {
                if (photoPanel) {
                    photoPanel.content.html(response);
                    photoPanel.find('#ajapaik-photo-pane-content-container').justifiedGallery(justifiedGallerySettings);
                } else {
                    galleryPanelSettings.content = response;
                    if (window.isMobile) {
                        // TODO: Fix resizable and draggable for mobile, without breaking the overlay buttons, mind you!
                        galleryPanelSettings.resizable = false;
                    }
                    photoPanel = $.jsPanel(galleryPanelSettings);
                    photoPanel.find('#ajapaik-photo-pane-content-container').justifiedGallery(justifiedGallerySettings);
                }
                if (markerIdToHighlightAfterPageLoad) {
                    window.highlightSelected(markerIdToHighlightAfterPageLoad, true);
                    markerIdToHighlightAfterPageLoad = false;
                }
                currentPaneDataRequest = undefined;
                lastRequestedPaneMarkersIds = markerIdsWithinBounds;
            });
        }
    };

    window.deselectMarker = function () {
        currentlySelectedMarkerId = undefined;
        window.currentlySelectedRephotoId = undefined;
        window.syncMapStateToURL();
        $('.ajapaik-mapview-pane-photo-container').find('img').removeClass('translucent-pane-element');
        if (lastHighlightedMarker) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        window.dottedAzimuthLine.setVisible(false);
    };

    window.highlightSelected = function (markerId, fromMarker, event) {
        if (event) {
            event.stopPropagation();
        }
        if (currentlySelectedMarkerId == markerId) {
            window.loadPhoto(markerId);
        }
        currentlySelectedMarkerId = markerId;
        window.syncMapStateToURL();
        targetPaneElement = $('#element' + markerId);
        $('.ajapaik-mapview-pane-photo-container').find('img').addClass('translucent-pane-element');
        targetPaneElement.find('img').removeClass('translucent-pane-element');
        if (!fromMarker) {
            window._gaq.push(['_trackEvent', 'Map', 'Pane photo click']);
        }
        if (lastSelectedPaneElement) {
            lastSelectedPaneElement.find('.ajapaik-azimuth').hide();
        }
        if (lastSelectedMarkerId && lastHighlightedMarker) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        // TODO: Restore?
        //$.post('/log_user_map_action/', {user_action: 'saw_marker', photo_id: markerId, csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')}, function () {});
        lastSelectedMarkerId = markerId;
        lastSelectedPaneElement = targetPaneElement;
        markerTemp = undefined;
        for (i = 0; i < markers.length; i += 1) {
            if (markers[i].id == markerId) {
                targetPaneElement.find('img').attr('src', markers[i].thumb);
                targetPaneElement.find('.ajapaik-azimuth').show();
                markers[i].setZIndex(maxIndex);
                maxIndex += 1;
                markerTemp = markers[i];
                if (markers[i].azimuth) {
                    window.dottedAzimuthLine.setPath([markers[i].position, Math.calculateMapLineEndPoint(markers[i].azimuth, markers[i].position, lineLength)]);
                    window.dottedAzimuthLine.setMap(window.map);
                    window.dottedAzimuthLine.setVisible(true);
                } else {
                    window.dottedAzimuthLine.setVisible(false);
                }
                setCorrectMarkerIcon(markers[i]);
            } else {
                setCorrectMarkerIcon(markers[i]);
            }
        }
        if (markerTemp) {
            lastHighlightedMarker = markerTemp;
            markerTemp = undefined;
        }
        var targetPos,
        targetTop;
        if (fromMarker && targetPaneElement) {
            targetPos = targetPaneElement.position();
            if (targetPos) {
                targetTop = targetPos.top;
                targetTopToScrollToAfterPaneLoad = targetTop;
                $('#ajapaik-mapview-photo-panel').find('.jsPanel-content').animate({scrollTop: targetTop}, 800);
            }
            window._gaq.push(['_trackEvent', 'Map', 'Marker click']);
        }
    };

    window.flipPhoto = function () {
        window.photoModalCurrentPhotoFlipStatus = !window.photoModalCurrentPhotoFlipStatus;
        window.userFlippedPhoto = true;
        var fullScreenPhoto = $('#ajapaik-mapview-full-screen-image');
        if (fullScreenPhoto.hasClass('ajapaik-photo-flipped')) {
            fullScreenPhoto.removeClass('ajapaik-photo-flipped');
        } else {
            fullScreenPhoto.addClass('ajapaik-photo-flipped');
        }
    };

    setCorrectMarkerIcon = function (marker) {
        if (marker) {
            if (marker.rephotoCount) {
                if (marker.id == currentlySelectedMarkerId) {
                    marker.setIcon(blueMarkerIcon35);
                } else {
                    marker.setIcon(blueMarkerIcon20Transparent);
                }
            } else {
                if (marker.id == currentlySelectedMarkerId) {
                    marker.setIcon(blackMarkerIcon35);
                } else {
                    marker.setIcon(blackMarkerIcon20Transparent);
                }
            }
        }
    };

    window.initializeMapStateFromOptionalURLParameters = function () {
        if (window.getQueryParameterByName('fromSelect') && window.areaLatLng) {
            window.getMap(window.areaLatLng, 13, false);
        } else {
            if (window.preselectPhotoId) {
                // There's a selected photo specified in the URL, select when ready
                currentlySelectedMarkerId = window.preselectPhotoId;
                markerIdToHighlightAfterPageLoad = window.preselectPhotoId;
            }
            if (window.getQueryParameterByName('lat') && window.getQueryParameterByName('lng') && window.getQueryParameterByName('zoom')) {
                // User has very specific parameters, allow to take precedence
                window.getMap(new window.google.maps.LatLng(window.getQueryParameterByName('lat'), window.getQueryParameterByName('lng')), parseInt(window.getQueryParameterByName('zoom'), false));
            } else {
                if (window.preselectPhotoLat && window.preselectPhotoLng) {
                    // We know the location of the photo, let's build the map accordingly
                    window.getMap(new window.google.maps.LatLng(window.preselectPhotoLat, window.preselectPhotoLng), 18, false);
                } else if (window.areaLatLng) {
                    // There's nothing preselected, but we do know the album the photo's in
                    window.getMap(window.areaLatLng, 13, false);
                } else {
                    // No idea
                    window.getMap(null, 13, false);
                }
            }
            if (window.preselectRephotoId) {
                window.loadPhoto(window.preselectPhotoId);
                window.currentlySelectedRephotoId = window.preselectRephotoId;
                photoDrawerOpen = true;
            } else if (window.getQueryParameterByName('photoModalOpen') && window.preselectPhotoId) {
                window.userClosedRephotoTools = true;
                window.loadPhoto(window.preselectPhotoId);
                photoDrawerOpen = true;
            }
        }
        window.preselectPhotoId = false;
        window.preselectRephotoId = false;
        window.syncMapStateToURL();
        window.urlParamsInitialized = true;
    };

    $(document).ready(function () {
        window.realMapElement = $('#ajapaik-map-canvas')[0];
        window.mapInfoPanelGeotagCountElement = $('#ajapaik-mapview-map-geotag-count');
        window.mapInfoPanelAzimuthCountElement = $('#ajapaik-mapview-map-geotag-with-azimuth-count');
        //window.mapInfoPanelConfidenceElement = $('#ajapaik-mapview-map-confidence');
        window.saveLocationButton = $('.ajapaik-save-location-button');

        window.updateLeaderboard();

        $('#ajapaik-game-description-viewing-warning').hide();

        if (window.preselectPhotoId) {
            currentlySelectedMarkerId = window.preselectPhotoId;
        }

        if (window.docCookies.getItem('ajapaik_closed_tutorial')) {
            window.userClosedTutorial = true;
        }

        window.initializeMapStateFromOptionalURLParameters();

        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

        $(document).on('hidden.bs.modal', '#ajapaik-photo-modal', function () {
            window.currentlySelectedRephotoId = false;
            photoDrawerOpen = false;
            window.syncMapStateToURL();
        });

        window.saveLocationButton.on('click', function () {
            window.firstDragDone = false;
            $('.ajapaik-marker-center-lock-button').hide();
            window.setCursorToAuto();
            if (window.disableSave) {
                window._gaq.push(['_trackEvent', 'Mapview', 'Forgot to move marker']);
                window.alert(window.gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view. You should also zoom the map before submitting your geotag.'));
            } else {
                // TODO: Flip data and stuff
                window.saveLocation(window.marker, photoId, window.photoModalCurrentPhotoFlipStatus, true, window.userFlippedPhoto, window.degreeAngle, window.azimuthLineEndPoint, 'Map');
                if (window.saveDirection) {
                    window._gaq.push(['_trackEvent', 'Mapview', 'Save location and direction']);
                } else {
                    window._gaq.push(['_trackEvent', 'Mapview', 'Save location only']);
                }
            }
        });

        if (window.map !== undefined) {
            window.mapMapviewIdleListener = window.google.maps.event.addListener(window.map, 'idle', toggleVisiblePaneElements);
            window.mapMapviewClickListener = window.google.maps.event.addListener(window.map, 'click', function() {
                window.deselectMarker();
            });
        }

        $('#logout-button').click(function () {
            window._gaq.push(['_trackEvent', 'Map', 'Logout']);
        });

        $('.ajapaik-game-next-photo-button').click(function () {
            window.stopGuessLocation();
            window._gaq.push(['_trackEvent', 'Map', 'Next photo']);
        });

        if (window.map !== undefined) {
            window.map.scrollwheel = true;
        }

        $('#full_leaderboard').bind('click', function (e) {
            e.preventDefault();
            $.ajax({
                url: window.leaderboardFullURL,
                success: function (response) {
                    var modalWindow = $('#ajapaik-full-leaderboard-modal');
                    modalWindow.find('.scoreboard').html(response);
                    modalWindow.modal().on('shown.bs.modal', function () {
                        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                    });
                }
            });
            window._gaq.push(['_trackEvent', 'Map', 'Full leaderboard']);
        });

        $(document).on('mouseover', '#ajapaik-mapview-guess-photo-container', function () {
            if (!window.isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
                $('.ajapaik-fullscreen-overlay-button').show();
            }
        });

        $(document).on('mouseout', '#ajapaik-mapview-guess-photo-container', function () {
            if (!window.isMobile) {
                $('.ajapaik-flip-photo-overlay-button').hide();
                $('.ajapaik-fullscreen-overlay-button').hide();
            }
        });

        $(document).on('click', '#ajapaik-mapview-guess-photo-js-panel .ajapaik-fullscreen-overlay-button', function () {
            if (window.BigScreen.enabled) {
                window.fullscreenEnabled = true;
                window.BigScreen.request($('#ajapaik-mapview-full-screen-image')[0]);
                window._gaq.push(['_trackEvent', 'Map', 'Full-screen']);
            }
        });

        $(document).on('click', '#ajapaik-mapview-guess-photo-js-panel .ajapaik-flip-photo-overlay-button', function () {
            var button = $(this),
                photo = $('#ajapaik-mapview-guess-photo-container').find('img');
            if (button.hasClass('active')) {
                button.removeClass('active');
            } else {
                button.addClass('active');
            }
            if (photo.hasClass('ajapaik-photo-flipped')) {
                photo.removeClass('ajapaik-photo-flipped');
            } else {
                photo.addClass('ajapaik-photo-flipped');
            }
            window.flipPhoto();
        });

        $(document).on('click', '.ajapaik-mapview-feedback-next-button', function () {
            var data = {
                level: $('input[name=difficulty]:checked', 'ajapaik-mapview-guess-feedback-difficulty-form').val(),
                photo_id: photoId,
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            };
            $.post(window.difficultyFeedbackURL, data, function () {
                $.noop();
            });
            window.stopGuessLocation();
        });

        //TODO: There has to be a better way
        window.paneImageHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-azimuth').show();
        };
        window.paneImageHoverOut = function (e) {
            if (e.dataset.id != currentlySelectedMarkerId) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-azimuth').hide();
            }
        };
        window.paneEyeHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-azimuth').show();
            return false;
        };
        window.paneEyeHoverOut = function (e) {
            if (e.dataset.id != currentlySelectedMarkerId) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-azimuth').hide();
            }
            return false;
        };
        window.paneAzimuthHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-azimuth').show();
            return false;
        };
        window.paneAzimuthHoverOut = function (e) {
            if (e.dataset.id != currentlySelectedMarkerId) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-azimuth').hide();
            }
            return false;
        };
        window.paneRephotoCountHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-azimuth').show();
            return false;
        };
        window.paneRephotoCountHoverOut = function (e) {
            if (e.dataset.id != currentlySelectedMarkerId) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-azimuth').hide();
            }
            return false;
        };
    });
}(jQuery));