/*global tmpl*/
/*global google*/
/*global _gaq*/
/*global leaderboardUpdateURL*/
/*global gettext*/
/*global BigScreen*/
/*global photoLikeURL*/
/*global docCookies*/
var map,
    streetPanorama,
    input,
    searchBox,
    getMap,
    firstResizeDone = false,
    marker,
    bypass = false,
    mapOpts,
    streetViewOptions = {
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
    },
    dottedAzimuthLineSymbol,
    dottedAzimuthLine,
    getQueryParameterByName,
    prepareFullscreen,
    scoreboardShown = false,
    showScoreboard,
    hideScoreboard,
    updateLeaderboard,
    now,
    paneNow,
    lastTriggeredPane,
    isPhotoview,
    mapTypeChangedListener,
    guessLocationStarted = false,
    streetviewVisibleChangedListener,
    streetviewPanoChangedListener,
    photoModalCurrentlyOpenPhotoId,
    currentlySelectedRephotoId,
    photoModalFullscreenImageUrl,
    photoModalFullscreenImageSize,
    photoModalRephotoFullscreenImageUrl,
    photoModalRephotoFullscreenImageSize,
    photoModalRephotoArray,
    userClosedRephotoTools = false,
    fullscreenEnabled = false,
    currentPhotoDescription = false,
    comingBackFromGuessLocation = false,
    getGeolocation,
    handleGeolocation,
    geolocationError,
    myLocationButton,
    closeStreetviewButton,
    albumSelectionDiv,
    handleAlbumChange,
    updateStatDiv;


