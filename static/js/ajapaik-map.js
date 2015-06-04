(function ($) {
    'use strict';
    /*jslint nomen: true*/
    var photoId,
        currentMapBounds,
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
        lineLength = 1000,
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
        ffWheelListener,
        markers = [],
        nonFFWheelListener,
        noticeDiv,
        noticeDivXs,
        markerIdToHighlightAfterPageLoad,
        targetTopToScrollToAfterPaneLoad,
        updateBoundingEdge,
        maxGalleryWidth = $(window).width() * 0.2,
        maxGalleryHeight = $('#ajapaik-map-canvas').height(),
        switchSearchBoxPosition,
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
        centerOnMapAfterLocating = false,
        specifyStart,
        specifyStartZoom,
        albumFilterButton = $('#ajapaik-header-album-filter-button'),
        activateAlbumFilter,
        deactivateAlbumFilter;
    window.loadPhoto = function (id) {
        photoId = id;
        $.ajax({
            cache: false,
            url: '/foto/' + id + '/?isMapview=1',
            success: function (result) {
                openPhotoDrawer(result);
            }
        });
    };
    openPhotoDrawer = function (content) {
        photoDrawerOpen = true;
        window.syncMapStateToURL();
        var fullScreenImage = $('#ajapaik-full-screen-image'),
            rephotoFullScreenImage = $('#ajapaik-rephoto-full-screen-image');
        $('#ajapaik-photo-modal').html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
            fullScreenImage.prop('src', window.photoModalFullscreenImageUrl);
            rephotoFullScreenImage.prop('src', window.photoModalRephotoFullscreenImageUrl);
            $('#ajapaik-guess-panel-photo').prop('src', window.photoModalCurrentImageUrl);
            //window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1]);
            if (window.photoModalRephotoFullscreenImageSize) {
                window.prepareFullscreen(window.photoModalRephotoFullscreenImageSize[0], window.photoModalRephotoFullscreenImageSize[1], '#ajapaik-rephoto-full-screen-image');
            }
            window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1], '#ajapaik-full-screen-image');
            $('#ajapaik-guess-panel-description').html(window.currentPhotoDescription).show();
            $('.ajapaik-game-show-description-button').hide();
            if (window.clickSpecifyAfterPageLoad) {
                setTimeout(function () {
                    if (!window.guessLocationStarted) {
                        $('#ajapaik-photo-modal-specify-location').click();
                        window.clickSpecifyAfterPageLoad = false;
                    }
                }, 3000);
            }
            window.FB.XFBML.parse($('#ajapaik-photo-modal-like').get(0));
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

    if (typeof String.prototype.startsWith !== 'function') {
        String.prototype.startsWith = function (str) {
            return this.indexOf(str) === 0;
        };
    }

    window.syncMapStateToURL = function () {
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
        if (window.areaId) {
            if (!window.albumId) {
                historyReplacementString += '?area=' + window.areaId;
            } else {
                historyReplacementString += '&area=' + window.areaId;
            }
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
        if (albumFilterButton.hasClass('ajapaik-header-album-filter-button-off')) {
            historyReplacementString += '&limitToAlbum=0';
        } else {
            historyReplacementString += '&limitToAlbum=1';
        }
        if (historyReplacementString.startsWith('/map/&')) {
            historyReplacementString = historyReplacementString.replace('&', '?');
        }
        if (historyReplacementString.indexOf('?') === -1 && historyReplacementString.indexOf('&') !== -1) {
            historyReplacementString = historyReplacementString.replace('&', '?');
        }
        window.History.replaceState(null, window.title, historyReplacementString);
    };

    switchSearchBoxPosition = function () {
        var topRightControls = window.map.controls[window.google.maps.ControlPosition.TOP_RIGHT],
            topLeftControls = window.map.controls[window.google.maps.ControlPosition.TOP_LEFT],
            indexOfControl,
            wasInTopRight;
        topRightControls.forEach(function (element, index) {
            if (element.id === 'pac-input-mapview') {
                indexOfControl = index;
                wasInTopRight = true;
            }
        });
        topLeftControls.forEach(function (element, index) {
            if (element.id === 'pac-input') {
                indexOfControl = index;
                wasInTopRight = false;
            }
        });
        if (wasInTopRight) {
            topRightControls.removeAt(indexOfControl);
            $(window.input).prop('id', 'pac-input');
            topLeftControls.push(window.input);
        } else {
            topLeftControls.removeAt(indexOfControl);
            $(window.input).prop('id', 'pac-input-mapview');
            topRightControls.push(window.input);
        }
        window.searchBox = new window.google.maps.places.SearchBox(/** @type {HTMLInputElement} */(window.input));
    };

    window.startGuessLocation = function () {
        if (!window.guessLocationStarted) {
            specifyStart = window.map.getCenter();
            specifyStartZoom = window.map.zoom;
            $('.ajapaik-mapview-game-button').hide();
            window.guessResponseReceived = false;
            if (window.map.zoom < 17) {
                window.map.setZoom(17);
            }
            var mq = window.matchMedia('(min-width: 481px)');
            if (mq.matches) {
                $('#ajapaik-map-container').animate({width: '70%'});
                guessPanelContainer.show();
                guessPanelContainer.animate({width: '30%'}, {complete: function () {
                    window.google.maps.event.trigger(window.map, 'resize');
                }});
                $('#ajapaik-geotag-info-panel-container').animate({width: '30%'});
                $('#ajapaik-guess-panel-container-xs').hide();
            } else {
                $('#ajapaik-map-canvas').animate({height: '70%'});
                $('#ajapaik-guess-panel-container-xs').animate({height: '25%'}, {complete: function () {
                    window.google.maps.event.trigger(window.map, 'resize');
                    $('#ajapaik-map-button-container-xs').show();
                }});
                guessPanelContainer.hide();
            }
            window.map.setOptions({
                zoomControlOptions: {
                    position: window.google.maps.ControlPosition.LEFT_CENTER
                },
                streetViewControlOptions: {
                    position: window.google.maps.ControlPosition.LEFT_CENTER
                }
            });
            $('#ajapaik-guess-panel-stats').show();
            $('#ajapaik-guess-panel-photo').prop('src', window.photoModalCurrentImageUrl);
            if (!mq.matches) {
                if (window.currentPhotoDescription) {
                    $('#ajapaik-guess-panel-description-xs').html(window.currentPhotoDescription);
                    $('#ajapaik-guess-panel-info-panel-xs').show();
                }
                $('#ajapaik-guess-panel-photo-xs').prop('src', window.photoModalCurrentImageUrl);
            }
            switchSearchBoxPosition();
            window.userFlippedPhoto = false;
            window.guessLocationStarted = true;
            window.dottedAzimuthLine.setVisible(false);
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
                if (!window.guessResponseReceived) {
                    window.firstDragDone = true;
                    if (window.guessLocationStarted) {
                        $('.ajapaik-marker-center-lock-button').show();
                    }
                }
            });
            window.mapMarkerPositionChangedListener = window.google.maps.event.addListener(window.marker, 'position_changed', function () {
                window.disableSave = false;
            });
            $('#ajapaik-photo-modal').modal('toggle');
            if (photoPanel) {
                photoPanel.close();
            }
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
            window._gaq.push(['_trackEvent', 'Map', 'Specify location']);
        }
    };
    window.handleGuessResponse = function (guessResponse) {
        window.guessResponseReceived = true;
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
        $('.ajapaik-marker-center-lock-button').hide();
        noticeDiv = $('#ajapaik-guess-feedback-panel');
        noticeDivXs = $('#ajapaik-guess-feedback-panel-xs');
        $('#ajapaik-guess-panel-stats').hide();
        $('#ajapaik-map-button-container').hide();
        $('#ajapaik-map-button-container-xs').hide();
        $('#ajapaik-guess-panel-photo-container-xs').hide();
        $('#ajapaik-guess-panel-info-panel-xs').hide();
        noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').text(window.gettext('Points awarded') + ': ' + guessResponse.currentScore);
        noticeDivXs.find('#ajapaik-game-guess-feedback-points-gained-xs').text(window.gettext('Points awarded') + ': ' + guessResponse.currentScore);
        noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').show();
        noticeDivXs.find('#ajapaik-game-guess-feedback-points-gained-xs').show();
        noticeDiv.show();
        var mq = window.matchMedia('(min-width: 481px)');
        if (!mq.matches) {
            noticeDivXs.show();
        }
        if (guessResponse.heatmapPoints && guessResponse.newEstimatedLocation) {
            window.mapDisplayHeatmapWithEstimatedLocation(guessResponse);
        }
    };

    window.stopGuessLocation = function () {
        if (!window.markerLocked) {
            $('.ajapaik-marker-center-lock-button')[0].click();
        }
        $('.ajapaik-mapview-game-button').show();
        $('#pac-input').val(null);
        $('#pac-input-mapview').val(null);
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
        var mq = window.matchMedia('(min-width: 481px)');
        if (!mq.matches) {
            $('#ajapaik-guess-panel-container-xs').animate({height: 0});
            $('#ajapaik-map-canvas').animate({height: '100%', complete: function () {
                window.google.maps.event.trigger(window.map, 'resize');
            }});
        } else {
            $('#ajapaik-guess-panel-container').hide(function () {
                window.google.maps.event.trigger(window.map, 'resize');
            });
            $('#ajapaik-map-container').animate({width: '100%', complete: function () {
                window.google.maps.event.trigger(window.map, 'resize');
            }});
        }
        if (photoPanel) {
            photoPanel.close();
            photoPanel = undefined;
        }
        window.map.setOptions({
            zoomControlOptions: {
                position: window.google.maps.ControlPosition.RIGHT_CENTER
            },
            streetViewControlOptions: {
                position: window.google.maps.ControlPosition.RIGHT_CENTER
            }
        });
        switchSearchBoxPosition();
        window.map.getStreetView().setVisible(false);
        $('#ajapaik-map-button-container').show();
        $('#ajapaik-map-button-container-xs').show();
        $('#ajapaik-guess-feedback-panel').hide();
        $('#ajapaik-guess-feedback-panel-xs').hide();
        $('#ajapaik-guess-panel-info-panel-xs').show();
        $('#ajapaik-guess-panel-photo-container-xs').show();
        lastRequestedPaneMarkersIds = undefined;
        window.map.set('scrollwheel', true);
        window.realMapElement.removeEventListener('mousewheel', nonFFWheelListener);
        window.realMapElement.removeEventListener('DOMMouseScroll', ffWheelListener);
        $('.center-marker').hide();
        if (specifyStart) {
            window.map.setCenter(specifyStart);
            if (specifyStartZoom) {
                window.map.setZoom(specifyStartZoom);
            }
        }
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
        window.firstDragDone = false;
        window.setCursorToAuto();
        window.dottedAzimuthLine.setMap(null);
        window.guessLocationStarted = false;
        window.toggleVisiblePaneElements();
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
                area: window.areaId,
                limit_by_album: !albumFilterButton.hasClass('ajapaik-header-album-filter-button-off'),
                sw_lat: sw.lat(),
                sw_lon: sw.lng(),
                ne_lat: ne.lat(),
                ne_lon: ne.lng(),
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            }, function (response) {
                if (mc) {
                    mc.clearMarkers();
                }
                markers.length = 0;

                if (response.photos) {
                    window.lastMarkerSet = [];
                    for (j = 0, l = response.photos.length; j < l; j += 1) {
                        p = response.photos[j];
                        arrowIcon.rotation = 0;
                        if (p[3]) {
                            arrowIcon.rotation = p[3];
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
                            position: new window.google.maps.LatLng(p[1], p[2]),
                            zIndex: 1,
                            azimuth: p[3],
                            map: null,
                            anchor: new window.google.maps.Point(0.0, 0.0)
                        });
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
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')}, function (response) {
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
                    //$('.jsPanel-content').scroll(function () {
                    //    window.deselectMarker();
                    //});
                }
                if (markerIdToHighlightAfterPageLoad) {
                    window.highlightSelected(markerIdToHighlightAfterPageLoad, true);
                    markerIdToHighlightAfterPageLoad = false;
                }
                currentPaneDataRequest = undefined;
                lastRequestedPaneMarkersIds = markerIdsWithinBounds;
                //window.FB.XFBML.parse();
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
        var fullScreenPhoto = $('#ajapaik-full-screen-image'),
            guessPhoto = $('#ajapaik-guess-panel-photo');
        if (fullScreenPhoto.hasClass('ajapaik-photo-flipped')) {
            fullScreenPhoto.removeClass('ajapaik-photo-flipped');
        } else {
            fullScreenPhoto.addClass('ajapaik-photo-flipped');
        }
        if (guessPhoto.hasClass('ajapaik-photo-flipped')) {
            guessPhoto.removeClass('ajapaik-photo-flipped');
        } else {
            guessPhoto.addClass('ajapaik-photo-flipped');
        }
    };

    setCorrectMarkerIcon = function (marker) {
        if (marker) {
            if (marker.id == currentlySelectedMarkerId) {
                if (marker.azimuth) {
                    arrowIcon.scale = 1.5;
                    arrowIcon.strokeWeight = 2;
                    arrowIcon.fillColor = 'white';
                    arrowIcon.rotation = marker.azimuth;
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
                    arrowIcon.rotation = marker.azimuth;
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
            //if (marker.rephotoCount) {
            //    if (marker.id == currentlySelectedMarkerId) {
            //        marker.setIcon(blueMarkerIcon35);
            //    } else {
            //        marker.setIcon(blueMarkerIcon20Transparent);
            //    }
            //} else {
            //    if (marker.id == currentlySelectedMarkerId) {
            //        marker.setIcon(blackMarkerIcon35);
            //    } else {
            //        marker.setIcon(blackMarkerIcon20Transparent);
            //    }
            //}
        }
    };




    window.initializeMapStateFromOptionalURLParameters = function () {
        var urlMapType = window.getQueryParameterByName('mapType');
        if (window.getQueryParameterByName('fromSelect')) {
            if (window.albumLatLng) {
                window.getMap(window.albumLatLng, 13, false, urlMapType);
            } else if (window.areaLatLng) {
                window.getMap(window.areaLatLng, 13, false, urlMapType);
            }
        } else {
            if (window.preselectPhotoId && !window.getQueryParameterByName('straightToSpecify')) {
                // There's a selected photo specified in the URL, select when ready
                currentlySelectedMarkerId = window.preselectPhotoId;
                markerIdToHighlightAfterPageLoad = window.preselectPhotoId;
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
                    window.getMap(window.albumLatLng, 13, false, urlMapType);
                } else if (window.areaLatLng) {
                    window.getMap(window.areaLatLng, 13, false, urlMapType);
                } else {
                    // No idea
                    window.getMap(null, 13, false, urlMapType);
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
        if (window.getQueryParameterByName('fromModal') != 1) {
            $('#ajapaik-header-album-name').click();
        }
        window.preselectPhotoId = false;
        window.preselectRephotoId = false;
        window.syncMapStateToURL();
        window.urlParamsInitialized = true;
    };
    activateAlbumFilter = function () {
        albumFilterButton.removeClass('ajapaik-header-album-filter-button-off');
        albumFilterButton.prop('title', window.gettext('Remove album filter'));
    };
    deactivateAlbumFilter = function () {
        albumFilterButton.addClass('ajapaik-header-album-filter-button-off');
        albumFilterButton.prop('title', window.gettext('Apply album filter'));
    };
    $(document).ready(function () {
        $('#ajapaik-album-name-container').css('visibility', 'visible');
        $('#ajapaik-header-game-button').show();
        $('#ajapaik-header-grid-button').show();
        window.realMapElement = $('#ajapaik-map-canvas')[0];
        window.mapInfoPanelGeotagCountElement = $('#ajapaik-game-map-geotag-count');
        window.mapInfoPanelAzimuthCountElement = $('#ajapaik-game-map-geotag-with-azimuth-count');
        window.saveLocationButton = $('.ajapaik-save-location-button');
        window.updateLeaderboard();
        window.isMapview = true;
        $(window.input).show();
        $('.ajapaik-navmenu').on('shown.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').show();
            if (window.albumId) {
                $('#ajapaik-album-selection-navmenu').scrollTop($(".ajapaik-album-selection-item[data-id='" + window.albumId + "']").offset().top);
            }
        }).on('hidden.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').hide();
        });
        guessPanelContainer = $('#ajapaik-guess-panel-container');
        $('#ajapaik-game-description-viewing-warning').hide();
        albumFilterButton.click(function () {
            var $this = $(this);
            if ($this.hasClass('ajapaik-header-album-filter-button-off')) {
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
        if (window.docCookies.getItem('ajapaik_closed_tutorial')) {
            window.userClosedTutorial = true;
        }
        window.initializeMapStateFromOptionalURLParameters();
        $(document).on('hidden.bs.modal', '#ajapaik-photo-modal', function () {
            window.currentlySelectedRephotoId = false;
            photoDrawerOpen = false;
            window.syncMapStateToURL();
        });
        $(document).on('click', '.ajapaik-mapview-game-button', function () {
            window.location.href = '/game?album=' + window.albumId;
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
        window.saveLocationButton.on('click', function () {
            $('.ajapaik-marker-center-lock-button').hide();
            window.setCursorToAuto();
            if (window.disableSave) {
                window._gaq.push(['_trackEvent', 'Mapview', 'Forgot to move marker']);
                window.alert(window.gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view.'));
            } else {
                // TODO: Flip data and stuff
                window.saveLocation(window.marker, photoId, window.photoModalCurrentPhotoFlipStatus, true, window.userFlippedPhoto, window.degreeAngle, window.azimuthLineEndPoint, 1);
                if (window.saveDirection) {
                    window._gaq.push(['_trackEvent', 'Mapview', 'Save location and direction']);
                } else {
                    window._gaq.push(['_trackEvent', 'Mapview', 'Save location only']);
                }
            }
        });
        if (window.map !== undefined) {
            window.mapMapviewClickListener = window.google.maps.event.addListener(window.map, 'click', function() {
                window.deselectMarker();
            });
        }
        $('#logout-button').click(function () {
            window._gaq.push(['_trackEvent', 'Map', 'Logout']);
        });
        // TODO: We have double of this, confusing
        $('.ajapaik-game-next-photo-button').click(function () {
            window.stopGuessLocation();
            window._gaq.push(['_trackEvent', 'Map', 'Next photo']);
        });
        if (window.map !== undefined) {
            window.map.scrollwheel = true;
        }
        $(document).on('click', '#ajapaik-game-flip-photo-button', function () {
            var button = $(this);
            if (button.hasClass('active')) {
                button.removeClass('active');
            } else {
                button.addClass('active');
            }
            window.flipPhoto();
        });
        $(document).on('click', '.ajapaik-game-feedback-next-button', function () {
            window.stopGuessLocation();
        });
        //TODO: There has to be a better way
        window.paneImageHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-azimuth').show();
        };
        window.paneImageHoverOut = function (e) {
            if (parseInt($(this).data('id'), 10) !== parseInt(currentlySelectedMarkerId, 10)) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-azimuth').hide();
            }
        };
        window.paneRephotoCountHoverIn = function (e) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-azimuth').show();
            return false;
        };
        window.paneRephotoCountHoverOut = function (e) {
            if (parseInt($(this).data('id'), 10) !== parseInt(currentlySelectedMarkerId, 10)) {
                var myParent = $(e).parent();
                myParent.find('.ajapaik-azimuth').hide();
            }
            return false;
        };
    });
}(jQuery));