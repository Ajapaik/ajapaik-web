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
            realMapElement,
            mapClickListenerActive,
            mapDragstartListenerActive,
            mapIdleListenerActive,
            mapMousemoveListenerActive,
            placeEstimatedLocationMarker,
            guessLocationStarted = false,
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

        placeEstimatedLocationMarker = function (position) {
            estimatedLocationMarker = new google.maps.Marker({
                position: position,
                map: window.map,
                title: gettext("The peoples' guess"),
                draggable: false,
                icon: '/static/images/ajapaik_marker_35px.png'
            });
        };

        realMapElement = $("#ajapaik-map-canvas")[0];
        realMapElement.addEventListener('mousewheel', window.wheelEventNonFF, true);
        realMapElement.addEventListener('DOMMouseScroll', window.wheelEventFF, true);

        window.handleGuessResponse = function (guessResponse) {
            window.updateLeaderboard();
            // TODO: How broken are GA events?
            //if (resp['is_correct'] == true) {
            //    _gaq.push(['_trackEvent', 'Grid', 'Correct coordinates']);
            //} else if (resp['location_is_unclear']) {
            //    _gaq.push(['_trackEvent', 'Grid', 'Coordinates uncertain']);
            //} else if (resp['is_correct'] == false) {
            //    _gaq.push(['_trackEvent', 'Grid', 'Wrong coordinates']);
            //}
            noticeDiv = $('#ajapaik-grid-guess-notice-container');
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
            $('#ajapaik-grid-map-geotag-count').html(guessResponse.heatmapPoints.length);
            $('#ajapaik-grid-map-geotag-with-azimuth-count').html(guessResponse.tagsWithAzimuth);
            $('.ajapaik-save-location-button').hide();
            var playerLatlng = new google.maps.LatLng(marker.getPosition().lat(), marker.getPosition().lng());
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
            if (guessResponse.newEstimatedLocation) {
                placeEstimatedLocationMarker(new google.maps.LatLng(guessResponse.newEstimatedLocation[0], guessResponse.newEstimatedLocation[1]));
            }
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
                    $('#ajapaik-map-container').show();
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
                    mapOptions.streetPanorama = new google.maps.StreetViewPanorama(document.getElementById('ajapaik-map-canvas'), streetViewOptions);
                    window.map = new google.maps.Map(document.getElementById('ajapaik-map-canvas'), mapOptions);
                    if (result.estimated_location) {
                        placeEstimatedLocationMarker(new google.maps.LatLng(result.estimated_location[0], result.estimated_location[1]));
                    }
                    if (estimatedLocationMarker) {
                        window.map.setCenter(estimatedLocationMarker.getPosition());
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

        window.startGuessLocation = function () {
            if (!guessLocationStarted) {
                //window.showHeatmap();
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
                $('.ajapaik-save-location-button').show();
                if (window.map) {
                    if (!mapClickListenerActive) {
                        google.maps.event.addListener(window.map, 'click', window.mapClickListenerFunction);
                        mapClickListenerActive = true;
                    }
                    if (!mapIdleListenerActive) {
                        google.maps.event.addListener(window.map, 'idle', window.mapIdleListenerFunction);
                        mapIdleListenerActive = true;
                    }
                    if (!mapDragstartListenerActive) {
                        google.maps.event.addListener(window.map, 'dragstart', window.mapDragstartListenerFunction);
                        mapDragstartListenerActive = true;
                    }
                    if (!mapMousemoveListenerActive) {
                        google.maps.event.addListener(window.map, 'mousemove', window.mapMousemoveListenerFunction);
                        mapMousemoveListenerActive = true;
                    }
                }
                google.maps.event.addListener(window.map, 'drag', function () {
                    firstDragDone = true;
                });
                google.maps.event.addListener(marker, 'position_changed', function () {
                    disableSave = false;
                });
                $('#ajapaik-map-container').show();
                $('#ajapaik-photo-modal').modal('toggle');
                google.maps.event.trigger(window.map, 'resize');
                guessLocationStarted = true;
            }
        };

        $('.ajapaik-grid-close-map-button').click(function () {
            guessLocationStarted = false;
            $('#photo-drawer').show();
            $('#ajapaik-grid-guess-photo').hide();
            $('#ajapaik-grid-guess-photo-back').hide();
            $('#ajapaik-map-container').hide();
        });

//        $('#ajapaik-grid-guess-photo').hover(function () {
//            now = new Date().getTime();
//            if (((lastMapHoverPhotoHide + 1000) < now) || !lastMapHoverPhotoHide) {
//                $(this).hide();
//                lastMapHoverPhotoHide = new Date().getTime();
//            }
//        });
//
//        $('#ajapaik-grid-guess-photo-back').hover(function () {
//            $('#ajapaik-grid-guess-photo').show();
//        });

        doGridAjaxQuery = function () {
            var i,
                newA,
                newImg;
            if (!ajaxQueryInProgress && window.start <= window.totalPhotoCount) {
                ajaxQueryInProgress = true;
                $.ajax({
                    cache: false,
                    url: '/grid_infinity/',
                    data: {city: window.cityId, start: window.start},
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
                $('#ajapaik-grid-no-more-photos-message').show();
            }
        };

        if (galleryDiv.innerHeight() < $(window).height()) {
            window.start += window.pageSize;
            doGridAjaxQuery();
        }

        openPhotoDrawer = function (content) {
            $('#ajapaik-photo-modal').html(content).modal().find('img').on('load', function () {
                $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
            });
        };

        window.closePhotoDrawer = function () {
            $('#ajapaik-photo-modal').modal('toggle');
            $('.filter-box').show();
        };

        window.loadPhoto = function (id) {
            //$.post('/log_user_map_action/', {user_action: 'opened_drawer', photo_id: id}, function () {
            //    $.noop();
            //});
            photoId = id;
            $.ajax({
                cache: false,
                url: '/foto/' + id + '/',
                success: function (result) {
                    openPhotoDrawer(result);
                    if (FB !== undefined) {
                        FB.XFBML.parse();
                    }
                }
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

        $('.ajapaik-save-location-button').on('click', function (e) {
            firstDragDone = false;
            e.preventDefault();
            if (disableSave) {
                _gaq.push(['_trackEvent', 'Game', 'Forgot to move marker']);
                alert(gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view.'));
            } else {
                // TODO: Flip status
                window.saveLocation(marker, currentlyOpenPhotoId, false, true, false, degreeAngle, azimuthLineEndPoint);
                if (saveDirection) {
                    _gaq.push(['_trackEvent', 'Game', 'Save location and direction']);
                } else {
                    _gaq.push(['_trackEvent', 'Game', 'Save location only']);
                }
            }
        });

        $('.ajapaik-grid-close-guess-notice-button').on('click', function () {
            noticeDiv.hide();
        });
    });
}());