(function ($) {
    'use strict';
    albumSelectionDiv = $('#ajapaik-album-selection-menu');
    albumSelectionDiv.justifiedGallery({
        rowHeight: 270,
        margins: 5,
        captions: false,
        waitThumbnailsLoad: false
    });

    getMap = function (startPoint, startingZoom, isGameMap, mapType) {
        var latLng,
            zoomLevel,
            mapTypeIds,
            allowedMapTypes = {
                roadmap: google.maps.MapTypeId.ROADMAP,
                satellite: google.maps.MapTypeId.ROADMAP,
                OSM: 'OSM'
            };

        if (!startPoint) {
            latLng = new google.maps.LatLng(59, 26);
            startingZoom = 8;
        } else {
            latLng = startPoint;
        }

        if (!startingZoom) {
            zoomLevel = 13;
        } else {
            zoomLevel = startingZoom;
        }

        streetPanorama = new google.maps.StreetViewPanorama(
            document.getElementById('ajapaik-map-canvas'), streetViewOptions
        );

        mapTypeIds = [];
        for (var type in google.maps.MapTypeId) {
            if (google.maps.MapTypeId.hasOwnProperty(type)) {
                mapTypeIds.push(google.maps.MapTypeId[type]);
            }

        }
        mapTypeIds.push('OSM');

        if (isGameMap) {
            // Geotagger module manages all activity now
            mapOpts = {
                zoom: zoomLevel,
                scrollwheel: false,
                center: latLng,
                mapTypeControl: false,
                zoomControl: false,
                panControl: false,
                streetViewControl: false
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
                    position: google.maps.ControlPosition.RIGHT_CENTER
                },
                streetViewControl: true,
                streetViewControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_CENTER
                },
                streetView: streetPanorama,
                mapTypeControlOptions: {
                    mapTypeIds: mapTypeIds,
                    position: google.maps.ControlPosition.BOTTOM_CENTER
                }
            };
        }

        if (allowedMapTypes[mapType]) {
            mapOpts.mapTypeId = allowedMapTypes[mapType];
        } else {
            mapOpts.mapTypeId = allowedMapTypes.OSM;
        }

        map = new google.maps.Map(document.getElementById('ajapaik-map-canvas'), mapOpts);

        map.mapTypes.set('OSM', new google.maps.ImageMapType({
            getTileUrl: function (coord, zoom) {
                return 'http://tile.openstreetmap.org/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
            },
            tileSize: new google.maps.Size(256, 256),
            name: 'OSM',
            maxZoom: 19
        }));

        if (!isGameMap) {
            myLocationButton = document.createElement('button');
            $(myLocationButton).addClass('btn btn-default btn-xs').prop('id', 'ajapaik-mapview-my-location-button')
                .prop('title', gettext('Go to my location'))
                .html('<i class="glyphicon ajapaik-icon ajapaik-icon-my-location"></i>');
            map.controls[google.maps.ControlPosition.TOP_RIGHT].push(myLocationButton);
            input = /** @type {HTMLInputElement} */(document.getElementById('pac-input-mapview'));
            $(input).on('focus', function () {
                window.hotkeysActive = false;
            }).on('blur', function () {
                window.hotkeysActive = true;
            });
            map.controls[google.maps.ControlPosition.TOP_RIGHT].push(input);
            closeStreetviewButton = document.createElement('button');
            $(closeStreetviewButton).addClass('btn btn-default').prop('id', 'ajapaik-mapview-close-streetview-button')
                .html(gettext('Close'));
            streetPanorama.controls[google.maps.ControlPosition.BOTTOM_RIGHT].push(closeStreetviewButton);
            searchBox = new google.maps.places.SearchBox(/** @type {HTMLInputElement} */(input));
            google.maps.event.addListener(searchBox, 'places_changed', function () {
                var places = searchBox.getPlaces();
                if (places.length === 0) {
                    return;
                }
                map.setCenter(places[0].geometry.location);
            });

            google.maps.event.addListener(map, 'bounds_changed', function () {
                var bounds = map.getBounds();
                searchBox.setBounds(bounds);
                if (!firstResizeDone) {
                    google.maps.event.trigger(map, 'resize');
                    firstResizeDone = true;
                }
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
        }

        streetviewVisibleChangedListener = google.maps.event.addListener(streetPanorama, 'visible_changed', function () {
            // Works only in map view
            var photoPanel = $('#ajapaik-mapview-photo-panel');
            if (streetPanorama.getVisible()) {
                _gaq.push(['_trackEvent', 'Map', 'Opened Street View']);
                photoPanel.hide();
            } else {
                if (!guessLocationStarted) {
                    photoPanel.show();
                }
            }
        });

        streetviewPanoChangedListener = google.maps.event.addListener(streetPanorama, 'pano_changed', function () {
            // Works only in map view
            _gaq.push(['_trackEvent', 'Map', 'Street View Movement']);
        });

        mapTypeChangedListener = google.maps.event.addListener(map, 'maptypeid_changed', function () {
            // Works only in map view
            _gaq.push(['_trackEvent', 'Map', 'Map type changed']);
            window.syncMapStateToURL();
        });
    };

    // Functions used on modal mini-map and map view, duplicates in geotagger plugin to make it self-contained
    Math.getAzimuthBetweenTwoPoints = function (p1, p2) {
        if (p1 && p2) {
            var x = p2.lat() - p1.lat(),
                y = p2.lng() - p1.lng();
            return Math.degrees(Math.atan2(y, x));
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
        var newX = (Math.cos(azimuth) * lineLength) + startPoint.lat(),
            newY = (Math.sin(azimuth) * lineLength) + startPoint.lng();

        return new google.maps.LatLng(newX, newY);
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

        return new google.maps.LatLng(Math.degrees(endLatRadians), Math.degrees(endLonRadians));
    };

    // Used in map view and mini-map
    dottedAzimuthLineSymbol = {
        path: google.maps.SymbolPath.CIRCLE,
        strokeOpacity: 1,
        strokeWeight: 1.5,
        strokeColor: 'red',
        scale: 0.75
    };

    dottedAzimuthLine = new google.maps.Polyline({
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

    $('.full-box div').on('click', function (e) {
        e.preventDefault();
        if (window.BigScreen.enabled) {
            fullscreenEnabled = false;
            window.BigScreen.exit();
            if (window.lastScrollPosition) {
                $(window).scrollTop(window.lastScrollPosition);
            }
        }
    });

    $(document).on('click', '#ajapaik-full-screen-link', function (e) {
        e.preventDefault();
        window.lastScrollPosition = $(window).scrollTop();
        if (window.BigScreen.enabled) {
            var div = $('#ajapaik-fullscreen-image-container'),
                img = div.find('img');
            img.attr('src', img.attr('data-src')).show();
            window.BigScreen.request(div[0]);
            fullscreenEnabled = true;
            if (window.isGame) {
                _gaq.push(['_trackEvent', 'Game', 'Full-screen']);
            } else if (window.isMapview) {
                _gaq.push(['_trackEvent', 'Mapview', 'Full-screen']);
            } else if (window.isGallery) {
                _gaq.push(['_trackEvent', 'Gallery', 'Full-screen']);
            } else if (window.isPhotoview) {
                _gaq.push(['_trackEvent', 'Photoview', 'Full-screen']);
            }
        }
    });

    $(document).on('click', '#ajapaik-rephoto-full-screen-link', function (e) {
        e.preventDefault();
        if (window.BigScreen.enabled) {
            var div = $('#ajapaik-rephoto-fullscreen-image-container'),
                img = div.find('img');
            img.attr('src', img.attr('data-src')).show();
            window.BigScreen.request(div[0]);
            fullscreenEnabled = true;
            if (window.isGame) {
                _gaq.push(['_trackEvent', 'Game', 'Rephoto full-screen']);
            } else if (window.isMapview) {
                _gaq.push(['_trackEvent', 'Mapview', 'Rephoto full-screen']);
            } else if (window.isGallery) {
                _gaq.push(['_trackEvent', 'Gallery', 'Rephoto full-screen']);
            } else if (window.isPhotoview) {
                _gaq.push(['_trackEvent', 'Photoview', 'Full-screen']);
            }
        }
    });

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
            navigator.geolocation.getCurrentPosition(callback, geolocationError);
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
            target.find('.scoreboard').load(leaderboardUpdateURL + 'album/' + window.albumId);
        } else {
            target.find('.scoreboard').load(leaderboardUpdateURL);
        }
    };

    $(document).on('click', '#ajapaik-header-grid-button', function (e) {
        e.preventDefault();
        if (!window.isFrontpage) {
            if (window.isSelection) {
                window.history.go(-1);
            } else {
                var filterOff = parseInt(getQueryParameterByName('limitToAlbum'), 10) === 0;
                // TODO: The photo set needs to be POSTed to be of any size, made nginx allow larger GETs for now
                if ((!window.albumId || filterOff) && window.lastMarkerSet && window.lastMarkerSet.length < 251) {
                    window.location.href = '/?photos=' + window.lastMarkerSet;
                } else if (window.albumId) {
                    window.location.href = '/?album=' + window.albumId;
                } else {
                    window.location.href = '/';
                }
            }
        }
    });
    
    handleGeolocation = function (position) {
        $('#ajapaik-geolocation-error').hide();
        window.location.href = '/map?lat=' + position.coords.latitude + '&lng=' + position.coords.longitude + '&limitToAlbum=0&zoom=15';
    };
    
    geolocationError = function (error) {
        var targetElement = $('#ajapaik-geolocation-error-message');
        switch (error.code) {
            case error.PERMISSION_DENIED:
                targetElement.html(gettext('User denied the request for Geolocation.'));
                if (window.clickedMapButton && window.lastGeotaggedPhotoId) {
                    window.location.href = '/map/photo/' + window.lastGeotaggedPhotoId;
                }
                break;
            case error.POSITION_UNAVAILABLE:
                targetElement.html(gettext('Location information is unavailable.'));
                break;
            case error.TIMEOUT:
                targetElement.html(gettext('The request to get user location timed out.'));
                break;
            case error.UNKNOWN_ERROR:
                targetElement.html(gettext('An unknown error occurred.'));
                break;
        }
        $('#ajapaik-geolocation-error').show();
        window.setTimeout(function () {
            $('#ajapaik-geolocation-error').hide();
        }, 3000);
    };

    $(document).on('click', '#ajapaik-header-map-button', function (e) {
        e.preventDefault();
        if (window.isSelection) {
            window.history.go(-1);
        } else {
            if (window.albumId) {
                window.location.href = '/map?album=' + window.albumId;
            } else if (window.photoId) {
                window.location.href = '/map/photo/' + window.photoId;
            } else {
                window.clickedMapButton = true;
                if (window.navigator.geolocation) {
                    window.getGeolocation(handleGeolocation);
                }
            }
        }
    });

    $(document).on('click', '#ajapaik-header-profile-button', function (e) {
        e.preventDefault();
        window.updateLeaderboard();
        if (scoreboardShown) {
            hideScoreboard();
        } else {
            showScoreboard();
        }
    });

    updateStatDiv = function (count) {
        var statDiv = $('.ajapaik-minimap-geotagging-user-number');
        statDiv.empty().text(count);
        if (count) {
            statDiv.append('<div class="ajapaik-minimap-geotagging-user-multiple-people"></div>');
        } else {
            statDiv.append('<div class="ajapaik-minimap-geotagging-user-single-person"></div>');
        }
    };

    $(document).on('click', '.ajapaik-minimap-confirm-geotag-button', function () {
        var $this = $(this);
        if (!$this.hasClass('ajapaik-minimap-confirm-geotag-button-done')) {
            var photoId = $(this).data('id');
            $.post(window.confirmLocationURL, {
                photo: photoId,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            }, function (response) {
                $this.addClass('ajapaik-minimap-confirm-geotag-button-done');
                updateStatDiv(response.new_geotag_count);
            });
            if (window.isGame) {
                window.nextPhoto();
            }
            if (window.isFrontpage) {
                _gaq.push(['_trackEvent', 'Gallery', 'Photo modal confirm location click']);
            } else if (window.isMapview) {
                _gaq.push(['_trackEvent', 'Map', 'Photo modal confirm location click']);
            } else if (window.isGame) {
                _gaq.push(['_trackEvent', 'Game', 'Photo modal confirm location click']);
            }
        }
    });

    $(document).on('click', '.ajapaik-minimap-start-guess-CTA-button', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal CTA specify location click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal CTA specify location click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Photo modal CTA specify location click']);
        }
        if (window.isGame) {
            $('.ajapaik-game-specify-location-button')[0].click();
        } else {
            window.startGuessLocation($(this).data('id'));
        }
    });

    window.showPhotoMapIfApplicable = function (isPhotoview) {
        var arrowIcon = {
            path: 'M12 2l-7.5 18.29.71.71 6.79-3 6.79 3 .71-.71z',
            strokeColor: 'white',
            strokeOpacity: 1,
            strokeWeight: 1,
            fillColor: 'black',
            fillOpacity: 1,
            rotation: 0,
            scale: 1.5,
            anchor: new google.maps.Point(12, 12)
        },
        locationIcon = {
            path: 'M12 2c-3.87 0-7 3.13-7 7 0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
            strokeColor: 'white',
            strokeOpacity: 1,
            strokeWeight: 1,
            fillColor: 'black',
            fillOpacity: 1,
            scale: 1.5,
            anchor: new google.maps.Point(12, 0)
        },
        currentIcon;
        var container = $('#ajapaik-modal-photo-container'),
            mapContainer = $('#ajapaik-photo-modal-map-container');
        if (!window.isMobile && mapContainer.length > 0 && (!photoModalRephotoArray ||
            photoModalRephotoArray.length === 0 || userClosedRephotoTools)) {
            if (isPhotoview) {
                mapContainer.css('height', $('#ajapaik-photoview-main-photo').height());
            } else {
                mapContainer.show().css('height', container.height());
            }
            if (!window.photoModalPhotoLat && !window.photoModalPhotoLng) {
                $('#ajapaik-minimap-disabled-overlay').show();
            } else {
                $('#ajapaik-minimap-disabled-overlay').hide();
            }
            var center,
                minimapLargeCTAButton;
            if (!window.photoModalPhotoLat && !window.photoModalPhotoLng) {
                center = {
                    lat: 59.4372,
                    lng: 24.7453
                };
                minimapLargeCTAButton = document.createElement('button');
                $(minimapLargeCTAButton).addClass('ajapaik-minimap-start-guess-CTA-button');
            } else {
                center = {
                    lat: window.photoModalPhotoLat,
                    lng: window.photoModalPhotoLng
                };
                minimapLargeCTAButton = null;
                $('.ajapaik-minimap-start-guess-CTA-button').remove();
            }
            window.miniMap = new google.maps.Map(document.getElementById('ajapaik-photo-modal-map-canvas'), {
                center: center,
                zoom: 17,
                mapTypeControl: false,
                mapTypeId: 'OSM'
            });
            var minimapConfirmGeotagButton = document.createElement('button');
            $(minimapConfirmGeotagButton).addClass('btn').addClass('btn-default')
                .addClass('ajapaik-minimap-confirm-geotag-button')
                .prop('title', gettext('Confirm correct location'))
                .data('id', window.photoModalCurrentlyOpenPhotoId);
            if (window.photoModalUserHasConfirmedThisLocation) {
                $(minimapConfirmGeotagButton).addClass('ajapaik-minimap-confirm-geotag-button-done');
            }
            window.miniMap.controls[google.maps.ControlPosition.BOTTOM_LEFT].push(minimapConfirmGeotagButton);
            var minimapStartGuessButton = document.createElement('button');
            $(minimapStartGuessButton).addClass('btn').addClass('btn-default')
                .addClass('ajapaik-minimap-start-guess-button')
                .prop('title', gettext('Submit your own location'));
            window.miniMap.controls[google.maps.ControlPosition.BOTTOM_RIGHT].push(minimapStartGuessButton);
            var minimapGeotaggingUserNumber = document.createElement('div');
            $(minimapGeotaggingUserNumber).addClass('ajapaik-minimap-geotagging-user-number')
                .prop('title', gettext('Geotagged by this many users')).text(window.photoModalGeotaggingUserCount);
            var minimapGeotaggingUserIcon = document.createElement('div');
            minimapGeotaggingUserNumber.appendChild(minimapGeotaggingUserIcon);
            if (window.photoModalGeotaggingUserCount < 2) {
                $(minimapGeotaggingUserIcon).addClass('ajapaik-minimap-geotagging-user-single-person');
            } else {
                $(minimapGeotaggingUserIcon).addClass('ajapaik-minimap-geotagging-user-multiple-people');
            }
            window.miniMap.controls[google.maps.ControlPosition.TOP_RIGHT].push(minimapGeotaggingUserNumber);
            if (minimapLargeCTAButton) {
                $('.ajapaik-minimap-start-guess-CTA-button').remove();
                var mapCanvas = $('#ajapaik-photo-modal-map-canvas');
                $(minimapLargeCTAButton).css('margin-left', ((mapCanvas.width() / 2) - 35) + 'px')
                    .css('margin-top', ((mapCanvas.height() / 2) - 35) + 'px').attr('data-id', window.photoModalCurrentlyOpenPhotoId);
                mapContainer.append(minimapLargeCTAButton);
            }
            window.miniMap.mapTypes.set('OSM', new google.maps.ImageMapType({
                getTileUrl: function (coord, zoom) {
                    return 'http://tile.openstreetmap.org/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
                },
                tileSize: new google.maps.Size(256, 256),
                name: 'OpenStreetMap',
                maxZoom: 18
            }));
            if (window.photoModalPhotoAzimuth) {
                var start = new google.maps.LatLng(center.lat, center.lng);
                var geodesicEndPoint = Math.calculateMapLineEndPoint(window.photoModalPhotoAzimuth, start, 2000);
                var angle = Math.getAzimuthBetweenTwoPoints(start, geodesicEndPoint);
                var angleFix = window.photoModalPhotoAzimuth - angle;
                arrowIcon.rotation = window.photoModalPhotoAzimuth + angleFix;
                currentIcon = arrowIcon;
                window.minimapDottedAzimuthLine = new google.maps.Polyline({
                    geodesic: false,
                    strokeOpacity: 0,
                    icons: [
                        {
                            icon: dottedAzimuthLineSymbol,
                            offset: '0',
                            repeat: '7px'
                        }
                    ],
                    visible: true,
                    clickable: false,
                    map: window.miniMap
                });
                window.minimapDottedAzimuthLine.setPath([start, Math.simpleCalculateMapLineEndPoint(window.photoModalPhotoAzimuth, start, 0.02)]);
            } else {
                if (window.minimapDottedAzimuthLine) {
                    window.minimapDottedAzimuthLine.setVisible(false);
                }
                currentIcon = locationIcon;
            }
            if (window.photoModalPhotoLat && window.photoModalPhotoLng) {
                window.miniMapMarker = new google.maps.Marker({
                    position: new google.maps.LatLng(window.photoModalPhotoLat, window.photoModalPhotoLng),
                    map: window.miniMap,
                    title: gettext('Current location'),
                    icon: currentIcon
                });
            }
            window.miniMapStreetView = window.miniMap.getStreetView();
            google.maps.event.addListener(window.miniMapStreetView, 'visible_changed', function() {
                if (window.miniMapStreetView.getVisible()) {
                    window.miniMapMarker.setIcon(locationIcon);
                } else {
                    window.miniMapMarker.setIcon(arrowIcon);
                }
            });
            $('#ajapaik-modal-photo-container-container').removeClass('col-xs-12').addClass('col-xs-9');
        }
    };
    
    $(document).on('click', '.ajapaik-minimap-start-guess-button', function () {
        $('#ajapaik-photo-modal-specify-location').click();
    });
    
    $(document).on('click', '.ajapaik-album-selection-item', function (e) {
        e.preventDefault();
        var $this = $(this);
        window.albumId = $this.data('id');
        handleAlbumChange();
    });
    
    $(document).on('click', '#ajapaik-photo-modal-discuss', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal discuss click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal discuss click']);
        }
        var commentsSection = $('#ajapaik-comments-section');
        if (commentsSection.hasClass('hidden')) {
            commentsSection.removeClass('hidden');
            window.FB.XFBML.parse($('#ajapaik-rephoto-comments').get(0));
            window.FB.XFBML.parse($('#ajapaik-original-photo-comments').get(0));
        } else {
            commentsSection.addClass('hidden');
        }
    });

    $(document).on('click', '#ajapaik-feedback-link', function () {
        _gaq.push(['_trackEvent', 'General', 'Feedback link click']);
    });
    $(document).on('click', '.ajapaik-photo-modal-rephoto-thumb', function () {
        var targetId = $(this).data('id'),
            infoDiv = $('#ajapaik-photo-modal-rephoto-info-column'),
            photoDiv = $('#ajapaik-modal-rephoto-container'),
            fullscreenDiv = $('#ajapaik-rephoto-full-screen-image');
        if (!targetId) {
            targetId = currentlySelectedRephotoId;
        }
        infoDiv.show();
        for (var i = 0; i < window.photoModalRephotoArray.length; i += 1) {
            if (window.photoModalRephotoArray[i].id == targetId) {
                fullscreenDiv.attr('data-src', window.photoModalRephotoArray[i].fullscreen_url);
                window.prepareFullscreen(window.photoModalRephotoArray[i].fullscreen_width,
                        window.photoModalRephotoArray[i].fullscreen_height,
                        '#ajapaik-rephoto-full-screen-image');
                photoDiv.html(tmpl('ajapaik-photo-modal-rephoto-template', window.photoModalRephotoArray[i]));
                infoDiv.html(tmpl('ajapaik-photo-modal-rephoto-info-template', window.photoModalRephotoArray[i]));
                currentlySelectedRephotoId = targetId;
                var commentsDiv = $('#ajapaik-rephoto-comments');
                commentsDiv.find('.fb-comments').attr('data-href', window.photoModalRephotoArray[i].fb_url);
                window.FB.XFBML.parse();
                if (window.isFrontpage) {

                } else {
                    window.syncMapStateToURL();
                }
                break;
            }
        }
    });
    $(document).on('click', '#ajapaik-show-rephoto-selection-overlay-button', function () {
        $(this).hide();
        userClosedRephotoTools = false;
        var rephotoColumn = $('#ajapaik-photo-modal-rephoto-column'),
            rephotoInfoColumn = $('#ajapaik-photo-modal-rephoto-info-column'),
            originalPhotoInfoColumn = $('#ajapaik-photo-modal-original-photo-info-column'),
            rephotoDiv = $('#ajapaik-modal-rephoto-container');
        if (window.photoModalRephotoArray.length > 1) {
            $('#ajapaik-rephoto-selection').show();
            $('#ajapaik-photo-modal-original-photo-column').removeClass('col-xs-12').addClass('col-xs-5');
            rephotoInfoColumn.removeClass('col-xs-12').removeClass('col-xs-6').addClass('col-xs-5');
            originalPhotoInfoColumn.removeClass('col-xs-12').removeClass('col-xs-6').addClass('col-xs-5');
        } else {
            $('#ajapaik-photo-modal-original-photo-column').removeClass('col-xs-12').addClass('col-xs-6');
            rephotoColumn.removeClass('col-xs-5').addClass('col-xs-6');
            rephotoInfoColumn.removeClass('col-xs-12').removeClass('col-xs-5').addClass('col-xs-6');
            originalPhotoInfoColumn.removeClass('col-xs-12').removeClass('col-xs-5').addClass('col-xs-6');
        }
        rephotoInfoColumn.show();
        rephotoColumn.show();
        currentlySelectedRephotoId = window.photoModalRephotoArray[0]['id'];
        rephotoDiv.html(tmpl('ajapaik-photo-modal-rephoto-template', window.photoModalRephotoArray[0]));
        rephotoInfoColumn.html(tmpl('ajapaik-photo-modal-rephoto-info-template', window.photoModalRephotoArray[0]));
        $('#ajapaik-photo-modal-map-container').hide();
        $('#ajapaik-modal-photo-container-container').removeClass('col-xs-9').addClass('col-xs-12');
        if (!window.isFrontpage) {
           window.syncMapStateToURL();
        }
    });
    $(document).on('click', '#ajapaik-photo-modal-source', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Source link click']);
        }  else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Source link click']);
        }
    });
    $(document).on('click', '#ajapaik-photo-modal-rephoto-source', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Rephoto source link click']);
        }  else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Rephoto source link click']);
        }
    });
    $(document).on('click', '#ajapaik-close-rephoto-overlay-button', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $('#ajapaik-photo-modal-rephoto-column').hide();
        $('#ajapaik-rephoto-selection').hide();
        $('#ajapaik-show-rephoto-selection-overlay-button').show();
        $('#ajapaik-grab-link').find('a').attr('href', window.hostname + window.originalPhotoAbsoluteURL).text(window.hostname + window.originalPhotoAbsoluteURL);
        $('#ajapaik-photo-modal-original-photo-column').removeClass('col-xs-5').removeClass('col-xs-6').addClass('col-xs-12');
        $('#ajapaik-photo-modal-original-photo-info-column').removeClass('col-xs-5').removeClass('col-xs-6').addClass('col-xs-12');
        $('#ajapaik-photo-modal-rephoto-info-column').hide();
        currentlySelectedRephotoId = false;
        if (window.isFrontpage || window.isPhotoview) {

        } else {
            window.syncMapStateToURL();
        }
        userClosedRephotoTools = true;
        if (window.showPhotoMapIfApplicable) {
            window.showPhotoMapIfApplicable();
        }
    });
    $(document).on('click', '#ajapaik-grab-link', function (e) {
        e.stopPropagation();
    });
    $(document).on('click', '#ajapaik-comment-tabs li', function () {
        window.FB.XFBML.parse($('#ajapaik-rephoto-comments').get(0));
        window.FB.XFBML.parse($('#ajapaik-original-photo-comments').get(0));
    });
    $(document).on('click', '.ajapaik-thumbnail-selection-icon', function (e) {
        e.stopPropagation();
        var $this = $(this),
            other = $(".ajapaik-frontpage-image-container[data-id='" + $this.data('id') +"']").find('.ajapaik-thumbnail-selection-icon');
        if ($this.hasClass('ajapaik-thumbnail-selection-icon-white')) {
            $this.removeClass('ajapaik-thumbnail-selection-icon-white');
        } else {
            $this.addClass('ajapaik-thumbnail-selection-icon-white');
        }
        if ($this.parent().attr('id') === 'ajapaik-modal-photo-container') {
            if (other) {
                if (other.hasClass('ajapaik-thumbnail-selection-icon-white')) {
                    other.removeClass('ajapaik-thumbnail-selection-icon-white');
                } else {
                    other.addClass('ajapaik-thumbnail-selection-icon-white');
                    other.show();
                }
            }
        }
        var data = {
            id: $this.data('id'),
            csrfmiddlewaretoken: docCookies.getItem('csrftoken')
        };
        $.post(window.photoSelectionURL, data, function (response) {
            var len = Object.keys(response).length,
                target = $('#ajapaik-header-selection-indicator');
            if (len > 0) {
                target.removeClass('hidden');
            } else {
                target.addClass('hidden');
            }
            target.find('span').html(len);
        });
    });
    window.openPhotoUploadModal = function () {
        if (window.photoModalCurrentlyOpenPhotoId) {
            $.ajax({
                cache: false,
                url: window.photoUploadModalURL + window.photoModalCurrentlyOpenPhotoId + '/',
                success: function (result) {
                    var rephotoUploadModal = $('#ajapaik-rephoto-upload-modal');
                    rephotoUploadModal.data('bs.modal', null);
                    rephotoUploadModal.html(result).modal();
                }
            });
        }
    };
    $(document).on('mouseenter', '.ajapaik-frontpage-image', function () {
        $(this).parent().find('.ajapaik-thumbnail-selection-icon').show();
    });
    $(document).on('mouseout', '.ajapaik-frontpage-image', function () {
        var icon = $(this).parent().find('.ajapaik-thumbnail-selection-icon');
        if (!icon.hasClass('ajapaik-thumbnail-selection-icon-white')) {
            $(this).parent().find('.ajapaik-thumbnail-selection-icon').hide();
        }
    });
    $(document).on('mouseenter', '.ajapaik-thumbnail-selection-icon', function () {
        $(this).parent().find('.ajapaik-thumbnail-selection-icon').show();
    });
    $(document).on('mouseout', '.ajapaik-thumbnail-selection-icon', function () {
        var icon = $(this).parent().find('.ajapaik-thumbnail-selection-icon');
        if (!icon.hasClass('ajapaik-thumbnail-selection-icon-white')) {
            $(this).parent().find('.ajapaik-thumbnail-selection-icon').hide();
        }
    });
    $(document).on('click', '#ajapaik-photo-modal-add-rephoto', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal add rephoto click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal add rephoto click']);
        }
        window.openPhotoUploadModal();
    });
    window.loadPossibleParentAlbums = function (parentAlbum, currentAlbumId, customSelector) {
        var url = window.curatorSelectableParentAlbumsURL;
        if (currentAlbumId) {
            url += currentAlbumId + '/';
        }
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            },
            success: function (response) {
                var targetDiv;
                if (customSelector) {
                    targetDiv = $(customSelector);
                } else {
                    targetDiv = $('#ajapaik-curator-change-album-parent');
                }
                targetDiv.empty();
                targetDiv.append(
                    tmpl(
                        'ajapaik-curator-my-album-select-option',
                        {id: -1, name: gettext('Not selected')}
                    )
                );
                for (var i = 0, l = response.length; i < l; i += 1) {
                    if (!response[i].open) {
                        targetDiv.append(tmpl('ajapaik-curator-my-album-select-option', response[i]));
                    }
                }
                targetDiv.append(tmpl('ajapaik-curator-my-album-select-separator', {}));
                for (i = 0, l = response.length; i < l; i += 1) {
                    if (response[i].open) {
                        targetDiv.append(tmpl('ajapaik-curator-my-album-select-option', response[i]));
                    }
                }
                if (parentAlbum) {
                    targetDiv.val(parentAlbum);
                }
                if (window.isCurator) {
                    _gaq.push(['_trackEvent', 'Curator', 'Load parent albums success']);
                } else {
                    _gaq.push(['_trackEvent', 'Selection', 'Load parent albums success']);
                }
            },
            error: function () {
                if (window.isCurator) {
                    _gaq.push(['_trackEvent', 'Curator', 'Load parent albums error']);
                } else {
                    _gaq.push(['_trackEvent', 'Selection', 'Load parent albums success']);
                }
            }
        });
    };
    window.loadSelectableAlbums = function () {
        $.ajax({
            type: 'POST',
            url: window.curatorSelectableAlbumsURL,
            data: {
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            },
            success: function (response) {
                var targetDiv = $('#ajapaik-curator-album-select');
                targetDiv.empty();
                targetDiv.append(
                    tmpl(
                        'ajapaik-curator-my-album-select-option',
                        {id: -1, name: gettext('Not selected')}
                    )
                );
                for (var i = 0, l = response.length; i < l; i += 1) {
                    if (!response[i].open) {
                        targetDiv.append(tmpl('ajapaik-curator-my-album-select-option', response[i]));
                    }
                }
                targetDiv.append(tmpl('ajapaik-curator-my-album-select-separator', {}));
                for (i = 0, l = response.length; i < l; i += 1) {
                    if (response[i].open) {
                        targetDiv.append(tmpl('ajapaik-curator-my-album-select-option', response[i]));
                    }
                }
                if (window.isCurator) {
                    _gaq.push(['_trackEvent', 'Curator', 'Load album selection success']);
                } else if (window.isSelection) {
                    _gaq.push(['_trackEvent', 'Selection', 'Load album selection success']);
                }
            },
            error: function () {
                if (window.isCurator) {
                    _gaq.push(['_trackEvent', 'Curator', 'Load album selection error']);
                } else if (window.isSelection) {
                    _gaq.push(['_trackEvent', 'Selection', 'Load album selection error']);
                }
            }
        });
    };
    $(document).on('click', '#ajapaik-header-menu-button-hidden-xs', function () {
        $('#ajapaik-header-menu-button').click();
    });
    $(document).on('click', '#ajapaik-photo-modal-share', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal share click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal share click']);
        }
    });
    $(document).on('click', '#ajapaik-sift-pics-link', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Sift.pics link click']);
        } else if (window.isOrder) {
            _gaq.push(['_trackEvent', 'Order', 'Sift.pics link click']);
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
        _gaq.push(['_trackEvent', '', 'Full leaderboard']);
    });
    $(document).on('click', '#ajapaik-info-window-leaderboard-link', function (e) {
        e.preventDefault();
        window.albumId = $(this).data('id');
        $('#full_leaderboard').click();
        window.albumId = null;
    });

    $(document).on('click', '#ajapaik-invert-rephoto-overlay-button', function (e) {
        e.preventDefault();
        e.stopPropagation();
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
            _gaq.push(['_trackEvent', 'Gallery', 'General info click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'General info click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Mapview', 'General info click']);
        }
    });

    //$(document).on('click', '#ajapaik-mobile-about-button', function (e) {
    //    var targetDiv = $('#ajapaik-general-info-modal');
    //    if (window.generalInfoModalURL) {
    //        $.ajax({
    //            url: window.generalInfoModalURL,
    //            success: function (resp) {
    //                targetDiv.html(resp).modal();
    //            }
    //        });
    //    }
    //    if (window.isFrontpage) {
    //        _gaq.push(['_trackEvent', 'Gallery', 'General info click']);
    //    } else if (window.isGame) {
    //        _gaq.push(['_trackEvent', 'Game', 'General info click']);
    //    } else if (window.isMapview) {
    //        _gaq.push(['_trackEvent', 'Mapview', 'General info click']);
    //    }
    //});

    $(document).on('click', '.ajapaik-photo-modal-previous-button', function (e) {
        e.preventDefault();
        if (!$(this).hasClass('ajapaik-photo-modal-previous-button-disabled')) {
            var previousId = $('#ajapaik-frontpage-image-container-' + photoModalCurrentlyOpenPhotoId).prev().data('id');
            if (previousId && !window.nextPhotoLoading) {
                window.loadPhoto(previousId);
            }
            if (window.isFrontpage) {
                _gaq.push(['_trackEvent', 'Gallery', 'Photo modal previous']);
            } else if (window.isGame) {
                _gaq.push(['_trackEvent', 'Game', 'Photo modal previous']);
            }
        } else {
            if (window.isFrontpage) {
                window.previousPageOnModalClose = true;
                window.closePhotoDrawer();
            }
        }
    });

    $(document).on('click', ".ajapaik-flip-photo-overlay-button", function () {
        var target = $("#ajapaik-modal-photo"),
            fullScreenImage = $('#ajapaik-full-screen-image');
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
        } else {
            $(this).addClass('active');
        }
        if (target.hasClass("ajapaik-photo-flipped")) {
            target.removeClass("ajapaik-photo-flipped");
        } else {
            target.addClass("ajapaik-photo-flipped");
        }
        if (fullScreenImage.hasClass("ajapaik-photo-flipped")) {
            fullScreenImage.removeClass("ajapaik-photo-flipped");
        } else {
            fullScreenImage.addClass("ajapaik-photo-flipped");
        }
        window.flipPhoto();
    });

    $(document).on('click', '.ajapaik-like-photo-overlay-button', function () {
        var $this = $(this),
            $i = $this.find('i'),
            $likeCount = $this.find('.ajapaik-like-count');
        $.post(photoLikeURL, {
            photo: window.photoModalCurrentlyOpenPhotoId,
            csrfmiddlewaretoken: docCookies.getItem('csrftoken')
        }, function (response) {
            if (response.level === 0) {
                $i.html('favorite_outline');
                $this.removeClass('active big');
            } else if (response.level === 1) {
                $i.html('favorite');
                $this.addClass('active');
            } else if (response.level === 2) {
                $i.html('favorite');
                $this.addClass('big');
            }
            $likeCount.html(response.likeCount);
        });
    });

    $(document).on('click', '.ajapaik-photo-modal-next-button', function () {
        if (!$(this).hasClass('ajapaik-photo-modal-next-button-disabled')) {
            var nextId = $('#ajapaik-frontpage-image-container-' + photoModalCurrentlyOpenPhotoId).next().data('id');
            if (nextId && !window.nextPhotoLoading) {
                window.loadPhoto(nextId);
            }
            if (window.isFrontpage) {
                _gaq.push(['_trackEvent', 'Gallery', 'Photo modal next']);
            } else if (window.isGame) {
                _gaq.push(['_trackEvent', 'Game', 'Photo modal next']);
            }
        } else {
            if (window.isFrontpage) {
                window.nextPageOnModalClose = true;
                window.closePhotoDrawer();
            }
        }
    });

    $(document).on('click', '.ajapaik-photo-modal-album-link', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Album link click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Album link click']);
        }
    });

    $(document).on('click', '#ajapaik-photo-modal-specify-location', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal specify location click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal specify location click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Photo modal specify location click']);
        }
        window.startGuessLocation($(this).data('id'));
    });

    $(document).on('click', '#ajapaik-photo-modal-close-button', function (e) {
        e.preventDefault();
        window.closePhotoDrawer();
    });

    $(document).on('change', '#ajapaik-curator-create-new-album-checkbox', function () {
        var $this = $(this),
            creationFields = $('.ajapaik-curator-new-album-creation-field'),
            existingFields = $('.ajapaik-curator-add-to-existing-album-field');
        if ($this.is(':checked')) {
            creationFields.show();
            existingFields.hide();
        } else {
            creationFields.hide();
            existingFields.show();
        }
    });

    $(document).on('keyup', '#ajapaik-curator-album-filter', function () {
        var filter = $(this).val().toLowerCase();
        if (filter === "") {
            $('option').show();
        } else {
            $('#ajapaik-curator-album-select').find('option').each(function() {
                if ($(this).text().toLowerCase().indexOf(filter) > -1) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        }
    });

    $(document).on('hidden.bs.modal', '#ajapaik-choose-albums-modal', function () {
        $('#ajapaik-curator-album-filter').val(null);
    });

    // Chrome jumps up https://code.google.com/p/chromium/issues/detail?id=142427
    BigScreen.onexit = function() {
        if (window.lastScrollPosition) {
            setTimeout(function () {
                $(window).scrollTop(window.lastScrollPosition);
                window.lastScrollPosition = null;
            }, 500);
        }
    };

    $(document).on('click', '#ajapaik-header-album-more', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var targetDiv = $('#ajapaik-info-modal');
        if (window.albumId && window.infoModalURL) {
            $.ajax({
                url: window.infoModalURL,
                data: {
                    album: window.albumId,
                    linkToMap: window.linkToMap,
                    linkToGame: window.linkToGame,
                    linkToGallery: window.linkToGallery,
                    fbShareGame: window.fbShareGame,
                    fbShareMap: window.fbShareMap,
                    fbShareGallery: window.fbShareGallery
                },
                success: function (resp) {
                    targetDiv.html(resp);
                    targetDiv.modal().on('shown.bs.modal', function () {
                        window.FB.XFBML.parse($('#ajapaik-info-modal-like').get(0));
                    });
                }
            });
        }
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Album info click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Album info click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Mapview', 'Album info click']);
        }
    });

    $(document).on('click', '.ajapaik-album-selection-album-more-button, .ajapaik-photo-modal-album-more-button', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var targetDiv = $('#ajapaik-info-modal');
        if ($(this).data('id') && window.infoModalURL) {
            var fbShareGallery = true,
                fbShareMap = false,
                fbShareGame = false,
                linkToGallery = true,
                linkToMap = true,
                linkToGame = true;
            if (window.isGallery) {
                fbShareGallery = true;
                fbShareMap = false;
                linkToGallery = false;
                linkToMap = true;
            } else if (window.isMapview) {
                fbShareGallery = false;
                fbShareMap = true;
                linkToGallery = true;
                linkToMap = false;
            } else if (window.isPhotoview) {
                fbShareGallery = true;
                fbShareMap = false;
                linkToGallery = true;
                linkToMap = true;
            }
            $.ajax({
                url: window.infoModalURL,
                data: {
                    album: $(this).data('id'),
                    linkToMap: linkToMap,
                    linkToGame: linkToGame,
                    linkToGallery: linkToGallery,
                    fbShareGallery: fbShareGallery,
                    fbShareMap: fbShareMap,
                    fbShareGame: fbShareGame
                },
                success: function (resp) {
                    targetDiv.html(resp);
                    targetDiv.modal().on('shown.bs.modal', function () {
                        window.FB.XFBML.parse($('#ajapaik-info-modal-like').get(0));
                    });
                }
            });
        }
        if (window.isGallery) {
           _gaq.push(['_trackEvent', 'Gallery', 'Album caption info click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Mapview', 'Album caption info click']);
        }
    });

    $(document).on('click', '.ajapaik-change-language-link', function (e) {
        e.preventDefault();
        $('#ajapaik-language').val($(this).attr('data-lang-code'));
        $('input[name=csrfmiddlewaretoken]').val(docCookies.getItem('csrftoken'));
        $('#ajapaik-change-language-form').submit();
    });

    $(document).on('click', '#ajapaik-filter-closest-link', function (e) {
        e.preventDefault();
        getGeolocation(window.handleGeolocation);
    });

    $(document).on('click', '.ajapaik-album-info-modal-album-link', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Album info album link click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Album info album link click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Mapview', 'Album info album link click']);
        }
    });

    $(document).on('click', '#ajapaik-mapview-close-streetview-button', function () {
        map.getStreetView().setVisible(false);
    });

    $(document).on('click', '#ajapaik-filtering-help', function (e) {
        e.stopPropagation();
        $('#ajapaik-filtering-tutorial-modal').modal();
    });

    $(document).on('click', '#ajapaik-close-filtering-tutorial-modal', function (e) {
        e.stopPropagation();
        $('#ajapaik-filtering-tutorial-modal').modal('toggle');
    });

    $(window).on('resize', function () {
        if (window.innerWidth > 768) {
            $('.navbar-collapse').removeClass('in');
        }
    });

    if (typeof String.prototype.startsWith !== 'function') {
        String.prototype.startsWith = function (str) {
            return this.indexOf(str) === 0;
        };
    }
}(jQuery));