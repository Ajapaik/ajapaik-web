(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*global docCookies*/
    var photoId,
        currentMapBounds,
        limitByAlbum,
        ne,
        sw,
        p,
        photoPanel,
        i = 0,
        j = 0,
        l = 0,
        maxIndex = 2,
        lastHighlightedMarker,
        lastSelectedPaneElement,
        markerIdsWithinBounds,
        refreshPane,
        lastSelectedMarkerId,
        currentlySelectedMarkerId,
        targetPaneElement,
        markerTemp,
        mc,
        currentMapDataRequest,
        currentPaneDataRequest,
        clusteringEndedListener,
        lastRequestedPaneMarkersIds,
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
        guessPanelContainer,
        photoDrawerOpen = false,
        markerClustererSettings = {
            minimumClusterSize: 2,
            maxZoom: 17
        },
        setCorrectMarkerIcon,
        currentIcon,
        arrowIcon = {
            path: 'M12 2l-7.5 18.29.71.71 6.79-3 6.79 3 .71-.71z',
            strokeColor: 'white',
            strokeOpacity: 1,
            strokeWeight: 1,
            fillColor: 'black',
            fillOpacity: 1,
            rotation: 0,
            scale: 1.0,
            anchor: new window.google.maps.Point(12, 12)
        },
        locationIcon = {
            path: 'M12 2c-3.87 0-7 3.13-7 7 0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
            strokeColor: 'white',
            strokeOpacity: 1,
            strokeWeight: 1,
            fillColor: 'black',
            fillOpacity: 1,
            scale: 1.0,
            anchor: new window.google.maps.Point(12, 0)
        },
        markers = [],
        markerIdToHighlightAfterPageLoad,
        targetTopToScrollToAfterPaneLoad,
        updateBoundingEdge,
        maxGalleryWidth = $(window).width() * 0.2,
        maxGalleryHeight = $('#ajapaik-map-canvas').height(),
        galleryPanelSettings = {
            selector: '#ajapaik-map-container',
            title: false,
            position: 'top left',
            size: {
                height: function () {
                    return maxGalleryHeight;
                }, width: function () {
                    return maxGalleryWidth;
                }
            },
            draggable: false,
            removeHeader: true,
            overflow: {horizontal: 'hidden', vertical: 'auto'},
            id: 'ajapaik-mapview-photo-panel'
        },
        centerOnMapAfterLocating = false,
        activateAlbumFilter,
        deactivateAlbumFilter;
    window.loadPhoto = function (id) {
        photoId = id;
        $.ajax({
            cache: false,
            url: '/foto/' + id + '/?isMapview=1',
            success: function (result) {
                openPhotoDrawer(result);
                var originalPhotoColumn = $('#ajapaik-photo-modal-original-photo-column'),
                    rephotoColumn = $('#ajapaik-photo-modal-rephoto-column');
                if (window.photoHistory && window.photoHistory.length > 0) {
                    $('.ajapaik-photo-modal-previous-button').removeClass('disabled');
                }
                if (window.userClosedRephotoTools) {
                    $('#ajapaik-rephoto-selection').hide();
                    rephotoColumn.hide();
                    if (window.isMapview) {
                        $('#ajapaik-photo-modal-original-photo-info-column').removeClass('col-xs-5').removeClass('col-xs-6').addClass('col-xs-12');
                        originalPhotoColumn.removeClass('col-xs-5').removeClass('col-xs-6').addClass('col-xs-12');
                    } else {
                        $('#ajapaik-photo-modal-original-photo-info-column').removeClass('col-xs-4').removeClass('col-xs-5').addClass('col-xs-10');
                        originalPhotoColumn.removeClass('col-xs-4').removeClass('col-xs-5').addClass('col-xs-10');
                    }
                    $('#ajapaik-photo-modal-rephoto-info-column').hide();
                } else {
                    $('#ajapaik-modal-photo-container-container').removeClass('col-xs-9').addClass('col-xs-12');
                }
                if (window.photoModalRephotoArray && window.photoModalRephotoArray[0] && window.photoModalRephotoArray[0][2] !== 'None' && window.photoModalRephotoArray[0][2] !== '') {
                    $('#ajapaik-photo-modal-date-row').show();
                }
                originalPhotoColumn.hover(function () {
                    if (!window.isMobile) {
                        $(this).find('.ajapaik-thumbnail-selection-icon').show();
                        $('.ajapaik-flip-photo-overlay-button').show();
                        if (window.userClosedRephotoTools) {
                            $('#ajapaik-show-rephoto-selection-overlay-button').show();
                        }
                    }
                }, function () {
                    if (!window.isMobile) {
                        $(this).find('.ajapaik-thumbnail-selection-icon').hide();
                        $('.ajapaik-flip-photo-overlay-button').hide();
                        $('#ajapaik-show-rephoto-selection-overlay-button').hide();
                    }
                });
                rephotoColumn.hover(function () {
                    if (!window.isMobile) {
                        if (!window.userClosedRephotoTools) {
                            $('#ajapaik-close-rephoto-overlay-button').show();
                            $('#ajapaik-invert-rephoto-overlay-button').show();
                        }
                    }
                }, function () {
                    if (!window.isMobile) {
                        if (!window.userClosedRephotoTools) {
                            $('#ajapaik-close-rephoto-overlay-button').hide();
                            $('#ajapaik-invert-rephoto-overlay-button').hide();
                        }
                    }
                });
                window.showPhotoMapIfApplicable();
            }
        });
    };
    openPhotoDrawer = function (content) {
        var target = $('#ajapaik-photo-modal');
        photoDrawerOpen = true;
        window.syncMapStateToURL();
        var fullScreenImage = $('#ajapaik-full-screen-image'),
            rephotoFullScreenImage = $('#ajapaik-rephoto-full-screen-image');
        target.html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
            fullScreenImage.attr('data-src', window.photoModalFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
            rephotoFullScreenImage.attr('data-src', window.photoModalRephotoFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
            if (window.photoModalRephotoFullscreenImageSize) {
                window.prepareFullscreen(window.photoModalRephotoFullscreenImageSize[0], window.photoModalRephotoFullscreenImageSize[1], '#ajapaik-rephoto-full-screen-image');
            }
            window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1], '#ajapaik-full-screen-image');
            window.showPhotoMapIfApplicable();
            window.FB.XFBML.parse($('#ajapaik-photo-modal-like').get(0));
        });
        target.on('shown.bs.modal', function () {
            if (window.clickSpecifyAfterPageLoad) {
                $('#ajapaik-photo-modal-specify-location').click();
                window.clickSpecifyAfterPageLoad = false;
            }
        });
    };
    $('#ajapaik-photo-modal').on('shown.bs.modal', function () {
        window.showPhotoMapIfApplicable();
    });
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
        // FIXME: Do this more elegantly
        var historyReplacementString = '/map/';
        if (currentlySelectedMarkerId) {
            historyReplacementString += 'photo/' + currentlySelectedMarkerId + '/';
        }
        if (window.currentlySelectedRephotoId) {
            historyReplacementString += 'rephoto/' + window.currentlySelectedRephotoId + '/';
        }
        if (window.albumId) {
            historyReplacementString += '?album=' + window.albumId;
        }
        historyReplacementString += '&mapType=' + window.map.getMapTypeId();
        if (window.map) {
            historyReplacementString += '&lat=' + window.map.getCenter().lat();
            historyReplacementString += '&lng=' + window.map.getCenter().lng();
            historyReplacementString += '&zoom=' + window.map.zoom;
        }
        if (photoDrawerOpen || window.guessLocationStarted) {
            historyReplacementString += '&photoModalOpen=1';
        }
        if (limitByAlbum) {
            historyReplacementString += '&limitToAlbum=1';
        } else {
            historyReplacementString += '&limitToAlbum=0';
        }
        if (window.guessLocationStarted) {
            historyReplacementString += '&straightToSpecify=1';
        }
        if (historyReplacementString.startsWith('/map/&')) {
            historyReplacementString = historyReplacementString.replace('&', '?');
        }
        if (historyReplacementString.indexOf('?') === -1 && historyReplacementString.indexOf('&') !== -1) {
            historyReplacementString = historyReplacementString.replace('&', '?');
        }
        window.history.replaceState(null, window.title, historyReplacementString);
    };

    window.startGuessLocation = function () {
        if (!window.guessLocationStarted) {
            var startLat = window.map.getCenter().lat(),
                startLon = window.map.getCenter().lng();
            if (window.photoModalPhotoLat && window.photoModalPhotoLng) {
                startLat = window.photoModalPhotoLat;
                startLon = window.photoModalPhotoLng;
            } else {
                startLat = 59;
                startLon = 26;
            }
            $('#ajapaik-map-container').hide();
            $('#ajapaik-photo-modal').hide();
            $('.modal-backdrop').hide();
            $('#ajp-geotagging-container').show().data('AjapaikGeotagger').initializeGeotaggerState({
                thumbSrc: '/foto_thumb/' + photoId + '/400',
                fullScreenSrc: window.photoModalFullscreenImageUrl,
                description: window.currentPhotoDescription,
                sourceKey: window.currentPhotoSourceKey,
                sourceName: window.currentPhotoSourceName,
                sourceURL: window.currentPhotoSourceURL,
                fullScreenWidth: window.photoModalFullscreenImageSize[0],
                fullScreenHeight: window.photoModalFullscreenImageSize[1],
                startLat: startLat,
                startLng: startLon,
                photoId: photoId,
                uniqueGeotagCount: window.photoModalGeotaggingUserCount,
                uniqueGeotagWithAzimuthCount: window.photoModalAzimuthCount,
                mode: 'vantage',
                markerLocked: true,
                isGame: false,
                isMapview: true,
                isGallery: false,
                tutorialClosed: docCookies.getItem('ajapaik_closed_geotagger_instructions') === 'true',
                hintUsed: true
            });
            $('body').css('overflow', 'auto');
            window.guessLocationStarted = true;
            window.syncMapStateToURL();
        }
    };
    window.stopGuessLocation = function () {
        $('#ajapaik-map-container').show();
        $('#ajapaik-photo-modal').show();
        $('.modal-backdrop').show();
        $('#ajp-geotagging-container').hide();
        $('body').css('overflow', 'hidden');
        window.guessLocationStarted = false;
        window.syncMapStateToURL();
    };
    window.closePhotoDrawer = function () {
        $('#ajapaik-photo-modal').modal('toggle');
        photoDrawerOpen = false;
        window.syncMapStateToURL();
    };
    window.uploadCompleted = function (response) {
        $('#ajapaik-rephoto-upload-modal').modal('toggle');
        if (response && response.new_id) {
            window.currentlySelectedRephotoId = response.new_id;
            window.syncMapStateToURL();
            window.location.reload();
        }
    };
    window.toggleVisiblePaneElements = function () {
        if (window.map && !window.guessLocationStarted) {
            window.dottedAzimuthLine.setVisible(false);
            if (!window.comingBackFromGuessLocation) {
                window.deselectMarker();
            } else {
                markerIdToHighlightAfterPageLoad = currentlySelectedMarkerId;
                window.comingBackFromGuessLocation = false;
            }
            if (window.urlParamsInitialized) {
                currentlySelectedMarkerId = null;
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
            currentMapDataRequest = $.post('/map_data/', {
                album: window.albumId,
                //area: window.areaId,
                limit_by_album: limitByAlbum,
                sw_lat: sw.lat(),
                sw_lon: sw.lng(),
                ne_lat: ne.lat(),
                ne_lon: ne.lng(),
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            }, function (response) {
                if (mc) {
                    mc.clearMarkers();
                }
                markers.length = 0;

                if (response.photos) {
                    window.lastMarkerSet = [];
                    for (j = 0, l = response.photos.length; j < l; j += 1) {
                        var currentAzimuth,
                            currentPosition,
                            geodesicEndPoint,
                            angle,
                            angleFix;
                        p = response.photos[j];
                        arrowIcon.rotation = 0;
                        currentAzimuth = p[3];
                        currentPosition = new window.google.maps.LatLng(p[1], p[2]);
                        if (currentAzimuth) {
                            geodesicEndPoint = Math.calculateMapLineEndPoint(currentAzimuth, currentPosition, 1000);
                            angle = Math.getAzimuthBetweenTwoPoints(currentPosition, geodesicEndPoint);
                            angleFix = currentAzimuth - angle;
                            arrowIcon.rotation = currentAzimuth + angleFix;
                            currentIcon = arrowIcon;
                        } else {
                            currentIcon = locationIcon;
                        }
                        if (p[4]) {
                            currentIcon.fillColor = '#007fff';
                        } else {
                            currentIcon.fillColor = 'black';
                        }
                        var marker = new window.google.maps.Marker({
                            id: p[0],
                            icon: currentIcon,
                            rephotoCount: p[4],
                            position: currentPosition,
                            zIndex: 1,
                            azimuth: currentAzimuth,
                            angleFix: angleFix,
                            map: null,
                            anchor: new window.google.maps.Point(0.0, 0.0)
                        });
                        if (angleFix)
                            window.lastMarkerSet.push(p[0]);
                        (function (id) {
                            window.google.maps.event.addListener(marker, 'click', function () {
                                window.highlightSelected(id, true);
                            });
                        })(p[0]);
                        markers.push(marker);
                    }
                }
                if (response.photos && response.photos.length <= 50) {
                    markerClustererSettings.gridSize = 0.0000001;
                } else {
                    markerClustererSettings.gridSize = 60;
                }
                if (mc && mc.clusters_) {
                    mc.clusters_.length = 0;
                }
                if (mc) {
                    window.google.maps.event.clearListeners(mc, 'clusteringend');
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
                    if (window.map.zoom > 17) {
                        markerIdsWithinBounds = [];
                        for (i = 0; i < markers.length; i += 1) {
                            markerIdsWithinBounds.push(markers[i].id);
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
            var mapCenter = window.map.getCenter();
            currentPaneDataRequest = $.post('/pane_contents/', {
                marker_ids: markerIdsWithinBounds, center_lat: mapCenter.lat(), center_lon: mapCenter.lng(),
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            }, function (response) {
                var i,
                    l,
                    targetDiv = $('#ajapaik-photo-pane-content-container');
                if (photoPanel) {
                    //photoPanel.content.html(response);
                    targetDiv.empty();
                    for (i = 0, l = response.length; i < l; i += 1) {
                        targetDiv.append(window.tmpl('ajapaik-pane-element-template', response[i]));
                    }
                    targetDiv.justifiedGallery(justifiedGallerySettings);
                } else {
                    //galleryPanelSettings.content = response;
                    if (window.isMobile) {
                        // TODO: Fix resizable and draggable for mobile, without breaking the overlay buttons, mind you!
                        galleryPanelSettings.resizable = false;
                    }
                    photoPanel = $.jsPanel(galleryPanelSettings);
                    photoPanel.content.append('<div id="ajapaik-photo-pane-content-container"></div>');
                    targetDiv = photoPanel.find('#ajapaik-photo-pane-content-container');
                    for (i = 0, l = response.length; i < l; i += 1) {
                        targetDiv.append(tmpl('ajapaik-pane-element-template', response[i]));
                    }
                    targetDiv.justifiedGallery(justifiedGallerySettings);
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
        currentlySelectedMarkerId = null;
        window.currentlySelectedRephotoId = null;
        $('.ajapaik-mapview-pane-photo-container').find('img').removeClass('translucent-pane-element');
        if (lastHighlightedMarker) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        if (!window.guessResponseReceived) {
            window.dottedAzimuthLine.setVisible(false);
        }
        window.syncMapStateToURL();
    };

    window.highlightSelected = function (markerId, fromMarker, event) {
        if (event) {
            event.preventDefault();
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
                    window.dottedAzimuthLine.setPath([markers[i].position, Math.simpleCalculateMapLineEndPoint(markers[i].azimuth, markers[i].position, 0.01)]);
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
        return false;
    };
    window.handleAlbumChange = function () {
        if (window.albumId) {
            window.location.href = '/map?album=' + window.albumId;
        }
    };
    window.flipPhoto = function () {
        window.photoModalCurrentPhotoFlipStatus = !window.photoModalCurrentPhotoFlipStatus;
        window.userFlippedPhoto = true;
        var fullScreenPhoto = $('#ajapaik-full-screen-image');
        if (fullScreenPhoto.hasClass('ajapaik-photo-flipped')) {
            fullScreenPhoto.removeClass('ajapaik-photo-flipped');
        } else {
            fullScreenPhoto.addClass('ajapaik-photo-flipped');
        }
    };
    setCorrectMarkerIcon = function (marker) {
        if (marker) {
            if (marker.id == currentlySelectedMarkerId) {
                if (marker.azimuth) {
                    arrowIcon.scale = 1.5;
                    arrowIcon.strokeWeight = 2;
                    arrowIcon.fillColor = 'white';
                    arrowIcon.rotation = marker.azimuth + marker.angleFix;
                    if (marker.rephotoCount) {
                        arrowIcon.strokeColor = '#007fff';
                    } else {
                        arrowIcon.strokeColor = 'black';
                    }
                    marker.setIcon(arrowIcon);
                } else {
                    locationIcon.scale = 1.5;
                    locationIcon.strokeWeight = 2;
                    locationIcon.fillColor = 'white';
                    locationIcon.anchor = new window.google.maps.Point(12, 6);
                    if (marker.rephotoCount) {
                        locationIcon.strokeColor = '#007fff';
                    } else {
                        locationIcon.strokeColor = 'black';
                    }
                    marker.setIcon(locationIcon);
                }
            } else {
                if (marker.azimuth) {
                    arrowIcon.scale = 1.0;
                    arrowIcon.strokeWeight = 1;
                    arrowIcon.strokeColor = 'white';
                    arrowIcon.rotation = marker.azimuth + marker.angleFix;
                    if (marker.rephotoCount) {
                        arrowIcon.fillColor = '#007fff';
                    } else {
                        arrowIcon.fillColor = 'black';
                    }
                    marker.setIcon(arrowIcon);
                } else {
                    locationIcon.scale = 1.0;
                    locationIcon.strokeWeight = 1;
                    locationIcon.strokeColor = 'white';
                    locationIcon.anchor = new window.google.maps.Point(12, 0);
                    if (marker.rephotoCount) {
                        locationIcon.fillColor = '#007fff';
                    } else {
                        locationIcon.fillColor = 'black';
                    }
                    marker.setIcon(locationIcon);
                }
            }
        }
    };
    window.initializeMapStateFromOptionalURLParameters = function () {
        var urlMapType = window.getQueryParameterByName('mapType');
        if (window.getQueryParameterByName('fromSelect')) {
            if (window.albumLatLng) {
                window.getMap(window.albumLatLng, 16, false, urlMapType);
            } else if (window.areaLatLng) {
                window.getMap(window.areaLatLng, 16, false, urlMapType);
            }
        } else {
            if (window.preselectPhotoId) {
                // There's a selected photo specified in the URL, select when ready
                currentlySelectedMarkerId = window.preselectPhotoId;
                if (window.preselectPhotoLat && window.preselectPhotoLat) {
                    markerIdToHighlightAfterPageLoad = window.preselectPhotoId;
                }
            }
            if (window.getQueryParameterByName('lat') && window.getQueryParameterByName('lng') && window.getQueryParameterByName('zoom')) {
                // User has very specific parameters, allow to take precedence
                window.getMap(new window.google.maps.LatLng(window.getQueryParameterByName('lat'), window.getQueryParameterByName('lng')),
                    parseInt(window.getQueryParameterByName('zoom'), 10), false, urlMapType);
            } else {
                if (window.preselectPhotoLat && window.preselectPhotoLng) {
                    // We know the location of the photo, let's build the map accordingly
                    window.getMap(new window.google.maps.LatLng(window.preselectPhotoLat, window.preselectPhotoLng), 18, false, urlMapType);
                } else if (window.albumLatLng) {
                    // There's nothing preselected, but we do know the album the photo's in
                    window.getMap(window.albumLatLng, 16, false, urlMapType);
                } else if (window.areaLatLng) {
                    window.getMap(window.areaLatLng, 16, false, urlMapType);
                } else {
                    // No idea
                    window.getMap(null, 16, false, urlMapType);
                }
            }
            if (window.preselectPhotoId && window.getQueryParameterByName('straightToSpecify')) {
                window.userClosedRephotoTools = true;
                window.loadPhoto(window.preselectPhotoId);
                window.clickSpecifyAfterPageLoad = true;
                photoDrawerOpen = true;
            } else if (window.preselectRephotoId) {
                window.loadPhoto(window.preselectPhotoId);
                window.currentlySelectedRephotoId = window.preselectRephotoId;
                photoDrawerOpen = true;
            } else if (window.getQueryParameterByName('photoModalOpen') && window.preselectPhotoId) {
                window.userClosedRephotoTools = true;
                window.loadPhoto(window.preselectPhotoId);
                photoDrawerOpen = true;
            }
        }
        if (window.getQueryParameterByName('limitToAlbum') == 0) {
            deactivateAlbumFilter();
        } else {
            activateAlbumFilter();
        }
        window.preselectPhotoId = false;
        window.preselectRephotoId = false;
        window.syncMapStateToURL();
        window.urlParamsInitialized = true;
    };
    activateAlbumFilter = function () {
        limitByAlbum = true;
        $('#ajapaik-header-album-filter-button-off').hide();
        $('#ajapaik-header-album-filter-button-on').show();
        $('#ajapaik-header-album-filter-button').prop('title', window.gettext('Remove album filter'));
    };
    deactivateAlbumFilter = function () {
        limitByAlbum = false;
        $('#ajapaik-header-album-filter-button-off').show();
        $('#ajapaik-header-album-filter-button-on').hide();
        $('#ajapaik-header-album-filter-button').prop('title', window.gettext('Apply album filter'));
    };
    $(document).ready(function () {
        window.updateLeaderboard();
        window.realMapElement = $('#ajapaik-map-canvas')[0];
        window.isMapview = true;
        $(window.input).show();
        guessPanelContainer = $('#ajapaik-guess-panel-container');
        $('#ajapaik-game-description-viewing-warning').hide();
        $('#ajapaik-header-album-filter-button').click(function () {
            if (!limitByAlbum) {
                activateAlbumFilter();
            } else {
                deactivateAlbumFilter();
            }
            window.toggleVisiblePaneElements();
            window.syncMapStateToURL();
        });
        if (window.preselectPhotoId) {
            currentlySelectedMarkerId = window.preselectPhotoId;
        }
        window.initializeMapStateFromOptionalURLParameters();
        $(document).on('hidden.bs.modal', '#ajapaik-photo-modal', function () {
            window.currentlySelectedRephotoId = false;
            photoDrawerOpen = false;
            window.syncMapStateToURL();
        });
        $(document).on('click', '#ajapaik-mapview-my-location-button', function () {
            window.getGeolocation(window.handleGeolocation);
            centerOnMapAfterLocating = true;
        });
        window.handleGeolocation = function (location) {
            $('#ajapaik-geolocation-error').hide();
            if (centerOnMapAfterLocating) {
                window.map.setCenter(new window.google.maps.LatLng(location.coords.latitude, location.coords.longitude));
                centerOnMapAfterLocating = false;
            }
        };
        $('#logout-button').click(function () {
            window._gaq.push(['_trackEvent', 'Map', 'Logout']);
        });
        if (window.map !== undefined) {
            window.map.scrollwheel = true;
            window.mapMapviewClickListener = window.google.maps.event.addListener(window.map, 'click', function () {
                window.deselectMarker();
            });
        }
        $(document).on('click', '.ajapaik-mapview-pane-photo-container', function (e) {
            e.preventDefault();
            e.stopPropagation();
        });
        //TODO: There has to be a better way
        window.paneImageHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-azimuth').show();
            myParent.find('.ajapaik-thumbnail-selection-icon').show();
        };
        window.paneImageHoverOut = function (e) {
            var myParent = $(e).parent(),
                icon = myParent.find('.ajapaik-thumbnail-selection-icon');
            if (parseInt($(this).data('id'), 10) !== parseInt(currentlySelectedMarkerId, 10)) {
                myParent.find('.ajapaik-azimuth').hide();
            }
            if (!icon.hasClass('ajapaik-thumbnail-selection-icon-white')) {
                myParent.find('.ajapaik-thumbnail-selection-icon').hide();
            }
        };
        window.paneRephotoCountHoverIn = function (e) {
            $(e).parent().find('.ajapaik-azimuth').show();
            return false;
        };
        window.paneRephotoCountHoverOut = function (e) {
            if (parseInt($(this).data('id'), 10) !== parseInt(currentlySelectedMarkerId, 10)) {
                $(e).parent().find('.ajapaik-azimuth').hide();
            }
            return false;
        };
    });
}(jQuery));