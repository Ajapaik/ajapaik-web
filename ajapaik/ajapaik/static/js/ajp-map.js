(function() {
    'use strict';
    /*jslint nomen: true*/
    /*global docCookies*/
    /*global moment*/
    /*global gtag*/
    /*global $*/
    /*global google*/
    /*global commonVgmapi*/

    const MAP_FILTERS = ['mapType',
        'album',
        'lat',
        'lng',
        'zoom',
        'maps-city',
        'maps-index',
        'photoModalOpen',
        'limitToAlbum',
        'straightToSpecify',
        'q'];

    var markerClustererSettings = {
        minimumClusterSize: 2,
        maxZoom: 17,
    };

    var arrowIcon = {
        path: 'M12 2l-7.5 18.29.71.71 6.79-3 6.79 3 .71-.71z',
        strokeColor: 'white',
        strokeOpacity: 1,
        strokeWeight: 1,
        fillColor: 'black',
        fillOpacity: 1,
        rotation: 0,
        scale: 1.0,
        anchor: new google.maps.Point(12, 12),
    };

    var locationIcon = {
        path: 'M12 2c-3.87 0-7 3.13-7 7 0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
        strokeColor: 'white',
        strokeOpacity: 1,
        strokeWeight: 1,
        fillColor: 'black',
        fillOpacity: 1,
        scale: 1.0,
        anchor: new google.maps.Point(12, 0),
    };

    var sidePanelPhotosBunchSize = 10;

    // Variables
    var photoId,
        limitByAlbum,
        maxIndex = 2,
        lastHighlightedMarker,
        photosOnSidePanel = [],
        lastSelectedMarkerId,
        currentlySelectedMarker,
        targetPaneElement,
        mc,
        currentMapDataRequest,
        photoDrawerOpen = false,
        markers = [],
        loadedPhotosCount = 0,
        centerOnMapAfterLocating = false,
        current_bunch = 1;


    window.isSidePanelOpen = false;
    document.getElementById('map-side-panel').style.opacity = 0;
    window.userClosedRephotoTools = false;
    window.userClosedSimilarPhotoTools = true;

    function findMarkerByPhotoId(photoId) {
        return markers.find(function(marker) {
            return marker.photoData.id === photoId;
        });
    }

    window.loadPhoto = function(id) {
        photoId = id;
        $.ajax({
            cache: false,
            url: '/photo/' + id + '/?isMapview=1',
            success: function(result) {
                openPhotoDrawer(result);
                var mainPhotoContainer = $('#ajp-modal-photo-container'),
                    rephotoColumn = $('#ajp-photo-modal-rephoto-column'),
                    rephotoContainer = $('#ajp-modal-rephoto-container'),
                    similarPhotoColumn = $('#ajp-photo-modal-similar-photo-column'),
                    similarPhotoContainer = $('#ajp-modal-similar-photo-container');
                if (window.photoHistory && window.photoHistory.length > 0) {
                    $('.ajp-photo-modal-previous-button').removeClass('disabled');
                }
                if (window.userClosedRephotoTools) {
                    $('#ajp-rephoto-selection').hide();
                    rephotoColumn.hide();
                    $('#ajp-photo-rephoto-info-column').hide();
                }
                if (window.userClosedSimilarPhotoTools) {
                    $('#ajp-similar-photo-selection').hide();
                    similarPhotoColumn.hide();
                    $('#ajp-photo-modal-similar-photo-info-column').hide();
                }
                if (window.photoModalRephotoArray && window.photoModalRephotoArray[0] && window.photoModalRephotoArray[0][2] !== 'None' && window.photoModalRephotoArray[0][2] !== '') {
                    $('#ajp-photo-modal-date-row').show();
                }
                mainPhotoContainer.hover(function() {
                    if (!window.isMobile) {
                        $('.ajp-thumbnail-selection-icon').show('fade', 250);
                        if (window.userClosedSimilarPhotoTools) {
                            $('.ajp-show-similar-photo-selection-overlay-button').show('fade', 250);
                        }
                        if (window.userClosedRephotoTools) {
                            $('.ajp-show-rephoto-selection-overlay-button').show('fade', 250);
                        }
                    }
                }, function() {
                    if (!window.isMobile) {
                        $('.ajp-thumbnail-selection-icon').hide('fade', 250);
                        $('.ajp-show-similar-photo-selection-overlay-button').hide('fade', 250);
                        $('.ajp-show-rephoto-selection-overlay-button').hide('fade', 250);
                    }
                });
                rephotoContainer.hover(function() {
                    if (!window.isMobile) {
                        if (!window.userClosedRephotoTools) {
                            $('.ajp-close-rephoto-overlay-button').show('fade', 250);
                            $('.ajp-invert-rephoto-overlay-button').show('fade', 250);
                            $('#ajp-rephoto-selection').show();
                        }
                    }
                }, function() {
                    if (!window.isMobile) {
                        if (!window.userClosedRephotoTools) {
                            $('.ajp-close-rephoto-overlay-button').hide('fade', 250);
                            $('.ajp-invert-rephoto-overlay-button').hide('fade', 250);
                            $('#ajp-rephoto-selection').hide();
                        }
                    }
                });
                similarPhotoContainer.hover(function() {
                    if (!window.isMobile) {
                        if (!window.userClosedSimilarPhotoTools) {
                            $('.ajp-close-similar-photo-overlay-button').show('fade', 250);
                            $('.ajp-invert-similar-photo-overlay-button').show('fade', 250);
                            $('#ajp-similar-photo-selection').show();
                        }
                    }
                }, function() {
                    if (!window.isMobile) {
                        if (!window.userClosedSimilarPhotoTools) {
                            $('.ajp-close-similar-photo-overlay-button').hide('fade', 250);
                            $('.ajp-invert-similar-photo-overlay-button').hide('fade', 250);
                            $('#ajp-similar-photo-selection').hide();
                        }
                    }
                });
                window.showPhotoMapIfApplicable();
            },
        });
    };


    var openPhotoDrawer = function(content) {
        var target = $('#ajp-photo-modal');
        photoDrawerOpen = true;
        window.syncMapStateToURL();
        var fullScreenImage = $('#ajp-fullscreen-image'),
            rephotoFullScreenImage = $('#ajp-rephoto-full-screen-image'),
            similarFullScreenImage = $('#ajp-similar-photo-full-screen-image');
        target.html(content).modal().find('#ajp-modal-photo').on('load', function() {
            fullScreenImage.attr('data-src', window.photoModalFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
            rephotoFullScreenImage.attr('data-src', window.photoModalRephotoFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
            similarFullScreenImage.attr('data-src', window.photoModalSimilarFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
            window.showPhotoMapIfApplicable();
            window.FB.XFBML.parse($('#ajp-photo-modal-like').get(0));
        });
        target.on('shown.bs.modal', function() {
            if (window.clickSpecifyAfterPageLoad) {
                $('#ajp-photo-modal-specify-location').click();
                window.clickSpecifyAfterPageLoad = false;
            }
        });
    };


    $('#ajp-photo-modal').on('shown.bs.modal', function() {
        window.showPhotoMapIfApplicable();
    });

    var updateBoundingEdge = function(edge) {
        var scale = Math.pow(2, window.map.getZoom()),
            projection = window.map.getProjection(),
            edgePixelCoordinates = projection.fromLatLngToPoint(edge);
        if (window.innerWidth > 768) {
            edgePixelCoordinates.x = (edgePixelCoordinates.x * scale + $('#map-side-panel').width() + 50) / scale;
            return projection.fromPointToLatLng(edgePixelCoordinates);
        } else {
            edgePixelCoordinates.y = (edgePixelCoordinates.y * scale + $('#map-side-panel').height() + 50) / scale;
            return projection.fromPointToLatLng(edgePixelCoordinates);
        }
    };

    window.syncMapStateToURL = function() {
        // FIXME: Do this more elegantly
        let uriPath = '/map/';
        if (currentlySelectedMarker) {
            uriPath += 'photo/' + currentlySelectedMarker.photoData.id + '/';
        } else if (window.currentlySelectedRephotoId) {
            uriPath += 'rephoto/' + window.currentlySelectedRephotoId + '/';
        }
        let uri = URI(window.location);
        uri.path = uriPath;

        MAP_FILTERS.forEach(filter => uri.removeQuery(filter));

        if (window.albumId) {
            uri.addQuery('album', window.albumId);
        }
        if (window.map) {
            var typeId = window.map.getMapTypeId();
            uri.addQuery('mapType', typeId);
            uri.addQuery('lat', window.map.getCenter().lat());
            uri.addQuery('lng', window.map.getCenter().lng());
            uri.addQuery('zoom', window.map.zoom);

            if (typeId === 'old-maps') {
                uri.addQuery('maps-city', commonVgmapi.vars.site);
                uri.addQuery('maps-city', commonVgmapi.vars.layerIndex);
            }
        }

        if (photoDrawerOpen || window.suggestionLocationStarted) {
            uri.addQuery('photoModalOpen', 1);
        }

        uri.addQuery('limitToAlbum', limitByAlbum ? 1 : 0);

        if (window.suggestionLocationStarted) {
            uri.addQuery('straightToSpecify', 1);
        }
        if (window.photoQuery) {
            uri.addQuery('q', window.photoQuery);
            $('#ajp-photo-filter-box').val(decodeURIComponent(window.photoQuery).replace('%2C', ',').replace('%3A', ':').replace('%2F', '/').replace('+', ' '));
        }

        window.history.replaceState(null, window.title, uri);
    };


    window.startSuggestionLocation = function() {
        if (!window.suggestionLocationStarted) {
            let startLat = 59;
            let startLon = 26;
            if (window.photoModalPhotoLat && window.photoModalPhotoLng) {
                startLat = window.photoModalPhotoLat;
                startLon = window.photoModalPhotoLng;
            }
            $('#ajp-map-container').hide();
            $('#map-side-panel').hide();
            $('#close-btn').hide();
            $('#open-btn').hide();
            $('#ajp-photo-modal').hide();
            $('.modal-backdrop').hide();
            $('#ajp-geotagging-container').show().data('AjapaikGeotagger').initializeGeotaggerState({
                thumbSrc: '/photo-thumb/' + photoId + '/400/',
                photoFlipped: window.photoModalCurrentPhotoFlipped,
                photoInverted: window.photoModalCurrentPhotoInverted,
                fullScreenSrc: window.photoModalFullscreenImageUrl,
                description: window.currentPhotoDescription,
                sourceKey: window.currentPhotoSourceKey,
                sourceName: window.currentPhotoSourceName,
                sourceURL: window.currentPhotoSourceURL,
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
                hintUsed: true,
            });
            $('body').css('overflow', 'auto');
            window.suggestionLocationStarted = true;
            window.syncMapStateToURL();
        }
    };


    window.stopSuggestionLocation = function() {
        $('#ajp-map-container').show();
        $('#map-side-panel').show();
        $('#close-btn').show();
        $('#open-btn').show();
        $('#ajp-photo-modal').show(0, function() {
            let photoHeight = $('#ajp-photo-modal-original-photo-column').height();
            if (photoHeight) {
                if (document.getElementById('ajp-photo-modal-map-container')) {
                    document.getElementById('ajp-photo-modal-map-container').style.height = photoHeight + 'px';
                }
            }
        });
        $('.modal-backdrop').show();
        $('#ajp-geotagging-container').hide();
        $('body').css('overflow', 'hidden');
        window.suggestionLocationStarted = false;
        window.syncMapStateToURL();
    };


    window.closePhotoDrawer = function() {
        $('#ajp-photo-modal').modal('hide');
        photoDrawerOpen = false;
        window.syncMapStateToURL();
    };


    window.uploadCompleted = function(response) {
        $('#ajp-rephoto-upload-modal').modal('hide');
        if (response && response.new_id) {
            window.currentlySelectedRephotoId = response.new_id;
            window.syncMapStateToURL();
            window.location.reload();
        }
    };


    window.toggleVisiblePaneElements = function() {
        if (window.map && !window.suggestionLocationStarted) {
            window.morePhotosCanBeLoaded = false;
            if (!window.comingBackFromSuggestionLocation) {
                window.deselectMarker();
            } else {
                window.comingBackFromSuggestionLocation = false;
            }
            if (window.urlParamsInitialized) {
                currentlySelectedMarker = null;
            }
            window.syncMapStateToURL();
            var currentMapBounds = window.map.getBounds();
            var ne = currentMapBounds.getNorthEast();
            var sw = currentMapBounds.getSouthWest();
            if (currentMapDataRequest) {
                currentMapDataRequest.abort();
            }
            sw = updateBoundingEdge(sw);

            let searchParams = new URLSearchParams(document.location.search);
            var payload = {
                album: window.albumId,
                limit_by_album: limitByAlbum,
                sw_lat: sw.lat(),
                sw_lon: sw.lng(),
                ne_lat: ne.lat(),
                ne_lon: ne.lng(),
                q: window.photoQuery,
                // Shared query params (gallery/album/map)
                portrait: searchParams.get('portrait'),
                square: searchParams.get('square'),
                landscape: searchParams.get('landscape'),
                panoramic: searchParams.get('panoramic'),
                backsides: searchParams.get('backsides'),
                people: searchParams.get('people'),
                ground_viewpoint_elevation: searchParams.get('ground_viewpoint_elevation'),
                raised_viewpoint_elevation: searchParams.get('raised_viewpoint_elevation'),
                aerial_viewpoint_elevation: searchParams.get('aerial_viewpoint_elevation'),
                interiors: searchParams.get('interiors'),
                exteriors: searchParams.get('exteriors'),
                no_geotags: searchParams.get('no_geotags'),
                high_quality: searchParams.get('high_quality'),
                date_from: searchParams.get('date_from'),
                date_to: searchParams.get('date_to'),
                // Shared sorting parameters
                order1: searchParams.get('order1'),
                order2: searchParams.get('order2'),
                order3: searchParams.get('order3'),
                // CSRF token
                csrfmiddlewaretoken: docCookies.getItem('csrftoken'),
            };
            if (window.map.zoom <= markerClustererSettings.maxZoom) {
                payload.count_limit = 1000;
            }
            currentMapDataRequest = $.post(window.mapDataURL, payload, function(response) {
                if (mc) {
                    mc.clearMarkers();
                }
                photosOnSidePanel = [];
                loadedPhotosCount = 0;
                markers.length = 0;

                if (response.photos) {
                    window.lastMarkerSet = [];
                    for (var j = 0; j < response.photos.length; j++) {
                        var photo = response.photos[j];
                        var currentPosition = new google.maps.LatLng(
                            photo.lat,
                            photo.lon,
                        );
                        var angleFix;
                        var currentIcon;

                        if (photo.azimuth) {
                            var geodesicEndPoint = Math.calculateMapLineEndPoint(
                                photo.azimuth, currentPosition, 2000,
                            );
                            var angle = Math.getAzimuthBetweenTwoPoints(
                                currentPosition, geodesicEndPoint,
                            );
                            angleFix = photo.azimuth - angle;
                            arrowIcon.rotation = photo.azimuth + angleFix;
                            currentIcon = $.extend(
                                true,
                                arrowIcon,
                                {
                                    rotation: photo.azimuth + angleFix,
                                },
                            );
                        } else {
                            currentIcon = $.extend(true, {}, locationIcon);
                        }
                        currentIcon.fillColor = photo.rephoto_count ? '#007fff' : 'black';
                        var marker = new google.maps.Marker({
                            icon: currentIcon,
                            position: currentPosition,
                            zIndex: 1,
                            angleFix: angleFix,
                            map: null,
                            anchor: new google.maps.Point(0.0, 0.0),
                            photoData: photo,
                        });
                        if (angleFix)
                            window.lastMarkerSet.push(photo.id);

                        (function(marker) {
                            google.maps.event.addListener(marker, 'click', function() {
                                highlightSelected(marker, true);
                            });
                        })(marker);

                        markers.push(marker);
                    }
                }
                if (mc && mc.clusters_) {
                    mc.clusters_.length = 0;
                }
                if (mc) {
                    google.maps.event.clearListeners(mc, 'clusteringend');
                }
                mc = new MarkerClusterer(
                    window.map,
                    markers,
                    $.extend(
                        true,
                        markerClustererSettings,
                        { gridSize: response.photos.length <= 50 ? 0.0000001 : 60 },
                    ),
                );
                google.maps.event.addListener(mc, 'clusteringend', function() {
                    if (photosOnSidePanel.length !== 0) {
                        return;
                    }
                    if (map.zoom > markerClustererSettings.maxZoom) {
                        photosOnSidePanel = markers.map(
                            function(marker) {
                                return marker.photoData;
                            },
                        );
                    } else {
                        // Filtering only single photos(outside of clusters) to
                        // show on side panel.
                        var clusters = mc.clusters_;
                        for (var i = 0; i < clusters.length; i++) {
                            var clusterMarkers = clusters[i].markers_;
                            if (clusterMarkers.length === 1) {
                                photosOnSidePanel.push(clusterMarkers[0].photoData);
                            }
                        }
                    }
                    var imgWrapper = document.getElementById('img-wrapper');
                    var fc = imgWrapper.firstChild;

                    while (fc) {
                        imgWrapper.removeChild(fc);
                        fc = imgWrapper.firstChild;
                    }
                    current_bunch = 1;
                    refreshPane(photosOnSidePanel.slice(0, sidePanelPhotosBunchSize));
                });
            });
        }
    };


    function loadMoreImages() {
        refreshPane(photosOnSidePanel.slice(
            current_bunch * sidePanelPhotosBunchSize,
            (current_bunch + 1) * sidePanelPhotosBunchSize,
        ));
        current_bunch++;
    }

    window.checkLoadedSidePanelPhotos = function() {
        var photos_count = $('#img-wrapper .side-panel-photo').length;
        window.morePhotosCanBeLoaded = photos_count <= ++loadedPhotosCount && photos_count < photosOnSidePanel.length;
    };

    function refreshPane(photosToAdd) {
        $('#img-wrapper').append(
            tmpl('ajp-map-view-side-panel-element-template', photosToAdd),
        );
        window.morePhotosCanBeLoaded = photosToAdd.length !== 0;
    }


    window.deselectMarker = function() {
        currentlySelectedMarker = null;
        window.currentlySelectedRephotoId = null;
        window.currentlySelectedSimilarPhotoId = null;
        $('#img-wrapper').find('img').removeClass('highlighted-image');
        if (lastHighlightedMarker) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        window.dottedAzimuthLine.setVisible(false);
        window.syncMapStateToURL();
    };


    var highlightSelected = function(marker, fromMarker, event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        if (!window.isSidePanelOpen) {
            window.toggleSidePanel();
        }
        targetPaneElement = $('#element' + marker.photoData.id);
        window.loadPhoto(marker.photoData.id);
        if (!targetPaneElement.length) {
            refreshPane([marker.photoData]);
            targetPaneElement = $('#element' + marker.photoData.id);
        }
        currentlySelectedMarker = marker;
        window.syncMapStateToURL();
        const imageWrapper = $('#img-wrapper');
        imageWrapper.find('img').removeClass('highlighted-image');
        targetPaneElement.find('img').addClass('highlighted-image');
        if (!fromMarker) {
            window.gtag('event', 'photo_pane_click', { 'category': 'Map' });
        }
        if (lastSelectedMarkerId && lastHighlightedMarker) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        lastSelectedMarkerId = marker.photoData.id;
        for (var i = 0; i < markers.length; i += 1) {
            if (markers[i].photoData.id === marker.photoData.id) {
                targetPaneElement.find('img').attr('src', markers[i].thumb);
                markers[i].setZIndex(maxIndex);
                maxIndex += 1;
                if (markers[i].photoData.azimuth) {
                    window.dottedAzimuthLine.setPath([
                        markers[i].position,
                        Math.simpleCalculateMapLineEndPoint(
                            markers[i].photoData.azimuth,
                            markers[i].position,
                            0.02,
                        ),
                    ]);
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
        lastHighlightedMarker = marker;
        if (targetPaneElement.length) {
            if (window.innerWidth > 768) {
                // Calculating scroll value to place photo in middle of screen.
                let scrollValue = imageWrapper.scrollTop() + (
                    targetPaneElement.position().top - (
                        imageWrapper.height() / 2 - targetPaneElement.height() / 2
                    )
                );
                imageWrapper.animate({ scrollTop: scrollValue }, 800);
            } else {
                let scrollValue = imageWrapper.scrollLeft() + (
                    targetPaneElement.position().left - (
                        imageWrapper.width() / 2 - targetPaneElement.width() / 2
                    )
                );
                imageWrapper.animate({ scrollLeft: scrollValue }, 800);
            }
            window.gtag('event', 'marker_click', { 'category': 'Map' });
        }
        return false;
    };


    window.handleAlbumChange = function(id) {
        window.albumId = id;
        window.location.href = '/map?album=' + id;
    };

    var setCorrectMarkerIcon = function(marker) {
        if (marker) {
            if (marker.photoData.id == (currentlySelectedMarker && currentlySelectedMarker.photoData.id)) {
                if (marker.photoData.azimuth) {
                    arrowIcon.scale = 1.5;
                    arrowIcon.strokeWeight = 2;
                    arrowIcon.fillColor = 'white';
                    arrowIcon.rotation = marker.photoData.azimuth + marker.angleFix;
                    if (marker.photoData.rephoto_count) {
                        arrowIcon.strokeColor = '#007fff';
                    } else {
                        arrowIcon.strokeColor = 'black';
                    }
                    marker.setIcon(arrowIcon);
                } else {
                    locationIcon.scale = 1.5;
                    locationIcon.strokeWeight = 2;
                    locationIcon.fillColor = 'white';
                    locationIcon.anchor = new google.maps.Point(12, 6);
                    if (marker.photoData.rephoto_count) {
                        locationIcon.strokeColor = '#007fff';
                    } else {
                        locationIcon.strokeColor = 'black';
                    }
                    marker.setIcon(locationIcon);
                }
            } else {
                if (marker.photoData.azimuth) {
                    arrowIcon.scale = 1.0;
                    arrowIcon.strokeWeight = 1;
                    arrowIcon.strokeColor = 'white';
                    arrowIcon.rotation = marker.photoData.azimuth + marker.angleFix;
                    if (marker.photoData.rephoto_count) {
                        arrowIcon.fillColor = '#007fff';
                    } else {
                        arrowIcon.fillColor = 'black';
                    }
                    marker.setIcon(arrowIcon);
                } else {
                    locationIcon.scale = 1.0;
                    locationIcon.strokeWeight = 1;
                    locationIcon.strokeColor = 'white';
                    locationIcon.anchor = new google.maps.Point(12, 0);
                    if (marker.photoData.rephoto_count) {
                        locationIcon.fillColor = '#007fff';
                    } else {
                        locationIcon.fillColor = 'black';
                    }
                    marker.setIcon(locationIcon);
                }
            }
        }
    };


    window.initializeMapStateFromOptionalURLParameters = function() {
        var urlMapType = window.getQueryParameterByName('mapType');
        if (window.preselectPhotoId) {
            // There's a selected photo specified in the URL, select when ready
            currentlySelectedMarker = findMarkerByPhotoId(window.preselectPhotoId);
            if (window.preselectPhotoLat && window.preselectPhotoLng) {
                currentlySelectedMarker = findMarkerByPhotoId(window.preselectPhotoId);
            }
        }
        if (window.getQueryParameterByName('lat') && window.getQueryParameterByName('lng') && window.getQueryParameterByName('zoom')) {
            // User has very specific parameters, allow to take precedence
            window.getMap(new google.maps.LatLng(window.getQueryParameterByName('lat'), window.getQueryParameterByName('lng')),
                parseInt(window.getQueryParameterByName('zoom'), 10), false, urlMapType);
        } else {
            if (window.preselectPhotoLat && window.preselectPhotoLng) {
                // We know the location of the photo, let's build the map accordingly
                window.getMap(new google.maps.LatLng(window.preselectPhotoLat, window.preselectPhotoLng), 18, false, urlMapType);
            } else if (window.albumLatLng) {
                // There's nothing preselected, but we do know the album the photo's in
                window.getMap(this.albumLatLng, 16, false, urlMapType);
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


    var activateAlbumFilter = function(showMessage = false) {
        limitByAlbum = true;
        $('#ajp-header-album-filter-button-off').hide();
        $('#ajp-header-album-filter-button-on').show();
        $('#ajp-header-album-filter-button').prop('title', window.gettext('Remove album filter'));
        if (showMessage) {
            var albumFilterMessage = interpolate(
                gettext('Pictures only in album: %(albumName)s are shown in the sidebar'),
                {
                    'albumName': $('#ajp-header-title').clone().children().remove().end().text().trim(),
                },
                true,
            );
            $.notify(albumFilterMessage, { type: 'info', placement: { from: 'top', align: 'left' } });
        }
    };


    var deactivateAlbumFilter = function(showMessage = false) {
        limitByAlbum = false;
        $('#ajp-header-album-filter-button-off').show();
        $('#ajp-header-album-filter-button-on').hide();
        $('#ajp-header-album-filter-button').prop('title', window.gettext('Apply album filter'));
        if (showMessage) {
            $.notify(gettext('All pictures are shown in the sidebar'), {
                type: 'info',
                placement: { from: 'top', align: 'left' },
            });
        }
    };


    $(document).ready(function() {
        window.updateLeaderboard();
        window.isMapview = true;
        $(window.input).show();
        $('#ajp-game-description-viewing-warning').hide();
        $('#ajp-header-album-filter-button').click(function() {
            if (!limitByAlbum) {
                activateAlbumFilter(true);
            } else {
                deactivateAlbumFilter(true);
            }
            window.toggleVisiblePaneElements();
            window.syncMapStateToURL();
        });
        if (window.preselectPhotoId) {
            currentlySelectedMarker = findMarkerByPhotoId(window.preselectPhotoId);
        }
        window.initializeMapStateFromOptionalURLParameters();
        $(document).on('hidden.bs.modal', '#ajp-photo-modal', function() {
            window.currentlySelectedRephotoId = false;
            photoDrawerOpen = false;
            window.syncMapStateToURL();
        });
        $(document).on('click', '#ajp-mapview-my-location-button', function() {
            window.getGeolocation(window.handleGeolocation);
            centerOnMapAfterLocating = true;
            window.map.setZoom(16);
        });
        window.handleGeolocation = function(location) {
            $('#ajp-geolocation-error').hide();
            if (centerOnMapAfterLocating) {
                window.map.setCenter(new google.maps.LatLng(location.coords.latitude, location.coords.longitude));
                centerOnMapAfterLocating = false;
            }
        };
        $('#logout-button').click(function() {
            window.gtag('event', 'logout', { 'category': 'Map' });
        });
        if (window.map !== undefined) {
            window.map.scrollwheel = true;
            window.mapMapviewClickListener = google.maps.event.addListener(window.map, 'click', function() {
                window.deselectMarker();
            });
        }
        $(document).on('click', '.sidepanel-photo', function(e) {
            e.preventDefault();
            e.stopPropagation();
        });

        window.toggleSidePanel = function() {
            if (window.innerWidth > 768) {
                let sidePanelWidth = 0;
                if (!window.isSidePanelOpen) {
                    sidePanelWidth = window.innerWidth / 4;
                    if (sidePanelWidth < 200) {
                        sidePanelWidth = 200;
                    }
                }
                document.getElementById('map-side-panel').style.width = sidePanelWidth + 'px';
                document.getElementById('map-side-panel').style.height = 'calc(100vh - 60px)';
                document.getElementById('img-wrapper').style.width = sidePanelWidth + 'px';
                document.getElementById('img-wrapper').style.height = 'calc(100vh - 60px)';
                document.getElementById('close-btn').style.left = sidePanelWidth + 'px';
                document.getElementById('close-btn').style.bottom = '';
            } else {
                let sidePanelHeight = 0;
                if (!window.isSidePanelOpen) {
                    sidePanelHeight = window.innerHeight / 4;
                    if (sidePanelHeight < 200) {
                        sidePanelHeight = 200;
                    }
                }
                document.getElementById('map-side-panel').style.height = sidePanelHeight + 'px';
                document.getElementById('map-side-panel').style.width = window.isSidePanelOpen ? 'inherit' : '100vw';
                document.getElementById('img-wrapper').style.height = sidePanelHeight + 'px';
                document.getElementById('img-wrapper').style.width = window.isSidePanelOpen ? 'inherit' : '100vw';
                document.getElementById('close-btn').style.bottom = sidePanelHeight + 'px';
                document.getElementById('close-btn').style.left = '';
            }
            document.getElementById('map-side-panel').style.opacity = window.isSidePanelOpen ? 0 : 1;
            document.getElementById('close-btn').style.opacity = window.isSidePanelOpen ? 0 : 0.5;
            document.getElementById('open-btn').style.display = window.isSidePanelOpen ? '' : 'none';
            document.getElementById('open-btn').style.opacity = window.isSidePanelOpen ? 0.5 : 0;
            window.isSidePanelOpen = !window.isSidePanelOpen;
        };

        if (!window.isMobile) {
            toggleSidePanel();
        }

        $(window).on('resize', function() {
            let resizeTimer;
            document.body.classList.add('resize-animation-stopper');
            clearTimeout(resizeTimer);
            setTimeout(() => {
                document.body.classList.remove('resize-animation-stopper');
            }, 400);
            if (window.innerWidth > 768) {
                document.getElementById('close-btn').style.bottom = '';
                let sidePanelWidth = window.isSidePanelOpen ? window.innerWidth / 4 : 0;
                if (window.isSidePanelOpen && sidePanelWidth < 200) {
                    sidePanelWidth = 200;
                }
                document.getElementById('map-side-panel').style.width = sidePanelWidth + 'px';
                document.getElementById('map-side-panel').style.height = 'calc(100vh - 60px)';
                document.getElementById('img-wrapper').style.width = sidePanelWidth + 'px';
                document.getElementById('img-wrapper').style.height = 'calc(100vh - 60px)';
                document.getElementById('close-btn').style.left = sidePanelWidth + 'px';
                document.getElementById('close-btn').style.bottom = '';
            } else {
                document.getElementById('close-btn').style.left = '';
                let sidePanelHeight = window.isSidePanelOpen ? window.innerHeight / 4 : 0;
                if (window.isSidePanelOpen && sidePanelHeight < 200) {
                    sidePanelHeight = 200;
                }
                document.getElementById('close-btn').style.bottom = sidePanelHeight + 'px';
                document.getElementById('map-side-panel').style.height = sidePanelHeight + 'px';
                document.getElementById('map-side-panel').style.width = '100vw';
                document.getElementById('img-wrapper').style.height = sidePanelHeight + 'px';
                document.getElementById('img-wrapper').style.width = '100vw';
            }
        });

        $('#img-wrapper').on('click', 'img', function(event) {
            var photoId = $(event.target).data('id');
            highlightSelected(findMarkerByPhotoId(photoId));
        });

        $('#img-wrapper').on('scroll', function() {
            if (window.innerWidth < 769 && ($('#img-wrapper')[0].scrollWidth - $('#img-wrapper')[0].scrollLeft - 20) < $('#img-wrapper')[0].clientWidth) {
                if (!!window.morePhotosCanBeLoaded) {
                    loadMoreImages();
                }
            } else if (window.innerWidth > 768 && ($('#img-wrapper')[0].scrollHeight - $('#img-wrapper')[0].scrollTop - 20) < $('#img-wrapper')[0].clientHeight) {
                if (!!window.morePhotosCanBeLoaded) {
                    loadMoreImages();
                }
            }
        });

        //TODO: There has to be a better way
        window.paneImageHoverIn = function(e) {
            var myParent = $(e).parent();
            myParent.find('.ajp-thumbnail-selection-icon').show('fade', 250);
        };
        window.paneImageHoverOut = function(e) {
            var myParent = $(e).parent(),
                icon = myParent.find('.ajp-thumbnail-selection-icon');
            if (!icon.hasClass('ajp-thumbnail-selection-icon-blue')) {
                myParent.find('.ajp-thumbnail-selection-icon').hide();
            }
        };
    });
}());