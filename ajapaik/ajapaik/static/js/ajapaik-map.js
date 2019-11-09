(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global docCookies*/
    /*global moment*/
    /*global _gaq*/
    /*global $*/
    /*global google*/
    /*global commonVgmapi*/

    var arrowIcon = {
        path: 'M12 2l-7.5 18.29.71.71 6.79-3 6.79 3 .71-.71z',
        strokeColor: 'white',
        strokeOpacity: 1,
        strokeWeight: 1,
        fillColor: 'black',
        fillOpacity: 1,
        rotation: 0,
        scale: 1.0,
        anchor: new google.maps.Point(12, 12)
    };

    var locationIcon = {
        path: 'M12 2c-3.87 0-7 3.13-7 7 0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
        strokeColor: 'white',
        strokeOpacity: 1,
        strokeWeight: 1,
        fillColor: 'black',
        fillOpacity: 1,
        scale: 1.0,
        anchor: new google.maps.Point(12, 0)
    };

    // Variables
    var photoId,
        limitByAlbum,
        lastHighlightedMarker,
        photosOnSidePanel = [],
        currentlySelectedMarker,
        photoDrawerOpen = false,
        markers = [],
        centerOnMapAfterLocating = false,
        markerClustererSettings = {
            minimumClusterSize: 2,
            maxZoom: 17
        },
        isSidePanelOpen = false,
        lastSelectedPaneElement,
        lastSelectedMarkerId,
        loadedPhotosCount = 0,
        targetPaneElement,
        maxIndex = 2,
        mc,
        currentMapDataRequest,
        limitByAlbum,
        temporalMapFilterTimeout;

    document.getElementById("map-side-panel").style.opacity = 0;
    window.userClosedRephotoTools = false;
    window.userClosedSimilarPhotoTools = true;

    function findMarkerByPhotoId(photoId) {
        return markers.find(function (marker) {
            return marker.photoData.id === photoId;
        });
    };

    var sidePanelPhotosBunchSize = 20;

    window.loadPhoto = function (id) {
        photoId = id;
        $.ajax({
            cache: false,
            url: '/photo/' + id + '/?isMapview=1',
            success: function (result) {
                openPhotoDrawer(result);
                var mainPhotoContainer = $('#ajapaik-modal-photo-container'),
                    rephotoColumn = $('#ajapaik-photo-modal-rephoto-column'),
                    rephotoContainer = $('#ajapaik-modal-rephoto-container'),
                    similarPhotoColumn = $('#ajapaik-photo-modal-similar-photo-column'),
                    similarPhotoContainer = $('#ajapaik-modal-similar-photo-container');
                if (window.photoHistory && window.photoHistory.length > 0) {
                    $('.ajapaik-photo-modal-previous-button').removeClass('disabled');
                }
                if (window.userClosedRephotoTools) {
                    $('#ajapaik-rephoto-selection').hide();
                    rephotoColumn.hide();
                    $('#ajapaik-photo-modal-rephoto-info-column').hide();
                }
                if (window.userClosedSimilarPhotoTools) {
                    $('#ajapaik-similar-photo-selection').hide();
                    similarPhotoColumn.hide();
                    $('#ajapaik-photo-modal-similar-photo-info-column').hide();
                }
                if (window.photoModalRephotoArray && window.photoModalRephotoArray[0] && window.photoModalRephotoArray[0][2] !== 'None' && window.photoModalRephotoArray[0][2] !== '') {
                    $('#ajapaik-photo-modal-date-row').show();
                }
                mainPhotoContainer.hover(function () {
                    if (!window.isMobile) {
                        $(this).find('.ajapaik-thumbnail-selection-icon').show("fade", 250);
                        $('.ajapaik-flip-photo-overlay-button').show("fade", 250);
                        if (window.userClosedSimilarPhotoTools) {
                            $('.ajapaik-show-similar-photo-selection-overlay-button').show("fade", 250);
                        }
                        if (window.userClosedRephotoTools) {
                            $('.ajapaik-show-rephoto-selection-overlay-button').show("fade", 250);
                        }
                    }
                }, function () {
                    if (!window.isMobile) {
                        $(this).find('.ajapaik-thumbnail-selection-icon').hide("fade", 250);
                        $('.ajapaik-flip-photo-overlay-button').hide("fade", 250);
                        $('.ajapaik-show-similar-photo-selection-overlay-button').hide("fade", 250);
                        $('.ajapaik-show-rephoto-selection-overlay-button').hide("fade", 250);
                    }
                });
                rephotoContainer.hover(function () {
                    if (!window.isMobile) {
                        if (!window.userClosedRephotoTools) {
                            $('.ajapaik-close-rephoto-overlay-button').show("fade", 250);
                            $('.ajapaik-invert-rephoto-overlay-button').show("fade", 250);
                            $('#ajapaik-rephoto-selection').show();
                        }
                    }
                }, function () {
                    if (!window.isMobile) {
                        if (!window.userClosedRephotoTools) {
                            $('.ajapaik-close-rephoto-overlay-button').hide("fade", 250);
                            $('.ajapaik-invert-rephoto-overlay-button').hide("fade", 250);
                            $('#ajapaik-rephoto-selection').hide();
                        }
                    }
                });
                similarPhotoContainer.hover(function () {
                    if (!window.isMobile) {
                        if (!window.userClosedSimilarPhotoTools) {
                            $('.ajapaik-close-similar-photo-overlay-button').show("fade", 250);
                            $('.ajapaik-invert-similar-photo-overlay-button').show("fade", 250);
                            $('#ajapaik-similar-photo-selection').show();
                        }
                    }
                }, function () {
                    if (!window.isMobile) {
                        if (!window.userClosedSimilarPhotoTools) {
                            $('.ajapaik-close-similar-photo-overlay-button').hide("fade", 250);
                            $('.ajapaik-invert-similar-photo-overlay-button').hide("fade", 250);
                            $('#ajapaik-similar-photo-selection').hide();
                        }
                    }
                });
                window.showPhotoMapIfApplicable();
            }
        });
    };


    var openPhotoDrawer = function (content) {
        var target = $('#ajapaik-photo-modal');
        photoDrawerOpen = true;
        window.syncMapStateToURL();
        var fullScreenImage = $('#ajapaik-full-screen-image'),
            rephotoFullScreenImage = $('#ajapaik-rephoto-full-screen-image'),
            similarFullScreenImage = $('#ajapaik-similar-photo-full-screen-image');
        target.html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
            fullScreenImage.attr('data-src', window.photoModalFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
            rephotoFullScreenImage.attr('data-src', window.photoModalRephotoFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
            similarFullScreenImage.attr('data-src', window.photoModalSimilarFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
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

    window.syncMapStateToURL = function () {
        // FIXME: Do this more elegantly
        var historyReplacementString = '/map/';
        if(window && window.location && window.location.pathname.search("map-tablet") > -1){
            var historyReplacementString = '/map-tablet/';
        }
        if (currentlySelectedMarker) {
            historyReplacementString += 'photo/' + currentlySelectedMarker.photoData.id + '/';
        }
        if (window.currentlySelectedRephotoId) {
            historyReplacementString += 'rephoto/' + window.currentlySelectedRephotoId + '/';
        }
        if (window.albumId) {
            historyReplacementString += '?album=' + window.albumId;
        }

        if (window.map) {
            var typeId = window.map.getMapTypeId();
            historyReplacementString += '&mapType=' + typeId;
            historyReplacementString += '&lat=' + window.map.getCenter().lat();
            historyReplacementString += '&lng=' + window.map.getCenter().lng();
            historyReplacementString += '&zoom=' + window.map.zoom;
            if (typeId === 'old-maps') {
                historyReplacementString += '&maps-city=' + commonVgmapi.vars.site;
                historyReplacementString += '&maps-index=' + commonVgmapi.vars.layerIndex;
            }
            if (typeId === 'old-helsinki') {
                historyReplacementString += '&maps-index=' + commonVgmapi.vars.layerIndex;
            }
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
                thumbSrc: '/photo-thumb/' + photoId + '/400/',
                photoFlipped: window.photoModalCurrentPhotoFlipped,
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
        $('#ajapaik-photo-modal').modal('hide');
        photoDrawerOpen = false;
        window.syncMapStateToURL();
    };


    window.uploadCompleted = function (response) {
        $('#ajapaik-rephoto-upload-modal').modal('hide');
        if (response && response.new_id) {
            window.currentlySelectedRephotoId = response.new_id;
            window.syncMapStateToURL();
            window.location.reload();
        }
    };

    $('.load-more-button').on('click', function (event) {
        var current_bunch = $(event.target).data('bunch-loaded');
        refreshPane(photosOnSidePanel.slice(
            current_bunch * sidePanelPhotosBunchSize,
            (current_bunch + 1) * sidePanelPhotosBunchSize
        ));
        $(event.target).data('bunch-loaded', ++current_bunch)
    });

    window.deselectMarker = function () {
        currentlySelectedMarker = null;
        window.currentlySelectedRephotoId = null;
        window.currentlySelectedSimilarPhotoId = null;
        $('#img-wrapper').find('img').addClass("opaque-image");
        if (lastHighlightedMarker) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        window.dottedAzimuthLine.setVisible(false);
        window.syncMapStateToURL();
    };

    window.handleAlbumChange = function () {
        if (window.albumId) {
            window.location.href = '/map?album=' + window.albumId;
        }
    };


    window.flipPhoto = function () {
        var fullScreenPhoto = $('#ajapaik-full-screen-image');
        if (fullScreenPhoto.hasClass('ajapaik-photo-flipped')) {
            fullScreenPhoto.removeClass('ajapaik-photo-flipped');
        } else {
            fullScreenPhoto.addClass('ajapaik-photo-flipped');
        }
        window.photoModalCurrentPhotoFlipped = !window.photoModalCurrentPhotoFlipped;
    };


    var setCorrectMarkerIcon = function (marker) {
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


    window.initializeMapStateFromOptionalURLParameters = function () {
        var urlMapType = window.getQueryParameterByName('mapType');
        if(this.isTabletView && urlMapType === 'old-maps'){
            urlMapType = 'old-helsinki';
        }
        if(!this.isTabletView && urlMapType === 'old-helsinki'){
            urlMapType = 'old-maps';
        }
        // FIXME: What is fromSelect?
        if (window.getQueryParameterByName('fromSelect')) {
            if (window.albumLatLng) {
                window.getMap(window.albumLatLng, 16, false, urlMapType);
            } else if (window.areaLatLng) {
                window.getMap(window.areaLatLng, 16, false, urlMapType);
            }
        } else {
            if (window.preselectPhotoId) {
                // There's a selected photo specified in the URL, select when ready
                currentlySelectedMarker = findMarkerByPhotoId(window.preselectPhotoId);
                if (window.preselectPhotoLat && window.preselectPhotoLat) {
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


    var activateAlbumFilter = function () {
        limitByAlbum = true;
        $('#ajapaik-header-album-filter-button-off').hide();
        $('#ajapaik-header-album-filter-button-on').show();
        $('#ajapaik-header-album-filter-button').prop('title', window.gettext('Remove album filter'));
    };


    var deactivateAlbumFilter = function () {
        limitByAlbum = false;
        $('#ajapaik-header-album-filter-button-off').show();
        $('#ajapaik-header-album-filter-button-on').hide();
        $('#ajapaik-header-album-filter-button').prop('title', window.gettext('Apply album filter'));
    };


    $(document).ready(function () {
        window.updateLeaderboard();
        window.isMapview = true;
        $(window.input).show();
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
            currentlySelectedMarker = findMarkerByPhotoId(window.preselectPhotoId);
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
            window.map.setZoom(16);
        });
        window.handleGeolocation = function (location) {
            $('#ajapaik-geolocation-error').hide();
            if (centerOnMapAfterLocating) {
                window.map.setCenter(new google.maps.LatLng(location.coords.latitude, location.coords.longitude));
                centerOnMapAfterLocating = false;
            }
        };
        $('#logout-button').click(function () {
            window._gaq.push(['_trackEvent', 'Map', 'Logout']);
        });
        if (window.map !== undefined) {
            window.map.scrollwheel = true;
            window.mapMapviewClickListener = google.maps.event.addListener(window.map, 'click', function () {
                window.deselectMarker();
            });
        }
    });

    function manipulateElements(isClose=false) {
        if(window.innerWidth > 768) {
            let sidePanelWidth = 0
            if(!isClose){
                sidePanelWidth = window.innerWidth / 4;
                if(sidePanelWidth < 200) {
                    sidePanelWidth = 200
                }
            }
            document.getElementById("map-side-panel").style.width = sidePanelWidth + "px";
            document.getElementById("map-side-panel").style.height = "calc(100vh - 60px)";
            document.getElementById("img-wrapper").style.width = sidePanelWidth + "px";
            document.getElementById("img-wrapper").style.height = "calc(100vh - 60px)";
            document.getElementById("close-btn").style.left = sidePanelWidth + "px";
            document.getElementById("close-btn").style.bottom = "";
        } else {
            let sidePanelHeight = 0
            if(!isClose){
                sidePanelHeight = window.innerHeight / 4;
                if(sidePanelHeight < 200) {
                    sidePanelHeight = 200
                }
            }
            document.getElementById("map-side-panel").style.height = sidePanelHeight + "px";
            document.getElementById("map-side-panel").style.width = isClose ? "inherit" : "100vw";
            document.getElementById("img-wrapper").style.height = sidePanelHeight + "px";
            document.getElementById("img-wrapper").style.width = isClose ? "inherit" : "100vw";
            document.getElementById("close-btn").style.bottom = sidePanelHeight + "px";
            document.getElementById("close-btn").style.left = "";
        }
        document.getElementById("map-side-panel").style.opacity = isClose ? 0 : 1;
        document.getElementById("close-btn").style.opacity = isClose ? 0 : 0.5;
        document.getElementById("open-btn").style.opacity = isClose ? 0.5 : 0;
    };
    
    window.openNav = function()  {
        manipulateElements();
        isSidePanelOpen = true;
    };
    
    window.closeNav = function() {
        manipulateElements(true);
        isSidePanelOpen = false;
    };
    
    var highlightSelected = function (marker, fromMarker, event) {
        if (!isSidePanelOpen) {
            window.openNav();
        }
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        targetPaneElement = $('#element' + marker.photoData.id);
        if ((currentlySelectedMarker && currentlySelectedMarker.photoData.id) == marker.photoData.id) {
            window.loadPhoto(marker.photoData.id);
            return;
        }
        if (!targetPaneElement.length) {
            refreshPane([marker.photoData]);
            targetPaneElement = $('#element' + marker.photoData.id);
        }
        currentlySelectedMarker = marker;
        window.syncMapStateToURL();
        $('#img-wrapper').find('img').addClass('opaque-image');
        targetPaneElement.find('img').removeClass('opaque-image');
        if (!fromMarker) {
            window._gaq.push(['_trackEvent', 'Map', 'Pane photo click']);
        }
        if (lastSelectedPaneElement) {
            lastSelectedPaneElement.find('.ajapaik-azimuth').hide();
        }
        if (lastSelectedMarkerId && lastHighlightedMarker) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        lastSelectedMarkerId = marker.photoData.id;
        lastSelectedPaneElement = targetPaneElement;
        for (var i = 0; i < markers.length; i += 1) {
            if (markers[i].photoData.id == marker.photoData.id) {
                targetPaneElement.find('img').attr('src', markers[i].thumb);
                targetPaneElement.find('.ajapaik-azimuth').show();
                markers[i].setZIndex(maxIndex);
                maxIndex += 1;
                if (markers[i].photoData.azimuth) {
                    window.dottedAzimuthLine.setPath([
                        markers[i].position,
                        Math.simpleCalculateMapLineEndPoint(
                            markers[i].photoData.azimuth,
                            markers[i].position,
                            0.02
                        )
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
        if (fromMarker && targetPaneElement.length) {
            var scrollElement = $('#img-wrapper');

            if(window.innerWidth > 768) {
                var currentScrollValue = scrollElement.scrollTop();
                // Calculating scroll value to place photo in middle of screen.
                var scrollValue = currentScrollValue + (
                    targetPaneElement.position().top - (
                        scrollElement.height() / 2 - targetPaneElement.height() / 2
                    )
                );
                scrollElement.animate({scrollTop: scrollValue}, 800);
            }
            else{
                var currentScrollValue = scrollElement.scrollLeft();
                var scrollValue = currentScrollValue + (
                    targetPaneElement.position().left - (
                        scrollElement.width() / 2 - targetPaneElement.width() / 2
                    )
                );
                scrollElement.animate({scrollLeft: scrollValue}, 800);
            }
            window._gaq.push(['_trackEvent', 'Map', 'Marker click']);
        }
        return false;
    };
    
    var updateBoundingEdge = function (edge) {
        var scale = Math.pow(2, window.map.getZoom()),
            projection = window.map.getProjection(),
            edgePixelCoordinates = projection.fromLatLngToPoint(edge),
            currentPaneWidth = $('#ajapaik-mapview-photo-panel').width();
        if (!currentPaneWidth) {
            currentPaneWidth = $(window).width() / 5;
        }
        edgePixelCoordinates.x = (edgePixelCoordinates.x * scale + currentPaneWidth + 20) / scale;
        return projection.fromPointToLatLng(edgePixelCoordinates);
    };
    
    window.doDelayedTemporalFiltering = function () {
        if (temporalMapFilterTimeout) {
            clearTimeout(temporalMapFilterTimeout);
        }
        temporalMapFilterTimeout = setTimeout(function () {
            window.toggleVisiblePaneElements();
            _gaq.push(['_trackEvent', 'Mapview', 'Filter by date']);
        }, 500);
    };
    
    $(window).on('resize', function() {
        let resizeTimer;
        document.body.classList.add("resize-animation-stopper");
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            document.body.classList.remove("resize-animation-stopper");
        }, 400);
        if(window.innerWidth <= 768) {
            document.getElementById("close-btn").style.left = "";
            let sidePanelHeight = isSidePanelOpen ? window.innerHeight / 4 : 0;
            if(isSidePanelOpen && sidePanelHeight < 200) {
                sidePanelHeight = 200
            }
            document.getElementById("close-btn").style.bottom = sidePanelHeight + "px";
            document.getElementById("map-side-panel").style.height = sidePanelHeight + "px";
            document.getElementById("map-side-panel").style.width = "100vw";
            document.getElementById("img-wrapper").style.height = sidePanelHeight + "px";
            document.getElementById("img-wrapper").style.width = "100vw";
        }
        else  {
            document.getElementById("close-btn").style.bottom = "";
            let sidePanelWidth = isSidePanelOpen ? window.innerWidth / 4 : 0;
            if(isSidePanelOpen && sidePanelWidth < 200) {
                sidePanelWidth = 200
            }
            document.getElementById("map-side-panel").style.width = sidePanelWidth + "px";
            document.getElementById("map-side-panel").style.height = "calc(100vh - 60px)";
            document.getElementById("img-wrapper").style.width = sidePanelWidth + "px";
            document.getElementById("img-wrapper").style.height = "calc(100vh - 60px)";
            document.getElementById("close-btn").style.left = sidePanelWidth + "px";
            document.getElementById("close-btn").style.bottom = "";
        }
    });

    window.toggleVisiblePaneElements = function () {
        if (window.map && !window.guessLocationStarted) {
            if (!window.comingBackFromGuessLocation) {
                window.deselectMarker();
            } else {
                window.comingBackFromGuessLocation = false;
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
            var payload = {
                album: window.albumId,
                limit_by_album: limitByAlbum,
                sw_lat: sw.lat(),
                sw_lon: sw.lng(),
                ne_lat: ne.lat(),
                ne_lon: ne.lng(),
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            };
            if (window.map.zoom <= markerClustererSettings.maxZoom) {
                payload.count_limit = 1000;
            }
            currentMapDataRequest = $.post(window.mapDataURL, payload, function (response) {
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
                            photo.lon
                        );
                        var angleFix;
                        var currentIcon;
    
                        if (photo.azimuth) {
                            var geodesicEndPoint = Math.calculateMapLineEndPoint(
                                photo.azimuth, currentPosition, 2000
                            );
                            var angle = Math.getAzimuthBetweenTwoPoints(
                                currentPosition, geodesicEndPoint
                            );
                            angleFix = photo.azimuth - angle;
                            arrowIcon.rotation = photo.azimuth + angleFix;
                            currentIcon = $.extend(
                                true,
                                arrowIcon,
                                {
                                    rotation: photo.azimuth + angleFix
                                }
                            )
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
                            photoData: photo
                        });
                        if (angleFix)
                            window.lastMarkerSet.push(photo.id);
    
                        (function (marker) {
                            google.maps.event.addListener(marker, 'click', function () {
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
                        {gridSize: response.photos.length <= 50 ? 0.0000001 : 60}
                    )
                );
                google.maps.event.addListener(mc, 'clusteringend', function () {
                    if (photosOnSidePanel.length != 0) {
                        return;
                    }
                    if (map.zoom > markerClustererSettings.maxZoom) {
                        photosOnSidePanel = markers.map(
                            function (marker) {
                                return marker.photoData
                            }
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
                    $('#img-wrapper').empty();
                    refreshPane(photosOnSidePanel.slice(0, sidePanelPhotosBunchSize));
                });
            });
        }
    };
    
    window.checkLoadedSidePanelPhotos = function (element) {
        var photos_count = $('#map-side-panel .img-wrapper').length;
        if (photos_count <= ++loadedPhotosCount) {
            if (photos_count >= photosOnSidePanel.length) {
                $('.load-more button').hide();
            } else {
                $('.load-more button').show();
            }
        }
    };
    
    function refreshPane(photosToAdd) {
        var targetDiv = $('#img-wrapper');
        targetDiv.append(
            tmpl('ajapaik-map-view-side-panel-element-template', photosToAdd)
        );
        $('#img-wrapper').on('click', 'img', function (event) {
            var photoId = $(event.target).data('id');
            highlightSelected(findMarkerByPhotoId(photoId));
        });
        if (photosToAdd.length == 0) {
            $('#ajapaik-map-container .ajapaik-load-more button').hide();
            $('#ajapaik-map-container .ajapaik-load-more .ajapaik-spinner').hide();
        } else {
            $('#ajapaik-map-container .ajapaik-load-more button').hide();
            $('#ajapaik-map-container .ajapaik-load-more .ajapaik-spinner').show();
        }
    };

    //TODO: There has to be a better way
    window.paneImageHoverIn = function (e) {
        var myParent = $(e).parent();
        myParent.find('.ajapaik-azimuth').show();
        myParent.find('.ajapaik-thumbnail-selection-icon').show("fade", 250);
    };
    window.paneImageHoverOut = function (e) {
        var myParent = $(e).parent(),
            icon = myParent.find('.ajapaik-thumbnail-selection-icon');
        if (parseInt($(this).data('id'), 10) !== parseInt(currentlySelectedMarker && currentlySelectedMarker.photoData.id, 10)) {
            myParent.find('.ajapaik-azimuth').hide();
        }
        if (!icon.hasClass('ajapaik-thumbnail-selection-icon-blue')) {
            myParent.find('.ajapaik-thumbnail-selection-icon').hide();
        }
    };
    window.paneRephotoCountHoverIn = function (e) {
        $(e).parent().find('.ajapaik-azimuth').show();
        return false;
    };
    window.paneRephotoCountHoverOut = function (e) {
        if (parseInt($(this).data('id'), 10) !== parseInt(currentlySelectedMarker && currentlySelectedMarker.photoData.id, 10)) {
            $(e).parent().find('.ajapaik-azimuth').hide();
        }
        return false;
    };
}());
