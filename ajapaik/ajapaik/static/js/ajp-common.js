/*global tmpl*/
/*global google*/
/*global _gaq*/
/*global leaderboardUpdateURL*/
/*global gettext*/
/*global BigScreen*/
/*global photoLikeURL*/
/*global docCookies*/
/*global VanalinnadGooglemApi */
var map,
    streetPanorama,
    input,
    searchBox,
    commonVgmapi,
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
            position: google.maps.ControlPosition.TOP_CENTER
        },
        enableCloseButton: true,
        visible: false
    },
    dottedAzimuthLineSymbol,	
    dottedAzimuthLine,
    getQueryParameterByName,
    scoreboardShown = false,
    showScoreboard,
    hideScoreboard,
    updateLeaderboard,
    now,
    isPhotoview,
    photoPanelClosedByStreetView = false,
    mapTypeChangedListener,
    guessLocationStarted = false,
    streetviewVisibleChangedListener,
    streetviewPanoChangedListener,
    currentlyOpenPhotoId,
    currentlySelectedRephotoId,
    currentlySelectedSimilarPhotoId,
    photoModalFullscreenImageUrl,
    photoModalRephotoFullscreenImageUrl,
    photoModalSimilarFullscreenImageUrl,
    photoModalRephotoArray,
    photoModalSimilarPhotoArray,
    userClosedRephotoTools = true,
    userClosedSimilarPhotoTools = true,
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

$('.ajp-navbar').autoHidingNavbar();

