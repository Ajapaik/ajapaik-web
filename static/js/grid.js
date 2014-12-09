(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global docCookies */
    /*global History */
    /*global FB */
    /*global _gaq */
    /*global document */
    /*global window */
    /*global setTimeout */
    /*global screen */
    /*global google */
    /*global gettext */
    /*global isMobile */
    /*global saveLocationURL */
    $(document).ready(function () {
        var galleryDiv = $('#gallery'),
            doGridAjaxQuery,
            ajaxQueryInProgress = false,
            loadMoreLink = $('#ajapaik-grid-load-more-link'),
            photoDrawerElement = $('#photo-drawer'),
            openPhotoDrawer,
            closePhotoDrawer,
            photoId,
            marker,
            radianAngle,
            degreeAngle,
            azimuthLineEndPoint,
            azimuthListenerActive = true,
            firstDragDone = false,
            saveDirection = false,
            disableSave = true,
            centerMarker,
            mapClickListenerFunction,
            mapDragstartListenerFunction,
            mapIdleListenerFunction,
            mapMousemoveListenerFunction,
            mapClickListenerActive,
            mapDragstartListenerActive,
            mapIdleListenerActive,
            mapMousemoveListenerActive,
            moveOrCreateHeatmapEstimatedLocationMarker,
            guessLocationStarted = false,
            saveLocation,
            noticeDiv,
            estimatedLocation,
            estimatedLocationMarker,
            currentlyOpenPhotoId,
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
            mapOptions = {
                zoom: 14,
                center: new google.maps.LatLng(59, 26),
                mapTypeControl: true,
                panControl: true,
                panControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_TOP
                },
                zoomControl: true,
                zoomControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_TOP
                },
                streetViewControl: true,
                streetViewControlOptions: {
                    position: google.maps.ControlPosition.RIGHT_TOP
                }
            },
            lastMapHoverPhotoHide,
            now;

        galleryDiv.justifiedGallery({
            rowHeight: 120,
            waitThumbnailsLoad: false,
            margins: 3,
            sizeRangeSuffixes: {
                'lt100': '',
                'lt240': '',
                'lt320': '',
                'lt500': '',
                'lt640': '',
                'lt1024': ''
            }
        });

        $.ajaxSetup({
            headers: { 'X-CSRFToken': docCookies.getItem('csrftoken') }
        });

        moveOrCreateHeatmapEstimatedLocationMarker = function (position) {
            if (estimatedLocationMarker) {
                estimatedLocationMarker.setPosition(position);
            } else {
                estimatedLocationMarker = new google.maps.Marker({
                    position: position,
                    map: window.map,
                    title: gettext("The peoples' guess"),
                    draggable: false,
                    icon: '/static/images/ajapaik_marker_35px.png'
                });
            }
        };

        saveLocation = function () {
            var lat = marker.getPosition().lat(),
                lon = marker.getPosition().lng(),
                data = {
                    photo_id: currentlyOpenPhotoId,
                    hint_used: true,
                    non_game_guess: true,
                    zoom_level: window.map.zoom
                };

            if (lat && lon) {
                data.lat = lat;
                data.lon = lon;
            }

            if (saveDirection) {
                data.azimuth = degreeAngle;
                data.azimuth_line_end_point = azimuthLineEndPoint;
            }

            //if (userFlippedPhoto) {
            //    data.flip = !photos[currentPhotoIdx - 1].flip;
            //}

            $.post(saveLocationURL, data, function (resp) {
                if (resp['is_correct'] == true) {
                    _gaq.push(['_trackEvent', 'Grid', 'Correct coordinates']);
                } else if (resp['location_is_unclear']) {
                    _gaq.push(['_trackEvent', 'Grid', 'Coordinates uncertain']);
                } else if (resp['is_correct'] == false) {
                    _gaq.push(['_trackEvent', 'Grid', 'Wrong coordinates']);
                }
                noticeDiv = $('#ajapaik-grid-guess-notice');
                noticeDiv.modal();
                marker.setMap(null);
                $(".center-marker").hide();
                mapMousemoveListenerActive = false;
                google.maps.event.clearListeners(window.map, 'mousemove');
                mapIdleListenerActive = false;
                google.maps.event.clearListeners(window.map, 'idle');
                mapClickListenerActive = false;
                google.maps.event.clearListeners(window.map, 'click');
                mapDragstartListenerActive = false;
                google.maps.event.clearListeners(window.map, 'dragstart');
                $('#ajapaik-grid-map-geotag-count').html(resp.heatmap_points.length);
                $('#ajapaik-grid-map-geotag-with-azimuth-count').html(resp.azimuth_tags);
                $('.ajapaik-grid-save-location-button').hide();
                var playerLatlng = new google.maps.LatLng(data.lat, data.lon);
                var markerImage = {
                    url: 'http://maps.gstatic.com/intl/en_ALL/mapfiles/drag_cross_67_16.png',
                    origin: new google.maps.Point(0, 0),
                    anchor: new google.maps.Point(8, 8),
                    scaledSize: new google.maps.Size(16, 16)
                };
                var playerMarker = new google.maps.Marker({
                    position: playerLatlng,
                    map: window.map,
                    title: gettext("Your guess"),
                    draggable: false,
                    icon: markerImage
                });
                if (resp.new_estimated_location) {
                    moveOrCreateHeatmapEstimatedLocationMarker(new google.maps.LatLng(resp.new_estimated_location[0], resp.new_estimated_location[1]));
                }
            }, 'json');
        };

        window.showHeatmap = function (photoId) {
            guessLocationStarted = false;
            $('.ajapaik-grid-guess-location-button').show();
            $.ajax({
                cache: false,
                url: '/heatmap_data/',
                data: {photo_id: photoId},
                success: function (result) {
                    var points = [],
                        heatmap,
                        i,
                        newLatLng,
                        latLngBounds = new google.maps.LatLngBounds(),
                        guessPhoto,
                        guessPhotoBack,
                        mainPhoto,
                        totalGeotags = result.heatmap_points.length,
                        geotagsWithAzimuth = 0;
                    $('#ajapaik-grid-map-container').show();
                    for (i = 0; i < totalGeotags; i += 1) {
                        newLatLng = new google.maps.LatLng(result.heatmap_points[i][0], result.heatmap_points[i][1]);
                        points.push(newLatLng);
                        latLngBounds.extend(newLatLng);
                        if (result.heatmap_points[i][2]) {
                            geotagsWithAzimuth += 1;
                        }
                    }
                    $('#ajapaik-grid-map-geotag-count').html(totalGeotags);
                    $('#ajapaik-grid-map-geotag-with-azimuth-count').html(geotagsWithAzimuth);
                    points = new google.maps.MVCArray(points);
                    heatmap = new google.maps.visualization.HeatmapLayer({
                        data: points
                    });
                    heatmap.setOptions({radius: 50, dissipating: true});
                    mapOptions.streetPanorama = new google.maps.StreetViewPanorama(document.getElementById('ajapaik-grid-map-canvas'), streetViewOptions);
                    window.map = new google.maps.Map(document.getElementById('ajapaik-grid-map-canvas'), mapOptions);
                    if (result.estimated_location) {
                        moveOrCreateHeatmapEstimatedLocationMarker(new google.maps.LatLng(result.estimated_location[0], result.estimated_location[1]));
                    }
                    if (estimatedLocationMarker) {
                        window.map.setCenter(estimatedLocation);
                        window.map.setZoom(17);
                    } else {
                        window.map.fitBounds(latLngBounds);
                    }
                    heatmap.setMap(window.map);
                    guessPhoto = $('#ajapaik-grid-guess-photo');
                    mainPhoto = $('#ajapaik-block-photoview-main-photo');
                    guessPhoto.attr('src', mainPhoto.attr('src'));
                    guessPhoto.show();
                    guessPhotoBack = $('#ajapaik-grid-guess-photo-back');
                    guessPhotoBack.attr('src', mainPhoto.attr('src'));
                    guessPhotoBack.show();
                    $('#photo-drawer').hide();
                }
            });
        };

        mapClickListenerFunction = function (e) {
            radianAngle = window.getAzimuthBetweenMouseAndMarker(e, marker);
            azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
            degreeAngle = Math.degrees(radianAngle);
            if (azimuthListenerActive) {
                mapMousemoveListenerActive = false;
                google.maps.event.clearListeners(window.map, 'mousemove');
                saveDirection = true;
                $('.ajapaik-grid-save-location-button').text(gettext('Save location and direction'));
                window.dottedAzimuthLine.icons[0].repeat = '2px';
                window.dottedAzimuthLine.setPath([marker.position, e.latLng]);
                window.dottedAzimuthLine.setVisible(true);
            } else {
                if (!mapMousemoveListenerActive) {
                    google.maps.event.addListener(window.map, 'mousemove', mapMousemoveListenerFunction);
                    mapMousemoveListenerActive = true;
                    google.maps.event.trigger(window.map, 'mousemove', e);
                }
            }
            azimuthListenerActive = !azimuthListenerActive;
        };

        mapMousemoveListenerFunction = function (e) {
            // The mouse is moving, therefore we haven't locked on a direction
            $('.ajapaik-grid-save-location').text(gettext('Save location only'));
            saveDirection = false;
            radianAngle = window.getAzimuthBetweenMouseAndMarker(e, marker);
            degreeAngle = Math.degrees(radianAngle);
            if (!isMobile) {
                window.dottedAzimuthLine.setPath([marker.position, e.latLng]);
                window.dottedAzimuthLine.setMap(window.map);
                window.dottedAzimuthLine.icons = [
                    {icon: window.dottedAzimuthLineSymbol, offset: '0', repeat: '7px'}
                ];
                window.dottedAzimuthLine.setVisible(true);
            } else {
                window.dottedAzimuthLine.setVisible(false);
            }
        };

        mapDragstartListenerFunction = function () {
//            if (mobileMapMinimized) {
//                toggleTouchPhotoView();
//            }
            window.dottedAzimuthLine.setVisible(false);
            centerMarker
                .css('background-image', 'url("/static/images/ajapaik_marker_35px_cross.png")')
                .css('margin-left', '-17px')
                .css('margin-top', '-55px')
                .css('height', '60px');
            $('.ajapaik-grid-save-location-button').text(gettext('Save location only'));
            azimuthListenerActive = false;
            window.dottedAzimuthLine.setVisible(false);
            mapMousemoveListenerActive = false;
            google.maps.event.clearListeners(window.map, 'mousemove');
        };

        mapIdleListenerFunction = function () {
            if (firstDragDone) {
                marker.position = window.map.center;
                azimuthListenerActive = true;
                centerMarker
                    .css('background-image', 'url("http://maps.gstatic.com/intl/en_ALL/mapfiles/drag_cross_67_16.png")')
                    .css('margin-left', '-8px')
                    .css('margin-top', '-9px');
                if (!mapMousemoveListenerActive) {
                    google.maps.event.addListener(window.map, 'mousemove', mapMousemoveListenerFunction);
                    mapMousemoveListenerActive = true;
                }
            }
        };

        window.startGuessLocation = function () {
            if (!guessLocationStarted) {
                marker = new google.maps.Marker({
                    map: window.map,
                    draggable: false,
                    position: window.map.getCenter(),
                    visible: false
                });
                marker.bindTo('position', window.map, 'center');
                $('<div/>').addClass('center-marker').appendTo(window.map.getDiv()).click(function () {
                    var that = $(this);
                    if (!that.data('win')) {
                        that.data('win').bindTo('position', window.map, 'center');
                    }
                    that.data('win').open(window.map);
                });
                centerMarker = $('.center-marker');
                $('.ajapaik-grid-guess-location-button').hide();
                $('.ajapaik-grid-save-location-button').show();
                if (window.map) {
                    if (!mapClickListenerActive) {
                        google.maps.event.addListener(window.map, 'click', mapClickListenerFunction);
                        mapClickListenerActive = true;
                    }
                    if (!mapIdleListenerActive) {
                        google.maps.event.addListener(window.map, 'idle', mapIdleListenerFunction);
                        mapIdleListenerActive = true;
                    }
                    if (!mapDragstartListenerActive) {
                        google.maps.event.addListener(window.map, 'dragstart', mapDragstartListenerFunction);
                        mapDragstartListenerActive = true;
                    }
                    if (!mapMousemoveListenerActive) {
                        google.maps.event.addListener(window.map, 'mousemove', mapMousemoveListenerFunction);
                        mapMousemoveListenerActive = true;
                    }
                }
                google.maps.event.addListener(window.map, 'drag', function () {
                    firstDragDone = true;
                });
                google.maps.event.addListener(marker, 'position_changed', function () {
                    disableSave = false;
                });
                guessLocationStarted = true;
            }
        };

        $('.ajapaik-grid-close-map-button').click(function () {
            $('#photo-drawer').show();
            $('#ajapaik-grid-guess-photo').hide();
            $('#ajapaik-grid-guess-photo-back').hide();
            $('#ajapaik-grid-map-container').hide();
        });

        $('#ajapaik-grid-guess-photo').hover(function () {
            now = new Date().getTime();
            if (((lastMapHoverPhotoHide + 1000) < now) || !lastMapHoverPhotoHide) {
                $(this).hide();
                lastMapHoverPhotoHide = new Date().getTime();
            }
        });

        $('#ajapaik-grid-guess-photo-back').hover(function () {
            $('#ajapaik-grid-guess-photo').show();
        });

        doGridAjaxQuery = function () {
            var i,
                newA,
                newImg;
            if (!ajaxQueryInProgress && window.start <= window.totalPhotoCount) {
                ajaxQueryInProgress = true;
                $.ajax({
                    cache: false,
                    url: '/grid_infinity/',
                    data: {city__pk: window.cityId, start: window.start},
                    success: function (result) {
                        for (i = 0; i < result.length; i += 1) {
                            newA = document.createElement('a');
                            newImg = document.createElement('img');
                            $(newA).addClass('ajapaik-grid-image-container').attr('href', result[i][1]);
                            $(newImg).attr('src', '').attr('data-src', result[i][1]).attr('width', result[i][2])
                                .attr('height', result[i][3]).attr('alt', result[i][0])
                                .addClass('lazyload').addClass('ajapaik-grid-image')
                                .attr('data-id', result[i][0]);
                            newA.appendChild(newImg);
                            $('#gallery').append(newA);
                        }
                        window.start += window.pageSize;
                        galleryDiv.justifiedGallery('norewind');
                        setTimeout(function () { $('.ajapaik-grid-image-container').css('opacity', 1); }, 100);
                        ajaxQueryInProgress = false;
                        $('.ajapaik-grid-image').on('click', function (e) {
                            e.preventDefault();
                            window.loadPhoto(e.target.dataset.id);
                        });
                        if (galleryDiv.innerHeight() < ($(window).height() * 1.5)) {
                            doGridAjaxQuery();
                        }
                    }
                });
            }
            if (window.start > window.totalPhotoCount) {
                loadMoreLink.hide();
                $('#ajapaik-grid-no-more-photos').show();
            }
        };

        if (galleryDiv.innerHeight() < $(window).height()) {
            window.start += window.pageSize;
            doGridAjaxQuery();
        }

        openPhotoDrawer = function (content) {
            photoDrawerElement.html(content);
            photoDrawerElement.animate({ top: '0' });
        };

        closePhotoDrawer = function () {
            var historyReplacementString = '/grid/?city__pk=' + window.cityId;
            photoDrawerElement.animate({ top: '-1000px' });
            $('.filter-box').show();
            History.replaceState(null, null, historyReplacementString);
        };

        window.loadPhoto = function (id) {
            $.post('/log_user_map_action/', {user_action: 'opened_drawer', photo_id: id}, function () {
                $.noop();
            });
            photoId = id;
            $.ajax({
                cache: false,
                url: '/foto/' + id + '/',
                success: function (result) {
                    openPhotoDrawer(result);
                    if (FB !== undefined) {
                        FB.XFBML.parse();
                    }
                    currentlyOpenPhotoId = id;
//                    $('a.iframe').fancybox({
//                        'width': '75%',
//                        'height': '75%',
//                        'autoScale': false,
//                        'hideOnContentClick': false
//                    });
                }
            });
        };

        window.prepareFullscreen = function () {
            $('.full-box img').load(function () {
                var that = $(this),
                    aspectRatio = that.width() / that.height(),
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
            });
        };

        window.uploadCompleted = function (response) {
            $.modal.close();
            if (photoId === undefined) {
                if (response && response.new_id !== undefined && response.new_id) {
                    window.location.href = '/foto/' + response.new_id + '/';
                } else {
                    window.location.reload();
                }
            } else {
                closePhotoDrawer();
                if (response && response.new_id !== undefined && response.new_id) {
                    window.loadPhoto(response.new_id);
                } else {
                    window.loadPhoto(photoId);
                }
            }
        };

        window.flipPhoto = function (photoId) {
            var photoElement = $('a[rel=' + photoId + ']').find('img'),
                photoFullscreenElement = $('#full-large1').find('img');
            if (photoElement.hasClass('flip-photo')) {
                photoElement.removeClass('flip-photo');
            } else {
                photoElement.addClass('flip-photo');
            }
            if (photoFullscreenElement.hasClass('flip-photo')) {
                photoFullscreenElement.removeClass('flip-photo');
            } else {
                photoFullscreenElement.addClass('flip-photo');
            }
        };

        loadMoreLink.on('click', function (e) {
            e.preventDefault();
            doGridAjaxQuery();
        });

        $(window).scroll(function () {
            if ($(window).scrollTop() - ($(window).height()) > 0 && !ajaxQueryInProgress && window.start <= window.totalPhotoCount) {
                doGridAjaxQuery();
            }
        });

        $('.ajapaik-grid-image-container').on('click', function (e) {
            e.preventDefault();
            var targetId = e.target.dataset.id;
            window.loadPhoto(targetId);
        });

        $('.ajapaik-grid-image').on('click', function (e) {
            e.preventDefault();
            var targetId = e.target.dataset.id;
            window.loadPhoto(targetId);
        });

        $('.ajapaik-grid-save-location-button').on('click', function (e) {
            firstDragDone = false;
            e.preventDefault();
            if (disableSave) {
                _gaq.push(['_trackEvent', 'Game', 'Forgot to move marker']);
                alert(gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view.'));
            } else {
                saveLocation();
                if (saveDirection) {
                    _gaq.push(['_trackEvent', 'Game', 'Save location and direction']);
                } else {
                    _gaq.push(['_trackEvent', 'Game', 'Save location only']);
                }
            }
        });

        $('.ajapaik-grid-close-notice-button').on('click', function (e) {
            noticeDiv.hide();
        });

        photoDrawerElement.delegate('#ajapaik-close-photo-drawer', 'click', function (e) {
            e.preventDefault();
            closePhotoDrawer();
        });

        photoDrawerElement.delegate('a.add-rephoto', 'click', function (e) {
            e.preventDefault();
            $('#notice').modal();
            _gaq.push(['_trackEvent', 'Map', 'Add rephoto']);
        });

        photoDrawerElement.delegate('#random-photo', 'click', function (e) {
            e.preventDefault();
            var imagesOnPage = $('.ajapaik-grid-image');
            window.loadPhoto(imagesOnPage[Math.floor(Math.random() * imagesOnPage.length)].dataset.id);
        });
    });
}());