(function ($) {
    'use strict';

    $(document).ready(function () {
        var galleryDiv = $('#gallery'),
            doGridAjaxQuery,
            ajaxQueryInProgress = false,
            loadMoreLink = $('#ajapaik-grid-load-more-link'),
            openPhotoDrawer,
            photoId,
            disableSave = true,
            noticeDiv,
            nonFFWheelListener,
            ffWheelListener,
            guessPhotoPanelContent,
            currentPhotoWidth,
            guessPhotoPanel,
            feedbackPanel,
            photoPanel;

        window.saveLocationButton = $('.ajapaik-save-location-button');
        window.realMapElement = $('#ajapaik-map-canvas')[0];
        window.mapInfoPanelGeotagCountElement = $('#ajapaik-grid-map-geotag-count');
        window.mapInfoPanelAzimuthCountElement = $('#ajapaik-grid-map-geotag-with-azimuth-count');

        $('.ajapaik-marker-center-lock-button').hide();
        $('.ajapaik-show-tutorial-button').hide();

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

        window.realMapElement.addEventListener('mousewheel', window.wheelEventNonFF, true);
        window.realMapElement.addEventListener('DOMMouseScroll', window.wheelEventFF, true);

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
            noticeDiv = $('#ajapaik-grid-feedback-js-panel-content');
            if (guessResponse.hideFeedback) {
                noticeDiv.find('#ajapaik-grid-guess-feedback-difficulty-prompt').hide();
                noticeDiv.find('#ajapaik-grid-guess-feedback-difficulty-form').hide();
                noticeDiv.find('#ajapaik-grid-guess-feedback-points-gained').hide();
            }
            noticeDiv.find('#ajapaik-grid-guess-feedback-message').html(guessResponse.feedbackMessage);
            noticeDiv.find('#ajapaik-grid-guess-feedback-points-gained').text(window.gettext('Points awarded') + ': ' + guessResponse.currentScore);
            feedbackPanel = $.jsPanel({
                selector: '#ajapaik-map-container',
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
                id: 'ajapaik-grid-feedback-panel'
            }).css('top', 'auto').css('left', 'auto');
            if (guessResponse.heatmapPoints && guessResponse.newEstimatedLocation) {
                window.mapDisplayHeatmapWithEstimatedLocation(guessResponse);
            }
            /*window.updateLeaderboard();
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
            window.saveLocationButton.hide();
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
            }*/
        };

        window.startGuessLocation = function () {
            if (!window.guessLocationStarted) {
                window.guessLocationStarted = true;
                $('#ajapaik-map-container').show();
                $('#ajapaik-grid-map-info-panel').show();
                $('.ajapaik-marker-center-lock-button').show();
                $('.ajapaik-show-tutorial-button').show();
                window.marker = new window.google.maps.Marker({
                    map: window.map,
                    draggable: false,
                    position: window.map.getCenter(),
                    visible: false,
                    icon: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg'
                });
                window.map.set('scrollwheel', false);
                nonFFWheelListener = window.realMapElement.addEventListener('mousewheel', window.wheelEventNonFF, true);
                ffWheelListener = window.realMapElement.addEventListener('DOMMouseScroll', window.wheelEventFF, true);
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
                guessPhotoPanelContent = $('#ajapaik-grid-guess-photo-js-panel-content');
                guessPhotoPanelContent.find('img').prop('src', window.currentPhotoURL);
                if (!window.isMobile) {
                    $('.ajapaik-flip-photo-overlay-button').hide();
                    $('.ajapaik-fullscreen-overlay-button').hide();
                }
                window.google.maps.event.trigger(window.map, 'resize');
                currentPhotoWidth = $('#ajapaik-grid-guess-photo-container').find('img').width();
                guessPhotoPanel = $.jsPanel({
                    selector: '#ajapaik-map-container',
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
                    id: 'ajapaik-game-guess-photo-js-panel'
                });
                $(guessPhotoPanel).css('max-width', currentPhotoWidth + 'px');
                //photoPanel.close();
                $('#ajapaik-mapview-map-info-panel').show();
                $('#ajapaik-map-button-container').show();
                $('#ajapaik-map-button-container-xs').show();
                //mc.clearMarkers();
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

        window.stopGuessLocation = function () {
            $('#ajapaik-map-container').hide();
            $('#ajapaik-grid-guess-photo-js-panel-content').hide();
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
            photoPanel = undefined;
            $('.ajapaik-marker-center-lock-button').hide();
            $('.ajapaik-show-tutorial-button').hide();
            window.heatmapEstimatedLocationMarker.setMap(null);
            window.map.set('scrollwheel', true);
            window.realMapElement.removeEventListener(nonFFWheelListener);
            window.realMapElement.removeEventListener(ffWheelListener);
            if (!window.centerMarker) {
                window.centerMarker = $('.center-marker');
            }
            window.centerMarker.hide();
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
            $('#ajapaik-grid-map-info-panel').hide();
            $('#ajapaik-map-button-container').hide();
            $('#ajapaik-map-button-container-xs').hide();
            window.setCursorToAuto();
            window.dottedAzimuthLine.setMap(null);
            window.guessLocationStarted = false;
        };

        $('.ajapaik-grid-close-map-button').click(function () {
            window.guessLocationStarted = false;
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
                    data: {area: window.areaId, start: window.start},
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

        window.saveLocationButton.on('click', function () {
            window.firstDragDone = false;
            window.setCursorToAuto();
            if (disableSave) {
                window._gaq.push(['_trackEvent', 'Grid', 'Forgot to move marker']);
                window.alert(window.gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view.'));
            } else {
                // TODO: Flip data and stuff
                window.saveLocation(window.marker, photoId, null, true, null, window.degreeAngle, window.azimuthLineEndPoint, 'Grid');
                if (window.saveDirection) {
                    window._gaq.push(['_trackEvent', 'Grid', 'Save location and direction']);
                } else {
                    window._gaq.push(['_trackEvent', 'Grid', 'Save location only']);
                }
            }
        });

        $(document).on('click', '.ajapaik-grid-feedback-next-button', function () {
            var data = {
                level: $('input[name=difficulty]:checked', 'ajapaik-grid-guess-feedback-difficulty-form').val(),
                photo_id: photoId
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
    });
}(jQuery));