(function ($) {
    'use strict';

    albumSelectionDiv = $('#ajp-album-selection-menu');
    if (albumSelectionDiv.length > 0) {
        albumSelectionDiv.justifiedGallery({
            rowHeight: 270,
            margins: 5,
            captions: false,
            waitThumbnailsLoad: false
        });
    }
    getMap = function (startPoint, startingZoom, isGameMap, mapType) {
        var latLng,
            zoomLevel,
            mapTypeIds,
            allowedMapTypes = {
                roadmap: google.maps.MapTypeId.ROADMAP,
                satellite: google.maps.MapTypeId.SATELLITE,
                OSM: 'OSM',
                'old-maps': 'old-maps'
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
            document.getElementById('ajp-map-canvas'), streetViewOptions
        );

        mapTypeIds = [];
        for (var type in google.maps.MapTypeId) {
            if (google.maps.MapTypeId.hasOwnProperty(type)) {
                mapTypeIds.push(google.maps.MapTypeId[type]);
            }

        }
        mapTypeIds.push('OSM');
        mapTypeIds.push('old-maps');

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
                    style: window.innerWidth > 768 ? google.maps.MapTypeControlStyle.HORIZONTAL_BAR : google.maps.MapTypeControlStyle.DROPDOWN_MENU,
                    mapTypeIds: mapTypeIds,
                    position: window.innerWidth > 768 ? google.maps.ControlPosition.BOTTOM_CENTER : google.maps.ControlPosition.BOTTOM_RIGHT
                }
            };
        }

        if (allowedMapTypes[mapType]) {
            mapOpts.mapTypeId = allowedMapTypes[mapType];
        } else {
            mapOpts.mapTypeId = allowedMapTypes.roadmap;;
        }

        map = new google.maps.Map(document.getElementById('ajp-map-canvas'), mapOpts);

        map.mapTypes.set('OSM', new google.maps.ImageMapType({
            getTileUrl: function (coord, zoom) {
                return 'https://a.tile.openstreetmap.org/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
            },
            tileSize: new google.maps.Size(256, 256),
            name: 'OSM',
            maxZoom: 19
        }));

        var oldMapsCity = getQueryParameterByName('maps-city'),
        oldMapsIdx = getQueryParameterByName('maps-index');
        if(oldMapsCity){
            commonVgmapi = new VanalinnadGooglemApi(oldMapsCity, false, map)
        }
        else{
            commonVgmapi = new VanalinnadGooglemApi(null, false, map);
        }
        var cityDataDoneCallback = function () {
            commonVgmapi.buildVanalinnadMapCityControl();
            commonVgmapi.buildMapYearControl();
            if (window.map.getMapTypeId() === 'old-maps') {
                commonVgmapi.showControls();
            } else {
                commonVgmapi.hideControls();
            }
            if (!oldMapsIdx) {
                commonVgmapi.changeIndex(0);
            } else {
                commonVgmapi.changeIndex(oldMapsIdx);
            }
        };
        commonVgmapi.getCityData(cityDataDoneCallback);
        map.mapTypes.set('old-maps', commonVgmapi.juksMapType);
        if (!isGameMap) {
            myLocationButton = document.createElement('button');
            $(myLocationButton)
                .addClass('btn btn-light btn-sm')
                .prop('id', 'ajp-mapview-my-location-button')
                .prop('title', gettext('Go to my location'))
                .html('<i class="glyphicon ajp-icon ajp-icon-my-location"></i>');
            map.controls[google.maps.ControlPosition.TOP_RIGHT].push(myLocationButton);
            input = /** @type {HTMLInputElement} */(document.getElementById('pac-input-mapview'));
            $(input).on('focus', function () {
                window.hotkeysActive = false;
            }).on('blur', function () {
                window.hotkeysActive = true;
            });
            map.controls[google.maps.ControlPosition.TOP_RIGHT].push(input);
            closeStreetviewButton = document.createElement('button');
            $(closeStreetviewButton).addClass('btn btn-secondary').prop('id', 'ajp-mapview-close-streetview-button')
                .html(gettext('Close'));
            streetPanorama.controls[google.maps.ControlPosition.BOTTOM_RIGHT].push(closeStreetviewButton);
            searchBox = new google.maps.places.SearchBox(/** @type {HTMLInputElement} */(input));
            google.maps.event.addListener(searchBox, 'places_changed', function () {
                var places = searchBox.getPlaces();
                if (places.length === 0) {
                    return;
                }
                map.setCenter(places[0].geometry.location);
                map.setZoom(16);
            });

            google.maps.event.addListener(map, 'idle', function () {
                google.maps.event.trigger(map, 'resize');
                var bounds = map.getBounds();
                searchBox.setBounds(bounds);
                window.toggleVisiblePaneElements();
            });
        }

        streetviewVisibleChangedListener = google.maps.event.addListener(streetPanorama, 'visible_changed', function () {
            // Works only in map view
            let openButton = $('#open-btn');
            if (streetPanorama.getVisible()) {
                _gaq.push(['_trackEvent', 'Map', 'Opened Street View']);
                if(!!window.toggleSidePanel && !!window.isSidePanelOpen){
                    window.toggleSidePanel();
                    window.photoPanelClosedByStreetView = true;
                }
                if(openButton){
                    openButton.addClass('d-none');
                }
            } else {
                if (!guessLocationStarted && photoPanelClosedByStreetView) {
                    window.toggleSidePanel();
                    window.photoPanelClosedByStreetView = false;
                }
                if(openButton){
                    openButton.removeClass('d-none');
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
            if (window.map.getMapTypeId() === 'old-maps') {
                commonVgmapi.showControls();
            } else {
                commonVgmapi.hideControls();
            }
            window.syncMapStateToURL();
        });
    };

    // Functions used on modal mini-map and map view, duplicates in geoTagger plugin to make it self-contained
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

    Math.haversineDistance = function (start, end) {
        var R = 6371,
            dLat = Math.radians(end.latitude - start.latitude),
            dLon = Math.radians(end.longitude - start.longitude),
            lat1 = Math.radians(start.latitude),
            lat2 = Math.radians(end.latitude),
            a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) *
                Math.cos(lat2),
            c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
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

    var update_comment_likes = function (link) {
        var update_badge = function (badge, count) {
            badge.text('(' + count + ')');
            if (count <= 0) {
                badge.addClass('d-none');
            } else {
                badge.removeClass('d-none');
            }
        };
        var comment_id = link.data('comment-id');

        $.get('/comments/like-count/' + comment_id + '/', {}, function (response) {
            var like_count_badge = $('#ajp-comments-like-count-' + comment_id);
            var dislike_count_badge = $('#ajp-comments-dislike-count-' + comment_id);
            update_badge(like_count_badge, response.like_count);
            update_badge(dislike_count_badge, response.dislike_count);
        });
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

    $(document).on('click', '#ajp-full-screen-link', function (e) {
        e.preventDefault();
        window.lastScrollPosition = $(window).scrollTop();
        if (window.BigScreen.enabled) {
            var div = $('#ajp-fullscreen-image-container'),
                img = div.find('img');
            img.attr('src', img.attr('data-src')).show();
            if (window.photoModalCurrentPhotoFlipped) {
                img.addClass('ajp-photo-flipped');
            } else {
                img.removeClass('ajp-photo-flipped');
            }
            openMainPhotoToFullScreen(div);
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

    $(document).on('click', '#ajp-rephoto-full-screen-link', function (e) {
        e.preventDefault();
        if (window.BigScreen.enabled) {
            var div = $('#ajp-rephoto-fullscreen-image-container'),
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

    $(document).on('click', '#ajp-similar-photo-full-screen-link', function (e) {
        e.preventDefault();
        if (window.BigScreen.enabled) {
            var div = $('#ajp-similar-fullscreen-image-container'),
                img = div.find('img');
            img.attr('src', img.attr('data-src')).show();
            window.BigScreen.request(div[0]);
            fullscreenEnabled = true;
            if (window.isGame) {
                _gaq.push(['_trackEvent', 'Game', 'Similar full-screen']);
            } else if (window.isMapview) {
                _gaq.push(['_trackEvent', 'Mapview', 'Similar full-screen']);
            } else if (window.isGallery) {
                _gaq.push(['_trackEvent', 'Gallery', 'Similar full-screen']);
            } else if (window.isPhotoview) {
                _gaq.push(['_trackEvent', 'Photoview', 'Full-screen']);
            }
        }
    });

    getGeolocation = function getLocation(callback) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(callback, geolocationError);
        }
    };

    showScoreboard = function () {
        $('.ajp-navbar').find('.score-container').slideDown();
        scoreboardShown = true;
    };

    hideScoreboard = function () {
        $('.ajp-navbar').find('.score-container').slideUp();
        scoreboardShown = false;
    };

    updateLeaderboard = function () {
        var target = $('.score-container');
        if (window.albumId) {
            target.find('.scoreboard').load(leaderboardUpdateURL + 'album/' + window.albumId);
        } else {
            target.find('.scoreboard').load(leaderboardUpdateURL);
        }
    };

    $(document).on('click', '#ajp-header-grid-button', function (e) {
        if (!window.isPhotoview) {
            e.preventDefault();
            var uri = URI(window.location);
            if (uri.query().indexOf('people') !== -1) {
                window.location.href = uri.removeQuery('people');
            }
            if (uri.query().indexOf('postcards') !== -1) {
                window.location.href = uri.removeQuery('postcards');
            }
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
        }
    });

    handleGeolocation = function (position) {
        $('#ajp-geolocation-error').hide();
        window.location.href = '/map?lat=' + position.coords.latitude + '&lng=' + position.coords.longitude + '&limitToAlbum=0&zoom=15';
    };

    geolocationError = function (error) {
        var targetElement = $('#ajp-geolocation-error-message');
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
        $('#ajp-geolocation-error').show();
        window.setTimeout(function () {
            $('#ajp-geolocation-error').hide();
        }, 3000);
    };

    $(document).on('click', '#ajp-header-map', function (e) {
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

    $(document).on('click', '#ajp-header-profile', function (e) {
        e.preventDefault();
        if (!window.isTop50 && !window.isLeaderboard) {
            window.updateLeaderboard();
        }
        if (scoreboardShown) {
            hideScoreboard();
        } else {
            showScoreboard();
        }
    });

    updateStatDiv = function (count) {
        var statDiv = $('.ajp-minimap-geotagging-user-number');
        if(statDiv.length === 0) {
            statDiv = $('#ajp-photo-modal-map-canvas > div.leaflet-control-container > div.leaflet-top.leaflet-right > div > div > span > span');
            statDiv.empty().text(count);
            statDiv.removeClass('ajp-minimap-geotagging-user-multiple-people');
            statDiv.removeClass('ajp-minimap-geotagging-user-single-person');
            if (count > 1) {
                statDiv.addClass('ajp-minimap-geotagging-user-multiple-people');
            } else {
                statDiv.addClass('ajp-minimap-geotagging-user-single-person');
            }
            statDiv.addClass('ajp-minimap-geotagging-user-active');
        } else {
            statDiv.find('span').empty().text(count);
        }
    };

    $(document).on('click', '.ajp-minimap-confirm-geotag-button', function () {
        var $this = $(this);
        if (!$this.hasClass('ajp-minimap-confirm-geotag-button-done')) {
            var photoId = $(this).data('id');
            $.post(window.confirmLocationURL, {
                photo: photoId,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            }, function (response) {
                $this.addClass('ajp-minimap-confirm-geotag-button-done');
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

    $(document).on('click', '.ajp-minimap-start-guess-CTA-button', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal CTA specify location click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal CTA specify location click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Photo modal CTA specify location click']);
        }
        if (window.isGame) {
            $('.ajp-game-specify-location-button')[0].click();
        } else {
            window.startGuessLocation($(this).data('id'));
        }
    });

    window.resizeMinimap = function () {
        var mapContainer = $('#ajp-photo-modal-map-container'),
            modalPhoto = $('#ajp-modal-photo'),
            photoviewPhoto = $('#ajp-photoview-main-photo');
            mapContainer.css('height', (photoviewPhoto.height() || modalPhoto.height()) + 'px');
    };

    window.positionMinimapCTAButton = function () {
        var mapCanvas = $('#ajp-photo-modal-map-canvas');
        $('.ajp-minimap-start-guess-CTA-button').css('margin-left', ((mapCanvas.width() / 2) - 35) + 'px')
            .css('margin-top', ((mapCanvas.height() / 2) - 35) + 'px');
    };

    window.showPhotoMapIfApplicable = function (isPhotoview) {
        var arrowIcon = {
                path: 'M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z',
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
                path: 'M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z',
                strokeColor: 'white',
                strokeOpacity: 1,
                strokeWeight: 1,
                fillColor: 'black',
                fillOpacity: 1,
                scale: 1.5,
                anchor: new google.maps.Point(12, 18)
            },
            currentIcon;
        var container = $('#ajp-modal-photo-container'),
            mapContainer = $('#ajp-photo-modal-map-container');
        if (!window.isMobile && mapContainer.length > 0 && ((!photoModalRephotoArray ||
            photoModalRephotoArray.length === 0 || userClosedRephotoTools) && (!photoModalSimilarPhotoArray || photoModalSimilarPhotoArray.length == 0 && userClosedSimilarPhotoTools))) {
            if (isPhotoview) {
                mapContainer.css('height', $('#ajp-photoview-main-photo').height());
            } else {
                mapContainer.show().css('height', container.height());
            }
            if (!window.photoModalPhotoLat && !window.photoModalPhotoLng) {
                $('#ajp-minimap-disabled-overlay').show();
            } else {
                $('#ajp-minimap-disabled-overlay').hide();
            }
            var center,
                minimapLargeCTAButton,
                minimapLargeCTAButtonIcon;
            if (!window.photoModalPhotoLat && !window.photoModalPhotoLng) {
                minimapLargeCTAButton = document.createElement('button');
                minimapLargeCTAButtonIcon = document.createElement('i');
                $(minimapLargeCTAButtonIcon).addClass('material-icons notranslate').html('add_location');
                $(minimapLargeCTAButton).addClass('ajp-minimap-start-guess-CTA-button')
                    .attr('title', gettext('Pick the shooting location!')).append(minimapLargeCTAButtonIcon);
                $('.ajp-minimap-start-guess-CTA-button').remove();
                var mapCanvas = $('#ajp-photo-modal-map-canvas');
                $(minimapLargeCTAButton).attr('data-id', window.currentlyOpenPhotoId);
                mapContainer.append(minimapLargeCTAButton);
                window.positionMinimapCTAButton();
                $('.ajp-minimap-geotagging-user-number').remove();
                var minimapGeotaggingUserNumber = document.createElement('div');
                var minimapGeotaggingUserNumberSpan = document.createElement('span');
                $(minimapGeotaggingUserNumberSpan).text(window.photoModalGeotaggingUserCount);
                $(minimapGeotaggingUserNumber).addClass('ajp-minimap-geotagging-user-number').addClass('no-location')
                    .prop('title', gettext('Geotagged by this many users'));
                $(minimapGeotaggingUserNumberSpan).addClass('pr-2');
                minimapGeotaggingUserNumber.appendChild(minimapGeotaggingUserNumberSpan);
                var minimapGeotaggingUserIcon = document.createElement('div');
                minimapGeotaggingUserNumber.appendChild(minimapGeotaggingUserIcon);
                if (window.photoModalGeotaggingUserCount < 2) {
                    $(minimapGeotaggingUserIcon).addClass('ajp-minimap-geotagging-user-single-person');
                } else {
                    $(minimapGeotaggingUserIcon).addClass('ajp-minimap-geotagging-user-multiple-people');
                }
                if (window.photoModalUserHasGeotaggedThisPhoto) {
                    $(minimapGeotaggingUserIcon).addClass('ajp-minimap-geotagging-user-active');
                }
                mapContainer.append(minimapGeotaggingUserNumber);
                window.miniMap = null;
            } else {
                center = {
                    lat: window.photoModalPhotoLat,
                    lng: window.photoModalPhotoLng
                };
                window.miniMap = new google.maps.Map(document.getElementById('ajp-photo-modal-map-canvas'), {
                    center: center,
                    zoom: 17,
                    mapTypeControl: false,
                    mapTypeId: 'OSM'
                });
                minimapLargeCTAButton = null;
                $('.ajp-minimap-start-guess-CTA-button').remove();
                var minimapConfirmGeotagButton = document.createElement('button');
                $(minimapConfirmGeotagButton).addClass('btn').addClass('btn-light')
                    .addClass('ajp-minimap-confirm-geotag-button')
                    .data('id', window.currentlyOpenPhotoId).data('trigger', 'hover')
                    .data('placement', 'top').data('toggle', 'popover')
                    .data('content', gettext('Confirm correct location'))
                    .html('<i class="material-icons notranslate">beenhere</i>').popover();
                if (window.photoModalUserHasConfirmedThisLocation) {
                    $(minimapConfirmGeotagButton).addClass('ajp-minimap-confirm-geotag-button-done');
                }
                window.miniMap.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(minimapConfirmGeotagButton);
                var minimapStartGuessButton = document.createElement('button');
                $(minimapStartGuessButton).addClass('btn').addClass('btn-light')
                    .addClass('ajp-minimap-start-guess-button')
                    .data('trigger', 'hover')
                    .data('placement', 'top').data('toggle', 'popover')
                    .data('content', gettext('Submit your own location'))
                    .html('<i class="material-icons notranslate">edit_location</i>').popover();
                window.miniMap.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(minimapStartGuessButton);
                $('.ajp-minimap-geotagging-user-number').remove();
                var minimapGeotaggingUserNumber = document.createElement('div');
                var minimapGeotaggingUserNumberSpan = document.createElement('span');
                $(minimapGeotaggingUserNumberSpan).text(window.photoModalGeotaggingUserCount);
                $(minimapGeotaggingUserNumber).addClass('ajp-minimap-geotagging-user-number dropdown pr-2')
                    .prop('title', gettext('Geotagged by this many users'));
                minimapGeotaggingUserNumber.appendChild(minimapGeotaggingUserNumberSpan);
                var minimapGeotaggingUserIcon = document.createElement('div');
                $(minimapGeotaggingUserIcon).addClass('dropdown-toggle').attr('data-toggle', 'dropdown');
                minimapGeotaggingUserNumber.appendChild(minimapGeotaggingUserIcon);
                if (window.photoModalGeotaggingUserCount < 2) {
                    $(minimapGeotaggingUserIcon).addClass('ajp-minimap-geotagging-user-single-person');
                } else {
                    $(minimapGeotaggingUserIcon).addClass('ajp-minimap-geotagging-user-multiple-people');
                }
                if (window.photoModalUserHasGeotaggedThisPhoto) {
                    $(minimapGeotaggingUserIcon).addClass('ajp-minimap-geotagging-user-active');
                }
                if (window.photoModalFirstGeotaggers) {
                    var dropdown = $([
                        '<ul class="dropdown-menu dropdown-menu-right" id="ajp-mini-map-geotaggers-dropdown" aria-labelledby="dropdownMenu1">',
                        '</ul>'
                    ].join('\n'));
                    if (window.photoModalUserHasGeotaggedThisPhoto) {
                        $(dropdown).append($('<li class="ajp-minimap-geotagger-list-item"><a href="#">' + gettext('You') + '</a></li>'));
                    } else {
                        if (window.photoModalFirstGeotaggers.length === 0) {
                            if (window.photoModalGeotaggingUserCount === 1) {
                                $(dropdown).append($('<li class="ajp-minimap-geotagger-list-item" data-lat="' + window.photoModalPhotoLat + '" data-lng="' + window.photoModalPhotoLng + '"><a href="#">' + gettext('Anonymous user') + '</a></li>'));
                            } else {
                                $(dropdown).append($('<li class="ajp-minimap-geotagger-list-item" data-lat="' + window.photoModalPhotoLat + '" data-lng="' + window.photoModalPhotoLng + '"><a href="#">' + gettext('Anonymous users') + '</a></li>'));
                            }
                        }
                    }
                    $(minimapGeotaggingUserNumber).append(dropdown);
                    $.each(window.photoModalFirstGeotaggers, function (k, v) {
                        $(dropdown).append($('<li class="ajp-minimap-geotagger-list-item" data-lat="' + v[1] + '" data-lng="' + v[2] + '"><a href="#">' + v[0] + '</a></li>'));
                    });
                }
                window.miniMap.controls[google.maps.ControlPosition.TOP_RIGHT].push(minimapGeotaggingUserNumber);
                window.miniMap.mapTypes.set('OSM', new google.maps.ImageMapType({
                    getTileUrl: function (coord, zoom) {
                        return 'https://a.tile.openstreetmap.org/' + zoom + '/' + coord.x + '/' + coord.y + '.png';
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
                    var arrowIconRotation;
                    arrowIconRotation = window.photoModalPhotoAzimuth;
                    // TODO: Why do we even need such magic? Should get to the bottom of our azimuth calculation problems
                    if (angleFix < 0 && arrowIconRotation > 0) {
                        arrowIconRotation += angleFix;
                    }
                    arrowIcon.rotation = arrowIconRotation;
                    currentIcon = arrowIcon;
                    window.minimapDottedAzimuthLine = new google.maps.Polyline({
                        geodesic: false,
                        strokeOpacity: 0,
                        icons: [
                            {
                                icon: {
                                    path: dottedAzimuthLineSymbol,
                                    strokeOpacity: 1,
                                    strokeWeight: 1.5,
                                    strokeColor: 'red',
                                    scale: 0.75
                                },
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
                    currentIcon = locationIcon;
                }
                if (window.photoModalPhotoLat && window.photoModalPhotoLng) {
                    if (window.miniMapMarker) {
                        window.miniMapMarker.setIcon(currentIcon);
                        window.miniMapMarker.setPosition(new google.maps.LatLng(window.photoModalPhotoLat, window.photoModalPhotoLng));
                        window.miniMapMarker.setMap(window.miniMap);
                    } else {
                        window.miniMapMarker = new google.maps.Marker({
                            position: new google.maps.LatLng(window.photoModalPhotoLat, window.photoModalPhotoLng),
                            map: window.miniMap,
                            title: gettext('Current location'),
                            icon: currentIcon
                        });
                    }
                }
                if (!window.miniMapStreetView) {
                    window.miniMapStreetView = window.miniMap.getStreetView();
                }
                google.maps.event.clearListeners(window.miniMapStreetView, 'visible_changed');
                google.maps.event.addListener(window.miniMapStreetView, 'visible_changed', function () {
                    if (window.miniMapMarker) {
                        if (window.miniMapStreetView.getVisible()) {
                            window.miniMapMarker.setIcon(locationIcon);
                        } else {
                            if (window.photoModalPhotoAzimuth) {
                                window.miniMapMarker.setIcon(arrowIcon);
                            }
                        }
                    }
                });
            }
        }
    };

    $(window).resize(function () {
        if(!$('#ajp-modal-rephoto-container').is(':visible') && !$('#ajp-modal-similar-photo-container').is(':visible') && !window.isMobile){
            window.resizeMinimap();
        }
        if(isMapview){
            if(window.outerWidth < 769){
                if(mapOpts.mapTypeControlOptions.style !== 2) {
                    mapOpts.mapTypeControlOptions.position = 9;
                    mapOpts.mapTypeControlOptions.style = 2;
                    map.setOptions(mapOpts);
                }
            } else {
                if(mapOpts.mapTypeControlOptions.style !== 0){
                    mapOpts.mapTypeControlOptions.style = 0;
                    mapOpts.mapTypeControlOptions.position = 11;
                    map.setOptions(mapOpts);
                }
            }
        }
        window.positionMinimapCTAButton();
    });

    $(document).on('click', '.ajp-album-selection-item', function (e) {
        e.preventDefault();
        var $this = $(this);
        window.albumId = $this.data('id');
        handleAlbumChange();
    });

    $(document).on('click', '#ajp-photo-modal-discuss', function (e) {
        e.preventDefault();
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal discuss click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal discuss click']);
        }
        var commentsSection = $('#ajp-comments-section');
        if (commentsSection.hasClass('d-none')) {
            commentsSection.removeClass('d-none');
            window.FB.XFBML.parse($('#ajp-rephoto-comments').get(0));
            window.FB.XFBML.parse($('#ajp-original-photo-comments').get(0));
        } else {
            commentsSection.addClass('d-none');
        }
    });

    $('#ajp-comment-form-register-link').click(function (e) {
        e.preventDefault();
        window.openPhotoUploadModal();
    });

    $(document).on('click', '.ajp-photo-modal-rephoto-thumb', function () {
        var targetId = $(this).data('id'),
            infoDiv = $('#ajp-photo-rephoto-info-column'),
            photoDiv = $('#ajp-modal-rephoto-container'),
            fullscreenDiv = $('#ajp-rephoto-full-screen-image');
        if (!targetId) {
            targetId = currentlySelectedRephotoId;
        }
        infoDiv.show();
        for (var i = 0; i < window.photoModalRephotoArray.length; i += 1) {
            if (window.photoModalRephotoArray[i].id == targetId) {
                fullscreenDiv.attr('data-src', window.photoModalRephotoArray[i].fullscreen_url);
                photoDiv.html(tmpl('ajp-photo-modal-rephoto-template', [window.photoModalRephotoArray,i]));
                infoDiv.html(tmpl('ajp-photo-modal-rephoto-info-template', window.photoModalRephotoArray[i]));
                currentlySelectedRephotoId = targetId;
                var commentsDiv = $('#ajp-rephoto-comments');
                commentsDiv.find('.fb-comments').attr('data-href', window.photoModalRephotoArray[i].fb_url);
                window.FB.XFBML.parse();
                if (!window.isFrontpage && !window.isSelection) {
                    window.syncMapStateToURL();
                }
                break;
            }
        }
    });
    $(document).on('click', '.ajp-show-rephoto-selection-overlay-button', function () {
        $(this).hide();
        userClosedRephotoTools = false;
        $('.ajp-close-similar-photo-overlay-button').click();
        userClosedSimilarPhotoTools = true;
        var rephotoColumn = $('#ajp-photo-modal-rephoto-column'),
            rephotoInfoColumn = $('#ajp-photo-rephoto-info-column'),
            rephotoDiv = $('#ajp-modal-rephoto-container'),
            originalPhotoColumn = $('#ajp-photo-modal-original-photo-column'),
            originalPhotoInfoColumn = $('#ajp-photo-modal-original-photo-info-column');
            
            originalPhotoInfoColumn.removeClass('col-lg-12').addClass('col-lg-6');
        originalPhotoColumn.removeClass('col-lg-12').addClass('col-lg-6');
        rephotoInfoColumn.show();
        rephotoColumn.show();
        currentlySelectedRephotoId = window.photoModalRephotoArray[0]['id'];
        rephotoDiv.html(tmpl('ajp-photo-modal-rephoto-template', [window.photoModalRephotoArray,0]));
        rephotoInfoColumn.html(tmpl('ajp-photo-modal-rephoto-info-template', window.photoModalRephotoArray[0]));
        $('#ajp-photo-modal-map-container').hide();
        if (!window.isFrontpage && !window.isSelection) {
            window.syncMapStateToURL();
        }
    });
    $(document).on('click', '.ajp-photo-modal-similar-photo-thumb', function () {
        $('#ajp-similar-photo-full-screen-image').removeClass('ajp-photo-bw')
        var targetId = $(this).data('id'),
            infoDiv = $('#ajp-photo-modal-similar-photo-info-column'),
            photoDiv = $('#ajp-modal-similar-photo-container'),
            similarFullScreen = $('#ajp-similar-photo-full-screen-image');
        if (!targetId) {
            targetId = currentlySelectedSimilarPhotoId;
        }
        infoDiv.show();
        for (var i = 0; i < window.photoModalSimilarPhotoArray.length; i += 1) {
            if (window.photoModalSimilarPhotoArray[i].id == targetId) {
                similarFullScreen.attr('data-src', window.photoModalSimilarPhotoArray[i].fullscreen_url);
                photoDiv.html(tmpl('ajp-photo-modal-similar-photo-template', [window.photoModalSimilarPhotoArray,i]));
                infoDiv.html(tmpl('ajp-photo-modal-similar-photo-info-template', window.photoModalSimilarPhotoArray[i]));
                currentlySelectedSimilarPhotoId = targetId;
                window.FB.XFBML.parse();
                if (!window.isFrontpage && !window.isSelection) {
                    window.syncMapStateToURL();
                }
                break;
            }
        }
    });
    $(document).on('click', '.ajp-show-similar-photo-selection-overlay-button', function () {
        $(this).hide();
        userClosedSimilarPhotoTools = false;
        $('.ajp-close-rephoto-overlay-button').click();
        userClosedRephotoTools = true;
        var similarPhotoColum = $('#ajp-photo-modal-similar-photo-column'),
            similarPhotoInfoColumn = $('#ajp-photo-modal-similar-photo-info-column'),
            similarPhotoDiv = $('#ajp-modal-similar-photo-container'),
            originalPhotoColumn = $('#ajp-photo-modal-original-photo-column'),
            originalPhotoInfoColumn = $('#ajp-photo-modal-original-photo-info-column');
            
        if (window.photoModalSimilarPhotoArray !== undefined && window.photoModalSimilarPhotoArray.length > 1) {
            $('#ajp-similar-photo-selection').show();
        }

        originalPhotoInfoColumn.removeClass('col-lg-12').addClass('col-lg-6');
        originalPhotoColumn.removeClass('col-lg-12').addClass('col-lg-6');
        similarPhotoInfoColumn.show();
        similarPhotoColum.show();
        currentlySelectedSimilarPhotoId = window.photoModalSimilarPhotoArray[0]['id'];
        similarPhotoDiv.html(tmpl('ajp-photo-modal-similar-photo-template', [window.photoModalSimilarPhotoArray,0]));
        similarPhotoInfoColumn.html(tmpl('ajp-photo-modal-similar-photo-info-template', window.photoModalSimilarPhotoArray[0]));
        $('#ajp-photo-modal-map-container').hide();
        if (!window.isFrontpage && !window.isSelection) {
            window.syncMapStateToURL();
        }
    });
    $(document).on('click', '#ajp-photo-source', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Source link click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Source link click']);
        }
    });
    $(document).on('click', '#ajp-photo-modal-rephoto-source', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Rephoto source link click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Rephoto source link click']);
        }
    });
    $(document).on('click', '.ajp-close-rephoto-overlay-button', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $('#ajp-photo-modal-rephoto-column').hide();
        $('#ajp-rephoto-selection').hide();
        $('.ajp-show-rephoto-selection-overlay-button').show('fade', 250);
        $('#ajp-grab-link').find('a').attr('href', window.hostname + window.originalPhotoAbsoluteURL).text(window.hostname + window.originalPhotoAbsoluteURL);
        var originalPhotoColumn = $('#ajp-photo-modal-original-photo-column');
        var originalPhotoInfoColumn = $('#ajp-photo-modal-original-photo-info-column');
        if (!window.isMapview) {
            originalPhotoColumn.removeClass('col-lg-6').addClass('col-lg-12');
            originalPhotoInfoColumn.removeClass('col-lg-12').addClass('col-lg-6');
        }
        $('#ajp-photo-rephoto-info-column').hide();
        currentlySelectedRephotoId = false;
        if (!window.isFrontpage && !window.isPhotoview && !window.isSelection) {
            window.syncMapStateToURL();
        }
        userClosedRephotoTools = true;
        if (window.showPhotoMapIfApplicable) {
            window.showPhotoMapIfApplicable();
        } else {
            if (window.photoModalPhotoLat && window.photoModalPhotoLng) {
                originalPhotoColumn.removeClass('col-lg-12').addClass('col-lg-6');
            }
        }
    });
    $(document).on('click', '.ajp-close-similar-photo-overlay-button', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $('#ajp-photo-modal-similar-photo-column').hide();
        $('#ajp-similar-photo-selection').hide();
        $('.ajp-show-similar-photo-selection-overlay-button').show('fade', 250);
        $('#ajp-grab-link').find('a').attr('href', window.hostname + window.originalPhotoAbsoluteURL).text(window.hostname + window.originalPhotoAbsoluteURL);
        var originalPhotoColumn = $('#ajp-photo-modal-original-photo-column');
        var originalPhotoInfoColumn = $('#ajp-photo-modal-original-photo-info-column');
        if (!window.isMapview) {
            originalPhotoColumn.removeClass('col-lg-6').addClass('col-lg-12');
            originalPhotoInfoColumn.removeClass('col-lg-12').addClass('col-lg-6');
        }
        $('#ajp-photo-modal-similar-photo-info-column').hide();
        currentlySelectedSimilarPhotoId = false;
        if (window.isFrontpage || window.isPhotoview || window.isSelection) {

        } else {
            window.syncMapStateToURL();
        }
        userClosedSimilarPhotoTools = true;
        if (window.showPhotoMapIfApplicable) {
            window.showPhotoMapIfApplicable();
        } else {
            if (window.photoModalPhotoLat && window.photoModalPhotoLng) {
                originalPhotoColumn.removeClass('col-lg-12').addClass('col-lg-6');
            }
        }
    });
    $(document).on('click', '#ajp-grab-link', function (e) {
        e.stopPropagation();
    });
    $(document).on('click', '#ajp-comment-tabs li', function () {
        window.FB.XFBML.parse($('#ajp-rephoto-comments').get(0));
        window.FB.XFBML.parse($('#ajp-original-photo-comments').get(0));
    });
    $(document).on('click', '.ajp-thumbnail-selection-icon', function (e) {
        e.stopPropagation();
        var $this = $(this),
            other = $(".ajp-frontpage-image-container[data-id='" + $this.data('id') + "']").find('.ajp-thumbnail-selection-icon');
        if ($this.hasClass('ajp-thumbnail-selection-icon-blue')) {
            $this.removeClass('ajp-thumbnail-selection-icon-blue');
        } else {
            $this.addClass('ajp-thumbnail-selection-icon-blue');
        }
        if ($this.parent().attr('id') === 'ajp-modal-photo-container') {
            if (other) {
                if (other.hasClass('ajp-thumbnail-selection-icon-blue')) {
                    other.removeClass('ajp-thumbnail-selection-icon-blue');
                } else {
                    other.addClass('ajp-thumbnail-selection-icon-blue');
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
                target = $('#ajp-header-selection-indicator');
            if (len > 0) {
                target.removeClass('d-none');
            } else {
                target.addClass('d-none');
            }
            target.find('span').html(len);
        });
    });
    window.openPhotoUploadModal = function () {
        if (window.currentlyOpenPhotoId) {
            $.ajax({
                cache: false,
                url: window.photoUploadModalURL + window.currentlyOpenPhotoId + '/',
                success: function (result) {
                    var rephotoUploadModal = $('#ajp-rephoto-upload-modal');
                    rephotoUploadModal.data('bs.modal', null);
                    rephotoUploadModal.html(result).modal();
                }
            });
        }
    };
    // Hover on dynamic elements doesn't work...
    $(document).on('mouseenter', '.ajp-frontpage-image-container', function () {
        $(this).find('.ajp-thumbnail-selection-icon').show('fade', 250);
    });
    $(document).on('mouseleave', '.ajp-frontpage-image-container', function () {
        var icon = $(this).find('.ajp-thumbnail-selection-icon');
        if (!icon.hasClass('ajp-thumbnail-selection-icon-blue')) {
            $(this).find('.ajp-thumbnail-selection-icon').hide('fade', 250);
        }
    });
    $(document).on('mouseenter', '.ajp-thumbnail-selection-icon', function (e) {
        $(this).show();
    });
    $(document.body).delegate('.ajp-frontpage-image-container', 'hover', function () {
        $(this).find('.ajp-thumbnail-selection-icon').show('fade', 250);
    }, function () {
        var icon = $(this).find('.ajp-thumbnail-selection-icon');
        if (!icon.hasClass('ajp-thumbnail-selection-icon-blue')) {
            $(this).find('.ajp-thumbnail-selection-icon').hide('fade', 250);
        }
    });
    $(document).on('click', '#ajp-photo-modal-add-rephoto', function (e) {
        e.preventDefault();
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
                    targetDiv = $('#ajp-curator-change-album-parent');
                }
                targetDiv.empty();
                targetDiv.append(
                    tmpl(
                        'ajp-curator-my-album-select-option',
                        {id: -1, name: gettext('Not selected')}
                    )
                );
                for (var i = 0, l = response.length; i < l; i += 1) {
                    if (!response[i].open) {
                        targetDiv.append(tmpl('ajp-curator-my-album-select-option', response[i]));
                    }
                }
                targetDiv.append(tmpl('ajp-curator-my-album-select-separator', {}));
                for (i = 0, l = response.length; i < l; i += 1) {
                    if (response[i].open) {
                        targetDiv.append(tmpl('ajp-curator-my-album-select-option', response[i]));
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
                var targetDiv = $('#ajp-curator-album-select');
                targetDiv.empty();
                targetDiv.append(
                    tmpl(
                        'ajp-curator-my-album-select-option',
                        {id: -1, name: gettext('Not selected')}
                    )
                );
                for (var i = 0, l = response.length; i < l; i += 1) {
                    if (!response[i].open) {
                        targetDiv.append(tmpl('ajp-curator-my-album-select-option', response[i]));
                    }
                }
                targetDiv.append(tmpl('ajp-curator-my-album-select-separator', {}));
                for (i = 0, l = response.length; i < l; i += 1) {
                    if (response[i].open) {
                        targetDiv.append(tmpl('ajp-curator-my-album-select-option', response[i]));
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
    $(document).on('click', '#ajp-photo-modal-share', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal share click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal share click']);
        }
    });
    $(document).on('click', '#ajp-sift-pics-link', function () {
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
                var modalWindow = $('#ajp-full-leaderboard-modal');
                modalWindow.find('.scoreboard').html(response);
                modalWindow.find('.score-container').show();
                window.hideScoreboard();
                modalWindow.modal();
            }
        });
        _gaq.push(['_trackEvent', '', 'Full leaderboard']);
    });
    $(document).on('click', '#ajp-info-window-leaderboard-link', function (e) {
        e.preventDefault();
        window.albumId = $(this).data('id');
        $('#full_leaderboard').click();
    });

    $(document).on('click', '.ajp-invert-similar-photo-overlay-button', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var targetDiv = $('#ajp-modal-similar-photo');
        var fullSCreen = $('#ajp-similar-photo-full-screen-image');
        if (targetDiv.hasClass('ajp-photo-bw')) {
            targetDiv.removeClass('ajp-photo-bw');
        } else {
            targetDiv.addClass('ajp-photo-bw');
        }
        if (fullSCreen.hasClass('ajp-photo-bw')) {
            fullSCreen.removeClass('ajp-photo-bw');
        } else {
            fullSCreen.addClass('ajp-photo-bw');
        }
    });

    $(document).on('click', '.ajp-invert-rephoto-overlay-button', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var targetDiv = $('#ajp-modal-rephoto');
        var fullSCreen = $('#ajp-rephoto-full-screen-image');
        if (targetDiv.hasClass('ajp-photo-bw')) {
            targetDiv.removeClass('ajp-photo-bw');
        } else {
            targetDiv.addClass('ajp-photo-bw');
        }
        if (fullSCreen.hasClass('ajp-photo-bw')) {
            fullSCreen.removeClass('ajp-photo-bw');
        } else {
            fullSCreen.addClass('ajp-photo-bw');
        }
    });

    $(document).on('click', '#ajp-header-about-button', function (e) {
        $('#ajp-loading-overlay').show();
        var targetDiv = $('#ajp-general-info-modal');
        if (window.generalInfoModalURL) {
            $.ajax({
                url: window.generalInfoModalURL,
                success: function (resp) {
                    targetDiv.html(resp).modal();
                },
                complete: function () {
                    $('#ajp-loading-overlay').hide();
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

    $(document).on('focus', '#id_comment', function () {
        $('.ajp-photo-modal-previous-button').addClass('ajp-photo-modal-previous-button-disabled').addClass('disabled');
        $('.ajp-photo-modal-next-button').addClass('ajp-photo-modal-next-button-disabled').addClass('disabled');
    });

    $(document).on('blur', '#id_comment', function () {
        $('.ajp-photo-modal-previous-button').removeClass('ajp-photo-modal-previous-button-disabled').removeClass('disabled');
        $('.ajp-photo-modal-next-button').removeClass('ajp-photo-modal-next-button-disabled').removeClass('disabled');
    });

    $(document).on('click', '.ajp-photo-modal-previous-button', function (e) {
        var $this = $(this);
        if (!isPhotoview) {
            e.preventDefault();  
            $('#ajp-rephoto-full-screen-image').hasClass('ajp-photo-bw');
            $('#ajp-similar-photo-full-screen-image').removeClass('ajp-photo-bw');
            if (!$this.hasClass('ajp-photo-modal-previous-button-disabled')) {
                var previousId = $('#ajp-frontpage-image-container-' + currentlyOpenPhotoId).prev().data('id');
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
        } else {
            if ($this.hasClass('ajp-photo-modal-previous-button-disabled')) {
                e.preventDefault();
            } else {
                _gaq.push(['_trackEvent', 'Photoview', 'Previous']);
            }
        }
    });

    $(document).on('click', '.ajp-flip-photo-overlay-button', function () {
        var target = $('#ajp-modal-photo'),
            fullScreenImage = $('#ajp-full-screen-image');
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
        } else {
            $(this).addClass('active');
        }
        if (target.hasClass('ajp-photo-flipped')) {
            target.removeClass('ajp-photo-flipped');
        } else {
            target.addClass('ajp-photo-flipped');
        }
        if (fullScreenImage.hasClass('ajp-photo-flipped')) {
            fullScreenImage.removeClass('ajp-photo-flipped');
        } else {
            fullScreenImage.addClass('ajp-photo-flipped');
        }
        window.flipPhoto();
    });

    $(document).on('click', '.ajp-like-photo-overlay-button', function () {
        var $this = $(this),
            $i = $this.find('i'),
            $likeCount = $this.find('.ajp-like-count');
        $.post(photoLikeURL, {
            photo: window.currentlyOpenPhotoId,
            csrfmiddlewaretoken: docCookies.getItem('csrftoken')
        }, function (response) {
            if (response.level === 0) {
                $i.html('favorite_border');
                $this.removeClass('active big');
            } else if (response.level === 1) {
                $i.html('favorite');
                $this.addClass('active');
            } else if (response.level === 2) {
                $i.html('favorite');
                $this.addClass('big');
            }
            $likeCount.html(response.likeCount);
            $('#ajp-frontpage-show-liked-link').removeClass('disabled');
        });
    });

    $(document).on('click', '.ajp-photo-modal-next-button', function (e) {
        if (!isPhotoview) {
            e.preventDefault();
            if (!$(this).hasClass('ajp-photo-modal-next-button-disabled')) {
                var nextId = $('#ajp-frontpage-image-container-' + currentlyOpenPhotoId).next().data('id');
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
        } else {
            if ($(this).hasClass('ajp-photo-modal-next-button-disabled')) {
                e.preventDefault();
            } else {
                _gaq.push(['_trackEvent', 'Photoview', 'Next']);
            }

        }
    });

    $(document).on('click', '#ajp-reverse-side-button', function (e) {
        if(!window.isPhotoview) {
            e.preventDefault();
            if (window.currentPhotoReverseId) {
                window.loadPhoto(window.currentPhotoReverseId);
            }
        }
    });

    $(document).on('click', '#ajp-rotate-photo-button', function () {
        var photoContainer = $('#ajp-modal-photo');
        var photoFullScreenContainer = $('#ajp-full-screen-image-wrapper');
        if(isPhotoview) {
            photoContainer = $('#ajp-photoview-main-photo');
        }

        disableAnnotations();

        if (photoContainer.hasClass('rotate90')) {
            photoContainer.removeClass('rotate90').addClass('rotate180');
            photoContainer.css({'padding-bottom': '', 'padding-top': ''});
            photoContainer.css({'padding-right': '', 'padding-left': ''});
            photoFullScreenContainer.removeClass('rotate90').addClass('rotate180');
        }
        else if(photoContainer.hasClass('rotate180')) {
            var photoContainerPadding = (1 - photoContainer.height() / photoContainer.width()) * 50;
            if(photoContainerPadding > 0) {
                photoContainer.attr('style', 'padding-bottom: calc(5px + ' + photoContainerPadding + '%) !important;padding-top: calc(5px + ' + photoContainerPadding + '%) !important');
            } else {
                var photoContainerPadding = (1 - photoContainer.width() / photoContainer.height()) * 50;
                photoContainer.attr('style', 'padding-left: calc(5px + ' + photoContainerPadding + '%) !important;padding-right: calc(5px + ' + photoContainerPadding + '%) !important');
            }
            photoContainer.removeClass('rotate180').addClass('rotate270');
            photoFullScreenContainer.removeClass('rotate180').addClass('rotate270');
        }
        else if(photoContainer.hasClass('rotate270')) {
            photoContainer.removeClass('rotate270');
            photoContainer.css({'padding-bottom': '', 'padding-top': ''});
            photoContainer.css({'padding-right': '', 'padding-left': ''});
            photoFullScreenContainer.removeClass('rotate270');

            enableAnnotations();
        }
        else {
            var photoContainerPadding = (1 - photoContainer.height() / photoContainer.width()) * 50;
            if(photoContainerPadding > 0) {
                photoContainer.attr('style', 'padding-bottom: calc(5px + ' + photoContainerPadding + '%) !important;padding-top: calc(5px + ' + photoContainerPadding + '%) !important');
            } else {
                var photoContainerPadding = (1 - photoContainer.width() / photoContainer.height()) * 50;
                photoContainer.attr('style', 'padding-left: calc(5px + ' + photoContainerPadding + '%) !important;padding-right: calc(5px + ' + photoContainerPadding + '%) !important');
            }
            photoContainer.addClass('rotate90');
            photoFullScreenContainer.addClass('rotate90');
        }
    });

    $(document).on('click', '.ajp-photo-album-link', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Album link click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Album link click']);
        }
    });

    $(document).on('click', '#ajp-photo-modal-specify-location, .ajp-minimap-start-guess-button', function (e) {
        e.preventDefault();
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal specify location click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal specify location click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Photo modal specify location click']);
        }
        window.startGuessLocation($(this).data('id'));
    });

    $(document).on('click', '#ajp-photo-modal-start-dating-button', function (e) {
        e.preventDefault();
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal date photo click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal date photo click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Photo modal date photo click']);
        }
        window.startDater($(this).data('id'));
    });
    
    $(document).on('click', '#ajp-photoview-transcribe-button', function (e) {
        e.preventDefault();
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal date photo click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Map', 'Photo modal date photo click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Photo modal date photo click']);
        }
        window.startTranscriber($(this).data('id'));
    });

    $(document).on('click', '#ajp-photo-modal-close-button', function (e) {
        e.preventDefault();
        window.closePhotoDrawer();
    });

    $(document).on('change', '#ajp-curator-create-new-album-checkbox', function () {
        var $this = $(this),
            creationFields = $('.ajp-curator-new-album-creation-field'),
            existingFields = $('.ajp-curator-add-to-existing-album-field');
        if ($this.is(':checked')) {
            creationFields.show();
            existingFields.hide();
        } else {
            creationFields.hide();
            existingFields.show();
        }
    });

    $(document).on('keyup', '#ajp-curator-album-filter', function () {
        var filter = $(this).val().toLowerCase();
        if (filter === '') {
            $('option').show();
        } else {
            $('#ajp-curator-album-select').find('option').each(function () {
                if ($(this).text().toLowerCase().indexOf(filter) > -1) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        }
    });

    $(document).on('hidden.bs.modal', '#ajp-choose-albums-modal', function () {
        $('#ajp-curator-album-filter').val(null);
    });

    addFullScreenExitListener();

    $(document).on('click', '#ajp-header-album-more', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var targetDiv = $('#ajp-info-modal');
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
                        window.FB.XFBML.parse($('#ajp-info-modal-like').get(0));
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

    $(document).on('click', '.ajp-album-selection-album-more-button, .ajp-photo-modal-album-more-button', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var targetDiv = $('#ajp-info-modal');
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
                        window.FB.XFBML.parse($('#ajp-info-modal-like').get(0));
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

    $('.ajp-bank-link-standing').click(function () {
        if (window.reportDonationStandingBankLinkClick) {
            window.reportDonationStandingBankLinkClick($(this).data('bank'));
        }
    });

    $('.ajp-bank-link-one-time').click(function () {
        if (window.reportDonationOneTimeBankLinkClick) {
            window.reportDonationOneTimeBankLinkClick($(this).data('bank'));
        }
    });

    $('.ajp-email-login-button').click(function () {
        if (window.reportEmailLoginClick) {
            window.reportEmailLoginClick();
        }
    });

    $('#ajp-email-register-button').click(function () {
        if (window.reportEmailRegisterClick) {
            window.reportEmailRegisterClick();
        }
    });

    $('.google-connect').click(function () {
        if (window.reportGooglePlusLoginClick) {
            window.reportGooglePlusLoginClick();
        }
    });

    $(document).on('click', '.ajp-change-language-link', function (e) {
        e.preventDefault();
        $('#ajp-language').val($(this).attr('data-lang-code'));
        $('input[name=csrfmiddlewaretoken]').val(docCookies.getItem('csrftoken'));
        if( window.location !== undefined && window.location.search !== undefined ) {
            $('input[name=next]').val(window.location.pathname + window.location.search)
        }
        $('#ajp-change-language-form').submit();
    });

    $(document).on('click', '#ajp-filter-closest-link', function (e) {
        e.preventDefault();
        getGeolocation(window.handleGeolocation);
    });

    $(document).on('click', '.ajp-album-info-modal-album-link', function () {
        if (window.isFrontpage) {
            _gaq.push(['_trackEvent', 'Gallery', 'Album info album link click']);
        } else if (window.isGame) {
            _gaq.push(['_trackEvent', 'Game', 'Album info album link click']);
        } else if (window.isMapview) {
            _gaq.push(['_trackEvent', 'Mapview', 'Album info album link click']);
        }
    });

    $(document).on('click', '#ajp-mapview-close-streetview-button', function () {
        map.getStreetView().setVisible(false);
    });

    $(document).on('click', '#ajp-filtering-help', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $('#ajp-filtering-tutorial-modal').modal();
    });

    $(document).on('click', '.ajp-minimap-geotagger-list-item', function (e) {
        e.preventDefault();
        //var $this = $(this);
        //window.miniMap.setCenter(new google.maps.LatLng($this.data('lat'), $this.data('lng')));
    });

    $(document).on('click', '#ajp-close-filtering-tutorial-modal', function (e) {
        e.stopPropagation();
        $('#ajp-filtering-tutorial-modal').modal('hide');
    });

    $(document).on('click', '.ajp-photo-modal-photo-curator', function () {
        $(this).find('p').toggleClass('d-none');
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

    $('#ajp-mode-select').find('a').click(function (e) {
        if (!window.isFrontpage && !window.isSelection) {
            e.preventDefault();
            var $this = $(this),
                selectedMode = $this.data('mode');
            if ($this.hasClass('disabled')) {
                return false;
            }
            switch (selectedMode) {
                case 'pictures':
                    window.location.href = '/?order1=time&order2=added&page=1';
                    break;
                case 'albums':
                    window.location.href = '/';
                    break;
                case 'likes':
                    window.location.href = '/?order1=time&order2=added&page=1&myLikes=1';
                    break;
                case 'rephotos':
                    window.location.href = '/?order1=time&order2=added&page=1&rephotosBy=' + window.currentProfileId;
                    break;
            }
        }
    });

    $(document).on('click', '#ajp-photo-selection-create-album-button,.ajp-photo-modal-album-icon', function () {
        if(!window.currentProfileEmail){
            window.openPhotoUploadModal();
            return;
        }
        $('#ajp-choose-albums-modal').modal();
        window.loadSelectableAlbums();
        window.loadPossibleParentAlbums();
    });

    $(document).on('click', '#ajp-curator-confirm-album-selection-button', function () {
        if(window.location.pathname.indexOf('curator') > -1) {
            return;
        }
        var albums =  $('#id-albums').val(),
            allIds = [],
            i,
            l;
        if(window.isSelection && !$('#ajp-photo-modal').is(':visible')){
            var allElements = $('.ajp-photo-selection-thumbnail-link');
            for (i = 0, l = allElements.length; i < l; i += 1) {
                allIds.push($(allElements[i]).data('id'));
            }
        }
        else {
            allIds = [];
            var photoId = window.currentlySelectedPhotoId;
            photoId ? allIds.push(photoId) : allIds.push(window.currentlyOpenPhotoId)
        }
        $('#ajp-loading-overlay').show();
        $.ajax({
            type: 'POST',
            url: '/upload-selection/',
            data: {
                selection: JSON.stringify(allIds),
                albums: albums,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            },
            success: function (response) {
                $('#ajp-loading-overlay').hide();
                if (response.error) {
                    $('#ajp-curator-upload-error').show();
                    $('#ajp-curator-upload-error-message').html(response.error);
                    $('#ajp-selection-top-panel').find('.alert-error').html(response.error).removeClass('d-none');
                    $('#ajp-selection-top-panel').find('.alert-success').html('').addClass('d-none');
                } else {
                    $('#ajp-selection-top-panel').find('.alert-error').html('').addClass('d-none');
                    $('#ajp-selection-top-panel').find('.alert-success').html(response.message).removeClass('d-none');
                    $('#ajp-curator-upload-error').hide();
                    $('#ajp-curator-upload-error-message').html(window.gettext('System error'));
                    $('#ajp-choose-albums-modal').modal('hide');
                    $('#ajp-curator-add-album-name').val(null);
                    $('#ajp-curator-add-area-name-hidden').val(null);
                    $('#ajp-curator-add-area-name').val(null);
                    window.areaLat = null;
                    window.areaLng = null;
                    window.loadPossibleParentAlbums();
                    window.loadSelectableAlbums();
                }
                window.loadSelectableAlbums();
                window._gaq.push(['_trackEvent', 'Selection', 'Upload success']);
            },
            error: function () {
                $('#ajp-loading-overlay').hide();
                $('#ajp-curator-upload-error').show();
                $('#ajp-selection-top-panel').find('.alert-error').html(window.gettext('System error')).removeClass('d-none');
                window._gaq.push(['_trackEvent', 'Selection', 'Upload error']);
            }
        });
    });

    $(document).on('click', '#ajp-photo-modal-map-canvas > div.leaflet-control-container > div.leaflet-top.leaflet-right, .ajp-minimap-geotagging-user-number, #ajp-geotagger-stats-container > i, #ajp-geotagger-stats-container > span', function (event) {
        var targetDiv = $('#ajp-geotaggers-modal');
        $('#ajp-loading-overlay').show();
        if (window.geotaggersListURL && window.currentlyOpenPhotoId) {
            let url = window.geotaggersListURL.replace('0', window.currentlyOpenPhotoId);
            $.ajax({
                url,
                success: function (resp) {
                    targetDiv.html(resp).modal();
                },
                complete: function () {
                    $('#ajp-loading-overlay').hide();
                }
            });
        }
    });

    $(document).on('click', '#ajp-comment-list a[data-action="like"],a[data-action="dislike"]', function (event) {
        event.preventDefault();
        var link = $(this);
        $.post(link.prop('href'), {
            csrfmiddlewaretoken: docCookies.getItem('csrftoken')
        }, function (response, status) {
            if (status === 'success') {
                update_comment_likes(link);
            }
        });
        return false;
    });

    $(document).on('click', 'a', function () {
        if (!window.audioContext) {
            window.audioContext = new AudioContext();
            if (window.audioContext.state !== 'running') {
                window.audioContext.resume();
            }
        }
    });

    $(document).on('mouseenter', '.annotation-label', function(el) {
        $(el.target).addClass('d-none');
    });

    $(document).on('mouseleave', '.ajp-modal-photo-container, .ajp-photo', function() {
        $('.annotation-label').removeClass('d-none');
    });

    $(document).on('mouseenter', '.ajp-face-rectangle', function(el) {
        if($(el.target).children()) {
            $($(el.target).children()[0]).removeClass('d-none');
        }
    });

    window.backClick = function() {
        if (document.referrer.indexOf(window.location.origin) == 0) {
            history.go(-1); return false;
        }
        else { window.location.href = '/'; }
    };
}(jQuery));
