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
        disableSave = true,
        guessLocationStarted = false,
        currentPanelWidth,
        lastPanelWidth,
        recurringCheckPanelSize,
        i = 0,
        j = 0,
        maxIndex = 2,
        lastHighlightedMarker,
        lastSelectedPaneElement,
        markerIdsWithinBounds,
        lineLength = 0.01,
        lastSelectedMarkerId,
        currentlySelectedMarkerId,
        targetPaneElement,
        markerTemp,
        markers = [],
        mc,
        currentMapDataRequest,
        currentPaneDataRequest,
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
        photoDrawerOpen = false,
        openPhotoDrawer,
        toggleVisiblePaneElements,
        setCorrectMarkerIcon,
        blackMarkerIcon20 = '/static/images/ajapaik_marker_20px.png',
        blackMarkerIcon20Transparent = '/static/images/ajapaik_marker_20px_transparent.png',
        blackMarkerIcon35 = '/static/images/ajapaik_marker_35px.png',
        blueMarkerIcon20 = '/static/images/ajapaik_marker_20px_blue.png',
        blueMarkerIcon20Transparent = '/static/images/ajapaik_marker_20px_blue_transparent.png',
        blueMarkerIcon35 = '/static/images/ajapaik_marker_35px_blue.png',
        ffWheelListener,
        nonFFWheelListener,
        guessPhotoPanel,
        guessPhotoPanelContent,
        currentPhotoWidth,
        guessResponseReceived,
        noticeDiv,
        feedbackPanel,
        markerIdToHighlightAfterPageLoad;


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
        var fullScreenImage = $('#ajapaik-mapview-full-screen-image');
        fullScreenImage.unbind('load');
        photoDrawerOpen = true;
        window.syncMapStateToURL();
        $('#ajapaik-photo-modal').html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
            $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
            fullScreenImage.prop('src', window.photoModalFullscreenImageUrl).on('load', function () {
                //$('#ajapaik-full-screen-link').prop('rel', photos[currentPhotoIdx].id).prop('href', mediaUrl + photos[currentPhotoIdx].large.url);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1]);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1], '#ajapaik-mapview-full-screen-image');
            });
            $('#ajapaik-mapview-guess-photo-description').html(window.currentPhotoDescription);
        });
    };

    window.syncMapStateToURL = function () {
        var historyReplacementString = '/kaart/?city=' + window.cityId;
        if (window.map) {
            historyReplacementString += '&lat=' + window.map.getCenter().lat();
            historyReplacementString += '&lng=' + window.map.getCenter().lng();
            historyReplacementString += '&zoom=' + window.map.zoom;
        }
        if (currentlySelectedMarkerId) {
            historyReplacementString += '&selectedPhoto=' + currentlySelectedMarkerId;
        }
        if (photoDrawerOpen) {
            historyReplacementString += '&photoModalOpen=1';
        }
        if (window.currentlySelectedRephotoId) {
            historyReplacementString += '&selectedRephoto=' + window.currentlySelectedRephotoId;
        }
        window.History.replaceState(null, null, historyReplacementString);
    };

    window.startGuessLocation = function () {
        if (!guessLocationStarted) {
            guessLocationStarted = true;
            $('.ajapaik-marker-center-lock-button').show();
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
            });
            window.mapMarkerPositionChangedListener = window.google.maps.event.addListener(window.marker, 'position_changed', function () {
                disableSave = false;
            });
            $('#ajapaik-photo-modal').modal('toggle');
            guessPhotoPanelContent = $('#ajapaik-mapview-guess-photo-js-panel-content');
            guessPhotoPanelContent.find('img').prop('src', window.currentPhotoURL);
            if (!window.isMobile) {
                $('.ajapaik-flip-photo-overlay-button').hide();
                $('.ajapaik-fullscreen-overlay-button').hide();
            }
            currentPhotoWidth = $('#ajapaik-mapview-guess-photo-container').find('img').width();
            guessPhotoPanel = $('#ajapaik-map-container').jsPanel({
                content: guessPhotoPanelContent.html(),
                controls: {buttons: false},
                title: false,
                header: false,
                draggable: {
                    handle: '.panel-body',
                    containment: '#ajapaik-map-container'
                },
                size: {
                    width: function () {
                        return currentPhotoWidth;
                    },
                    height: 'auto'
                },
                id: 'ajapaik-mapview-guess-photo-js-panel'
            });
            $(guessPhotoPanel).css('max-width', currentPhotoWidth + 'px');
            photoPanel.close();
            $('#ajapaik-mapview-map-info-panel').show();
            $('#ajapaik-map-button-container').show();
            mc.clearMarkers();
            $.ajax({
                url: '/heatmap_data/',
                data: {photo_id: photoId},
                cache: false,
                success: function (response) {
                    window.mapDisplayHeatmapWithEstimatedLocation(response);
                }
            });
        }
    };

    // TODO: Incomplete
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
        guessResponseReceived = true;
        // TODO: What to do about rephoto and game leaderboard mixing up?
        //window.updateLeaderboard();
        noticeDiv = $('#ajapaik-mapview-feedback-js-panel-content');
        if (guessResponse.hideFeedback) {
            noticeDiv.find('#ajapaik-mapview-guess-feedback-difficulty-prompt').hide();
            noticeDiv.find('#ajapaik-mapview-guess-feedback-difficulty-form').hide();
            noticeDiv.find('#ajapaik-mapview-guess-feedback-points-gained').hide();
        }
        noticeDiv.find('#ajapaik-mapview-guess-feedback-message').html(guessResponse.feedbackMessage);
        noticeDiv.find('#ajapaik-mapview-guess-feedback-points-gained').text(window.gettext('Points awarded') + ': ' + guessResponse.currentScore);
        setTimeout(function () {
            feedbackPanel = $('#ajapaik-map-container').jsPanel({
                content: noticeDiv.html(),
                controls: {
                    buttons: false
                },
                title: false,
                header: false,
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
        window.marker.setMap(null);
        if (window.heatmap) {
            window.heatmap.setMap(null);
        }
        if (window.panoramaMarker) {
            window.panoramaMarker.setMap(null);
        }
        guessPhotoPanel.close();
        if (feedbackPanel) {
            feedbackPanel.close();
        }
        photoPanel.close();
        photoPanel = undefined;
        lastRequestedPaneMarkersIds = undefined;
        $('.ajapaik-marker-center-lock-button').hide();
        window.heatmapEstimatedLocationMarker.setMap(null);
        window.map.set('scrollwheel', true);
        window.realMapElement.removeEventListener(nonFFWheelListener);
        window.realMapElement.removeEventListener(ffWheelListener);
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
        guessLocationStarted = false;
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
        //$.modal.close();
        //if (photoId === undefined) {
        //    if (response && response.new_id !== undefined && response.new_id) {
        //        //window.location.href = '/foto/' + response.new_id + '/';
        //    } else {
        //        //window.location.reload();
        //    }
        //} else {
        //    //closePhotoDrawer();
        //    if (response && response.new_id !== undefined && response.new_id) {
        //        window.loadPhoto(response.new_id);
        //    } else {
        //        window.loadPhoto(photoId);
        //    }
        //}
    };

    toggleVisiblePaneElements = function () {
        if (window.map && !guessLocationStarted) {
            currentlySelectedMarkerId = false;
            window.dottedAzimuthLine.setVisible(false);
            if (window.cityId) {
                window.syncMapStateToURL();
            }
            currentMapBounds = window.map.getBounds();
            ne = currentMapBounds.getNorthEast();
            sw = currentMapBounds.getSouthWest();
            if (currentMapDataRequest) {
                currentMapDataRequest.abort();
            }
            currentMapDataRequest = $.post('/map_data/', { sw_lat: sw.lat(), sw_lon: sw.lng(), ne_lat: ne.lat(), ne_lon: ne.lng(), zoom: window.map.zoom, csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')}, function (response) {
                if (mc) {
                    mc.clearMarkers();
                }
                markers = [];
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
                mc = new MarkerClusterer(window.map, markers, {maxZoom: 15, minimumClusterSize: 5});
                // TODO: Make neat, no extra request
                var clusterMarkers = mc.getMarkers();
                if (window.map.zoom > 15) {
                    markerIdsWithinBounds = [];
                    for (i = 0; i < clusterMarkers.length; i += 1) {
                        markerIdsWithinBounds.push(clusterMarkers[i].id);
                    }
                    if (!lastRequestedPaneMarkersIds || lastRequestedPaneMarkersIds.sort().join(',') !== markerIdsWithinBounds.sort().join(',')) {
                        if (currentPaneDataRequest) {
                            currentPaneDataRequest.abort();
                        }
                        currentPaneDataRequest = $.post('/pane_contents/', { marker_ids: markerIdsWithinBounds, csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')}, function (response) {
                            if (photoPanel) {
                                photoPanel.content.html(response);
                                photoPanel.find('.panel-body').justifiedGallery(justifiedGallerySettings);
                            } else {
                                photoPanel = $('#ajapaik-map-container').jsPanel({
                                    content: response,
                                    controls: {buttons: false},
                                    title: false,
                                    position: {top: 35, left: 35},
                                    size: { height: function () {
                                        return $(window).height() / 1.5;
                                    }},
                                    draggable: {
                                        handle: '.jsPanel-header',
                                        containment: '#ajapaik-map-container'
                                    },
                                    overflow: { horizontal: 'hidden', vertical: 'auto' },
                                    id: 'ajapaik-mapview-photo-panel'
                                });
                                photoPanel.find('.panel-body').justifiedGallery(justifiedGallerySettings);
                            }
                            if (!recurringCheckPanelSize) {
                                recurringCheckPanelSize = setInterval(function () {
                                    currentPanelWidth = $('#ajapaik-mapview-photo-panel').width();
                                    if (photoPanel && currentPanelWidth !== lastPanelWidth) {
                                        photoPanel.find('.panel-body').justifiedGallery();
                                    }
                                    lastPanelWidth = currentPanelWidth;
                                }, 500);
                            }
                            if (markerIdToHighlightAfterPageLoad) {
                                window.highlightSelected(markerIdToHighlightAfterPageLoad);
                                markerIdToHighlightAfterPageLoad = false;
                            }
                            currentPaneDataRequest = undefined;
                            lastRequestedPaneMarkersIds = markerIdsWithinBounds;
                        });
                    }
                } else {
                    if (photoPanel) {
                        photoPanel.close();
                        photoPanel = undefined;
                    }
                }
            });
        }
    };

    window.highlightSelected = function (markerId, fromMarker) {
        if (currentlySelectedMarkerId == markerId && fromMarker) {
            window.loadPhoto(markerId);
        }
        currentlySelectedMarkerId = markerId;
        if (window.cityId) {
            window.syncMapStateToURL();
        }
        targetPaneElement = $('#element' + markerId);
        userAlreadySeenPhotoIds[markerId] = 1;
        if (fromMarker && targetPaneElement) {
            var targetPos = targetPaneElement.position(),
                targetTop;
            if (targetPos) {
                targetTop = targetPos.top;
                $('#ajapaik-mapview-photo-panel').find('.jsPanel-content').scrollTop(targetTop);
            }
            _gaq.push(['_trackEvent', 'Map', 'Marker click']);
        }
        if (!fromMarker) {
            _gaq.push(['_trackEvent', 'Map', 'Pane photo click']);
        }
        //if (currentlySelectedMarkerId == lastSelectedMarkerId) {
        //    return true;
        //}
        if (lastSelectedPaneElement) {
            lastSelectedPaneElement.find('.ajapaik-azimuth').hide();
            lastSelectedPaneElement.find('.ajapaik-eye-open').hide();
            lastSelectedPaneElement.find('.ajapaik-rephoto-count').hide();
        }
        if (lastSelectedMarkerId && lastHighlightedMarker) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        $.post('/log_user_map_action/', {user_action: 'saw_marker', photo_id: markerId, csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')}, function () {});
        lastSelectedMarkerId = markerId;
        lastSelectedPaneElement = targetPaneElement;
        markerTemp = undefined;
        if (mc) {
            var clusterMarkers = mc.getMarkers();
            for (i = 0; i < clusterMarkers.length; i += 1) {
                if (clusterMarkers[i].id == markerId) {
                    targetPaneElement.find('img').attr('src', clusterMarkers[i].thumb);
                    targetPaneElement.find('.ajapaik-azimuth').show();
                    targetPaneElement.find('.ajapaik-eye-open').show();
                    targetPaneElement.find('.ajapaik-rephoto-count').show();
                    if (!targetPaneElement.find('.ajapaik-eye-open').hasClass('ajapaik-eye-open-light-bg')) {
                        targetPaneElement.find('.ajapaik-eye-open').addClass('ajapaik-eye-open-light-bg');
                    }
                    clusterMarkers[i].setZIndex(maxIndex);
                    maxIndex += 1;
                    markerTemp = clusterMarkers[i];
                    if (clusterMarkers[i].azimuth) {
                        window.dottedAzimuthLine.setPath([clusterMarkers[i].position, Math.calculateMapLineEndPoint(clusterMarkers[i].azimuth, clusterMarkers[i].position, lineLength)]);
                        window.dottedAzimuthLine.setMap(window.map);
                        window.dottedAzimuthLine.setVisible(true);
                    } else {
                        window.dottedAzimuthLine.setVisible(false);
                    }
                    setCorrectMarkerIcon(clusterMarkers[i]);
                } else {
                    setCorrectMarkerIcon(clusterMarkers[i]);
                }
            }
        }
/*        for (i = 0; i < markers.length; i += 1) {
            if (markers[i].id == markerId) {
                targetPaneElement.find('img').attr('src', markers[i].thumb);
                targetPaneElement.find('.ajapaik-azimuth').show();
                targetPaneElement.find('.ajapaik-eye-open').show();
                targetPaneElement.find('.ajapaik-rephoto-count').show();
                if (!targetPaneElement.find('.ajapaik-eye-open').hasClass('ajapaik-eye-open-light-bg')) {
                    targetPaneElement.find('.ajapaik-eye-open').addClass('ajapaik-eye-open-light-bg');
                }
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
        }*/
        if (markerTemp) {
            lastHighlightedMarker = markerTemp;
            markerTemp = undefined;
        }
    };

    window.flipPhoto = function () {
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

    $(document).ready(function () {
        window.realMapElement = $('#ajapaik-map-canvas')[0];
        window.mapInfoPanelGeotagCountElement = $('#ajapaik-mapview-map-geotag-count');
        window.mapInfoPanelAzimuthCountElement = $('#ajapaik-mapview-map-geotag-with-azimuth-count');

        if (window.getQueryParameterByName('fromSelect') && window.cityId) {
            window.fromSelect = true;
            window.History.replaceState(null, null, '/kaart/?city=' + window.cityId);
        } else {
            window.fromSelect = false;
        }

        if (window.cityLatLng) {
            window.getMap(window.cityLatLng, 13, false);
        } else {
            window.getMap(null, 13, false);
        }

        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

        $(document).on('hidden.bs.modal', '#ajapaik-photo-modal', function () {
            photoDrawerOpen = false;
            window.syncMapStateToURL();
        });

        window.saveLocationButton = $('.ajapaik-save-location-button');

        window.saveLocationButton.on('click', function () {
            window.firstDragDone = false;
            window.setCursorToAuto();
            if (disableSave) {
                window._gaq.push(['_trackEvent', 'Mapview', 'Forgot to move marker']);
                window.alert(window.gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view.'));
            } else {
                // TODO: Flip data and stuff
                window.saveLocation(window.marker, photoId, null, true, null, window.degreeAngle, window.azimuthLineEndPoint, 'Map');
                if (window.saveDirection) {
                    window._gaq.push(['_trackEvent', 'Mapview', 'Save location and direction']);
                } else {
                    window._gaq.push(['_trackEvent', 'Mapview', 'Save location only']);
                }
            }
        });

        if (window.getQueryParameterByName('lat') && window.getQueryParameterByName('lng') && window.getQueryParameterByName('zoom') && !window.fromSelect) {
            window.map.setCenter(new window.google.maps.LatLng(window.getQueryParameterByName('lat'), window.getQueryParameterByName('lng')));
            window.map.setZoom(parseInt(window.getQueryParameterByName('zoom'), 10));
        }

        if (window.getQueryParameterByName('selectedPhoto') && !window.fromSelect) {
            currentlySelectedMarkerId = window.getQueryParameterByName('selectedPhoto');
            if (window.map.zoom > 15) {
                markerIdToHighlightAfterPageLoad = window.getQueryParameterByName('selectedPhoto');
            }
            if (window.getQueryParameterByName('photoModalOpen')) {
                window.loadPhoto(window.getQueryParameterByName('selectedPhoto'));
            }
            if (window.getQueryParameterByName('selectedRephoto')) {
                window.currentlySelectedRephotoId = window.getQueryParameterByName('selectedRephoto');
            }
        }

        if (window.map !== undefined) {
            window.mapMapviewIdleListener = window.google.maps.event.addListener(window.map, 'idle', toggleVisiblePaneElements);
        }

        $('#google-plus-login-button').click(function () {
            _gaq.push(['_trackEvent', 'Map', 'Google+ login']);
        });

        $('#logout-button').click(function () {
            _gaq.push(['_trackEvent', 'Map', 'Logout']);
        });

        $('.ajapaik-mapview-skip-photo-button').click(function () {
            window.stopGuessLocation();
        });

        //photoDrawerElement.delegate('ul.thumbs li.photo a', 'click', function (e) {
        //    e.preventDefault();
        //    var rephotoContentElement = $('#rephoto_content'),
        //        fullLargeElement = $('#full-large2'),
        //        that = $(this);
        //    $('ul.thumbs li.photo').removeClass('current');
        //    that.parent().addClass('current');
        //    rephotoContentElement.find('a').attr('href', rephotoImgHref[that.attr('rel')]);
        //    rephotoContentElement.find('a').attr('rel', that.attr('rel'));
        //    rephotoContentElement.find('img').attr('src', rephotoImgSrc[that.attr('rel')]);
        //    fullLargeElement.find('img').attr('src', rephotoImgSrcFs[that.attr('rel')]);
        //    $('#meta_content').html(rephotoMeta[that.attr('rel')]);
        //    $('#add-comment').html(rephotoComment[that.attr('rel')]);
        //    if (typeof FB !== 'undefined') {
        //        FB.XFBML.parse();
        //    }
        //    History.replaceState(null, window.document.title, that.attr('href'));
        //    _gaq.push(['_trackPageview', that.attr('href')]);
        //});

        //photoDrawerElement.delegate('a.add-rephoto', 'click', function (e) {
        //    e.preventDefault();
        //    $('#notice').modal();
        //    _gaq.push(['_trackEvent', 'Map', 'Add rephoto']);
        //});

        //$('.single .original').hoverIntent(function () {
        //    $('.original .tools').addClass('hovered');
        //}, function () {
        //    $('.original .tools').removeClass('hovered');
        //});
        //$('.single .rephoto .container').hoverIntent(function () {
        //    $('.rephoto .container .meta').addClass('hovered');
        //}, function () {
        //    $('.rephoto .container .meta ').removeClass('hovered');
        //});

        if (window.map !== undefined) {
            window.map.scrollwheel = true;
        }

        $('#full_leaderboard').bind('click', function (e) {
            e.preventDefault();
            $.ajax({
                url: leaderboardFullURL,
                success: function (response) {
                    var modalWindow = $('#ajapaik-full-leaderboard-modal');
                    modalWindow.find('.scoreboard').html(response);
                    modalWindow.modal().on('shown.bs.modal', function () {
                        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                    });
                }
            });
            _gaq.push(['_trackEvent', 'Map', 'Full leaderboard']);
        });

//        $(document).on('mouseover', '#ajapaik-photo-modal', function () {
//            if (!isMobile) {
//                $('.ajapaik-flip-photo-overlay-button').show();
//            }
//        });

//        $(document).on('mouseout', '#ajapaik-photo-modal', function () {
//            if (!isMobile) {
//                $('.ajapaik-flip-photo-overlay-button').hide();
//            }
//        });

        $(document).on('mouseover', '#ajapaik-mapview-guess-photo-container', function () {
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
                $('.ajapaik-fullscreen-overlay-button').show();
            }
        });

        $(document).on('mouseout', '#ajapaik-mapview-guess-photo-container', function () {
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').hide();
                $('.ajapaik-fullscreen-overlay-button').hide();
            }
        });

        $(document).on('click', '#ajapaik-mapview-guess-photo-js-panel .ajapaik-fullscreen-overlay-button', function () {
            if (window.BigScreen.enabled) {
                window.fullscreenEnabled = true;
                window.BigScreen.request($('#ajapaik-mapview-full-screen-image')[0]);
                window._gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'historic-' + this.rel]);
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
            //$('#ajapaik-mapview-photo-modal').modal();
            //$('#ajapaik-map-button-container').hide();
            //$('#ajapaik-game-guess-photo-js-panel').hide();
            //if (feedbackPanel) {
            //    feedbackPanel.close();
            //}
            //if (guessPhotoPanel) {
            //    guessPhotoPanel.close();
            //}
            //window.map.getStreetView().setVisible(false);
        });

        //TODO: There has to be a better way
        window.paneImageHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-eye-open').show();
            myParent.find('.ajapaik-azimuth').show();
            myParent.find('.ajapaik-rephoto-count').show();
        };
        window.paneImageHoverOut = function (e) {
            if (e.dataset.id != currentlySelectedMarkerId) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-eye-open').hide();
                myParent.find('.ajapaik-azimuth').hide();
                myParent.find('.ajapaik-rephoto-count').hide();
            }
        };
        window.paneEyeHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-eye-open').show();
            myParent.find('.ajapaik-azimuth').show();
            myParent.find('.ajapaik-rephoto-count').show();
            return false;
        };
        window.paneEyeHoverOut = function (e) {
            if (e.dataset.id != currentlySelectedMarkerId) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-eye-open').hide();
                myParent.find('.ajapaik-azimuth').hide();
                myParent.find('.ajapaik-rephoto-count').hide();
            }
            return false;
        };
        window.paneAzimuthHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-eye-open').show();
            myParent.find('.ajapaik-azimuth').show();
            myParent.find('.ajapaik-rephoto-count').show();
            return false;
        };
        window.paneAzimuthHoverOut = function (e) {
            if (e.dataset.id != currentlySelectedMarkerId) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-eye-open').hide();
                myParent.find('.ajapaik-azimuth').hide();
                myParent.find('.ajapaik-rephoto-count').hide();
            }
            return false;
        };
        window.paneRephotoCountHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-eye-open').show();
            myParent.find('.ajapaik-azimuth').show();
            myParent.find('.ajapaik-rephoto-count').show();
            return false;
        };
        window.paneRephotoCountHoverOut = function (e) {
            if (e.dataset.id != currentlySelectedMarkerId) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-eye-open').hide();
                myParent.find('.ajapaik-azimuth').hide();
                myParent.find('.ajapaik-rephoto-count').hide();
            }
            return false;
        };
    });
}(jQuery));