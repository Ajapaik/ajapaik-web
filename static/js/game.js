(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global google */
    /*global leaderboardFullURL */
    /*global start_location */
    /*global _gaq */
    /*global gettext */
    /*global isMobile */
    /*global $ */
    /*global URI */
    /*global BigScreen */

    var photos = [],
        currentPhotoIdx = 0,
        hintUsed = 0,
        mediaUrl = '',
        streamUrl = '/stream/',
        difficultyFeedbackURL = '/difficulty_feedback/',
        disableNext = false,
        disableSave = true,
        locationToolsOpen = false,
        guessResponseReceived = false,
        infowindow,
        photoContainer,
        noticeDiv,
        radianAngle,
        degreeAngle,
        azimuthLineEndPoint,
        azimuthListenerActive = true,
        firstDragDone = false,
        saveDirection = false,
        userFlippedPhoto = false,
        taxiData = [],
        pointArray,
        heatmap,
        playerMarker,
        mapClickListenerFunction,
        mapDragstartListenerFunction,
        mapIdleListenerFunction,
        mapMousemoveListenerFunction,
        mapClickListenerActive,
        mapDragstartListenerActive,
        mapIdleListenerActive,
        mapMousemoveListenerActive,
        marker,
        location,
        lastTriggeredWheeling,
        now,
        realMapElement,
        wheelEventFF,
        wheelEventNonFF,
        i,
        loadPhotos,
        playerLatlng,
        centerMarker = $('.center-marker'),
        nextPhoto,
        panoramaMarker,
        setCursorToPanorama,
        setCursorToAuto,
        guessPhotoPanel,
        feedbackPanel,
        jsPanelContent,
        saveLocationButton =  $('.ajapaik-game-save-location-button');

    setCursorToPanorama = function () {
        window.map.setOptions({draggableCursor: 'url(/static/images/material-design-icons/ajapaik_custom_size_panorama.svg) 18 18, auto', draggingCursor: 'auto'});
    };

    setCursorToAuto = function () {
        window.map.setOptions({draggableCursor: 'auto', draggingCursor: 'auto'});
    };

    mapClickListenerFunction = function (e) {
        if (infowindow !== undefined) {
            centerMarker.show();
            infowindow.close();
            infowindow = undefined;
        }
        radianAngle = window.getAzimuthBetweenMouseAndMarker(e, marker);
        azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
        degreeAngle = Math.degrees(radianAngle);
        if (isMobile) {
            window.dottedAzimuthLine.setPath([marker.position, Math.calculateMapLineEndPoint(degreeAngle, marker.position, 0.05)]);
            window.dottedAzimuthLine.setMap(window.map);
            window.dottedAzimuthLine.icons = [
                {icon: window.dottedAzimuthLineSymbol, offset: '0', repeat: '7px'}
            ];
            window.dottedAzimuthLine.setVisible(true);
        }
        if (azimuthListenerActive) {
            mapMousemoveListenerActive = false;
            google.maps.event.clearListeners(window.map, 'mousemove');
            saveDirection = true;
            saveLocationButton.removeAttr('disabled');
            saveLocationButton.removeClass('btn-default');
            saveLocationButton.removeClass('btn-warning');
            saveLocationButton.addClass('btn-success');
            saveLocationButton.text(gettext('Save location and direction'));
            window.dottedAzimuthLine.icons[0].repeat = '2px';
            window.dottedAzimuthLine.setPath([marker.position, e.latLng]);
            window.dottedAzimuthLine.setVisible(true);
            if (panoramaMarker) {
                panoramaMarker.setMap(null);
            }
            var markerImage = {
                url: '/static/images/material-design-icons/ajapaik_custom_size_panorama.svg',
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(18, 18),
                scaledSize: new google.maps.Size(36, 36)
            };
            panoramaMarker = new google.maps.Marker({
                map: window.map,
                draggable: false,
                position: e.latLng,
                icon: markerImage
            });
            setCursorToAuto();
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
        saveLocationButton.removeAttr('disabled');
        saveLocationButton.removeClass('btn-default');
        saveLocationButton.addClass('btn-warning');
        saveLocationButton.text(gettext('Save location only'));
        saveDirection = false;
        radianAngle = window.getAzimuthBetweenMouseAndMarker(e, marker);
        degreeAngle = Math.degrees(radianAngle);
        if (panoramaMarker) {
            panoramaMarker.setMap(null);
        }
        setCursorToPanorama();
        if (!isMobile) {
            window.dottedAzimuthLine.setPath([marker.position, Math.calculateMapLineEndPoint(degreeAngle, marker.position, 0.05)]);
            window.dottedAzimuthLine.setMap(window.map);
            window.dottedAzimuthLine.icons = [
                {icon: window.dottedAzimuthLineSymbol, offset: '0', repeat: '7px'}
            ];
            window.dottedAzimuthLine.setVisible(true);
        } else {
            window.dottedAzimuthLine.setVisible(false);
        }
    };

    mapIdleListenerFunction = function () {
        if (firstDragDone) {
            marker.position = window.map.center;
            azimuthListenerActive = true;
            if (!mapMousemoveListenerActive && !saveDirection) {
                google.maps.event.addListener(window.map, 'mousemove', mapMousemoveListenerFunction);
                mapMousemoveListenerActive = true;
            }
        }
    };

    mapDragstartListenerFunction = function () {
        centerMarker = $('.center-marker');
        saveDirection = false;
        if (panoramaMarker) {
            panoramaMarker.setMap(null);
        }
        setCursorToPanorama();
        window.dottedAzimuthLine.setVisible(false);
        if (infowindow !== undefined) {
            centerMarker.show();
            infowindow.close();
            infowindow = undefined;
        }
        saveLocationButton.removeAttr('disabled');
        saveLocationButton.removeClass('btn-default');
        saveLocationButton.addClass('btn-warning');
        saveLocationButton.text(gettext('Save location only'));
        azimuthListenerActive = false;
        window.dottedAzimuthLine.setVisible(false);
        mapMousemoveListenerActive = false;
        google.maps.event.clearListeners(window.map, 'mousemove');
    };

    // Our own custom zooming functions to fix the otherwise laggy zooming for mobile
    wheelEventFF = function (e) {
        now = new Date().getTime();
        if (!lastTriggeredWheeling) {
            lastTriggeredWheeling = now - 250;
        }
        if (now - 250 > lastTriggeredWheeling) {
            lastTriggeredWheeling = now;
            if (e.detail > 0) {
                window.map.setZoom(window.map.zoom + 1);
            } else {
                if (window.map.zoom > 14) {
                    window.map.setZoom(window.map.zoom - 1);
                }
            }
        }
    };

    wheelEventNonFF = function (e) {
        now = new Date().getTime();
        if (!lastTriggeredWheeling) {
            lastTriggeredWheeling = now - 100;
        }
        if (now - 100 > lastTriggeredWheeling) {
            lastTriggeredWheeling = now;
            if (e.wheelDelta > 0) {
                window.map.setZoom(window.map.zoom + 1);
            } else {
                if (window.map.zoom > 14) {
                    window.map.setZoom(window.map.zoom - 1);
                }
            }
        }
    };

    nextPhoto = function () {
        $('#ajapaik-game-photo-description').hide();
        photoContainer = $('#ajapaik-game-modal-photo-container');
        photoContainer.css('visibility', 'hidden');
        window.map.getStreetView().setVisible(false);
        hintUsed = 0;
        disableSave = true;
        locationToolsOpen = false;
        azimuthListenerActive = false;
        guessResponseReceived = false;
        window.map.setZoom(16);
        mapMousemoveListenerActive = false;
        saveLocationButton.removeClass('btn-primary').removeClass('btn-warning').removeClass('btn-success')
            .addClass('btn-default').text(gettext('Save location only')).attr('disabled', 'disabled');
        google.maps.event.clearListeners(window.map, 'mousemove');
        if (window.dottedAzimuthLine !== undefined) {
            window.dottedAzimuthLine.setVisible(false);
        }
        if (photos.length > currentPhotoIdx) {
            $('img').removeClass('ajapaik-photo-flipped');
            $('.btn').removeClass('active');
            $('#ajapaik-game-modal-photo').prop('src', mediaUrl + photos[currentPhotoIdx].big.url).on('load', function () {
                $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                photoContainer.css('visibility', 'visible');
            });
            if (photos[currentPhotoIdx].description) {
                $('#ajapaik-game-photo-description').html(photos[currentPhotoIdx].description);
                $('.ajapaik-game-show-description-button').show();
            } else {
                $('.ajapaik-game-show-description-button').hide();
            }
            $('#ajapaik-game-full-screen-image').prop('src', mediaUrl + photos[currentPhotoIdx].large.url);
            $('#ajapaik-game-full-screen-link').prop('rel', photos[currentPhotoIdx].id)
                .prop('href', mediaUrl + photos[currentPhotoIdx].large.url);
            $('#ajapaik-game-map-geotag-count').html(photos[currentPhotoIdx].total_geotags);
            $('#ajapaik-game-map-geotag-with-azimuth-count').html(photos[currentPhotoIdx].geotags_with_azimuth);
            window.prepareFullscreen(photos[currentPhotoIdx].large.size[0], photos[currentPhotoIdx].large.size[1]);
            disableNext = true;
        } else {
            loadPhotos(1);
        }
    };

    loadPhotos = function (next) {
        // IE needs a different URL, sending seconds
        var date = new Date(),
            qs = URI.parseQuery(window.location.search);
        if (marker) {
            marker.setMap(window.map);
            $('.center-marker').show();
        }

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

        if (heatmap) {
            heatmap.setMap(null);
        }

        if (playerMarker) {
            playerMarker.setMap(null);
        }

        $.getJSON(streamUrl, $.extend({'b': date.getTime()}, qs), function (data) {
            $.merge(photos, data.photos);
            var textTarget = $('#ajapaik-game-status-message');
            if (data.nothing_more_to_show) {
                textTarget.html(gettext('We are now showing you random photos.'));
            } else if (data.user_seen_all) {
                textTarget.html(gettext('You have seen all the pictures we have for this area.'));
            } else {
                textTarget.hide();
            }
            if (next || currentPhotoIdx <= 0) {
                nextPhoto();
            }
        });
    };

    window.flipPhoto = function () {
        userFlippedPhoto = !userFlippedPhoto;
        var photoElement = $('#ajapaik-game-modal-photo'),
            guessPhotoElement = $('#ajapaik-game-guess-photo-container').find('img'),
            guessPhotoElementDynamic = $('#ajapaik-game-guess-photo-js-panel').find('img'),
            fullscreenPhotoElement = $('#ajapaik-game-full-screen-image');
        if (photoElement.hasClass('ajapaik-photo-flipped')) {
            photoElement.removeClass('ajapaik-photo-flipped');
        } else {
            photoElement.addClass('ajapaik-photo-flipped');
        }
        if (guessPhotoElement.hasClass('ajapaik-photo-flipped')) {
            guessPhotoElement.removeClass('ajapaik-photo-flipped');
        } else {
            guessPhotoElement.addClass('ajapaik-photo-flipped');
        }
        if (guessPhotoElementDynamic.hasClass('ajapaik-photo-flipped')) {
            guessPhotoElementDynamic.removeClass('ajapaik-photo-flipped');
        } else {
            guessPhotoElementDynamic.addClass('ajapaik-photo-flipped');
        }
        if (fullscreenPhotoElement.hasClass('ajapaik-photo-flipped')) {
            fullscreenPhotoElement.removeClass('ajapaik-photo-flipped');
        } else {
            fullscreenPhotoElement.addClass('ajapaik-photo-flipped');
        }
    };

    window.handleGuessResponse = function (guessResponse) {
        guessResponseReceived = true;
        window.updateLeaderboard();
        noticeDiv = $('#ajapaik-game-feedback-js-panel-content');
        if (guessResponse.hideFeedback) {
            noticeDiv.find('#ajapaik-game-guess-feedback-difficulty-prompt').hide();
            noticeDiv.find('#ajapaik-game-guess-feedback-difficulty-form').hide();
            noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').hide();
        }
        noticeDiv.find('#ajapaik-game-guess-feedback-message').html(guessResponse.feedbackMessage);
        noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').text(gettext('Points awarded') + ': ' + guessResponse.currentScore);
        feedbackPanel = $('#ajapaik-game-map-container').jsPanel({
            content: noticeDiv.html(),
            controls: {
                buttons: false
            },
            title: false,
            header: false,
            size: {
                width: function () {
                    return $(window).width() / 4;
                },
                height: 'auto'
            },
            position: {
                bottom: 0,
                right: 0
            },
            id: 'ajapaik-game-feedback-panel'
        });
        if (guessResponse.heatmapPoints) {
            marker.setMap(null);
            $('.center-marker').hide();
            mapMousemoveListenerActive = false;
            google.maps.event.clearListeners(window.map, 'mousemove');
            mapIdleListenerActive = false;
            google.maps.event.clearListeners(window.map, 'idle');
            mapClickListenerActive = false;
            google.maps.event.clearListeners(window.map, 'click');
            mapDragstartListenerActive = false;
            google.maps.event.clearListeners(window.map, 'dragstart');
            playerLatlng = new google.maps.LatLng(marker.getPosition().lat(), marker.getPosition().lng());
            $('#ajapaik-game-map-geotag-count').html(guessResponse.heatmapPoints.length);
            $('#ajapaik-game-map-geotag-with-azimuth-count').html(guessResponse.tagsWithAzimuth);
            var markerImage = {
                url: '/static/images/material-design-icons/ajapaik_photo_camera_arror_drop_down_mashup.svg',
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(0, 16),
                scaledSize: new google.maps.Size(24, 33)
            };
            playerMarker = new google.maps.Marker({
                position: playerLatlng,
                map: window.map,
                title: gettext('Your guess'),
                draggable: false,
                icon: markerImage
            });
            taxiData = [];
            for (i = 0; i < guessResponse.heatmapPoints.length; i += 1) {
                taxiData.push(new google.maps.LatLng(guessResponse.heatmapPoints[i][0], guessResponse.heatmapPoints[i][1]));
            }
            pointArray = new google.maps.MVCArray(taxiData);
            heatmap = new google.maps.visualization.HeatmapLayer({
                data: pointArray
            });
            heatmap.setOptions({radius: 50, dissipating: true});
            heatmap.setMap(window.map);
        }
    };

    $(document).ready(function () {
        window.updateLeaderboard();

        if (!isMobile) {
            $('.ajapaik-flip-photo-overlay-button').hide();
        }

        $('#ajapaik-game-photo-modal').modal({
            backdrop: 'static',
            keyboard: false
        });

        loadPhotos();

        location = new google.maps.LatLng(start_location[1], start_location[0]);

        if (location) {
            window.getMap(start_location, 15, true);
        } else {
            window.getMap(undefined, undefined, true);
        }

        // To support touchscreens, we have an invisible marker underneath a fake one (otherwise it's laggy)
        marker = new google.maps.Marker({
            map: window.map,
            draggable: false,
            position: location,
            visible: false
        });

        marker.bindTo('position', window.map, 'center');

        realMapElement = $("#ajapaik-game-map-canvas")[0];
        realMapElement.addEventListener('mousewheel', wheelEventNonFF, true);
        realMapElement.addEventListener('DOMMouseScroll', wheelEventFF, true);

        mapClickListenerActive = true;
        google.maps.event.addListener(window.map, 'click', mapClickListenerFunction);
        mapIdleListenerActive = true;
        google.maps.event.addListener(window.map, 'idle', mapIdleListenerFunction);
        mapDragstartListenerActive = true;
        google.maps.event.addListener(window.map, 'dragstart', mapDragstartListenerFunction);

        google.maps.event.addListener(window.map, 'drag', function () {
            firstDragDone = true;
            setCursorToPanorama();
        });
        google.maps.event.addListener(marker, 'position_changed', function () {
            disableSave = false;
        });

        // TODO: Re-implement
        infowindow = new google.maps.InfoWindow({
            content: '<div style="overflow:hidden;white-space:nowrap;">' + gettext('Point the marker to where the picture was taken from.') + '</div>'
        });

        //$(".center-marker").hide();
//        $(".center-marker")
//            .css("background-image", "url('/static/images/material-design-icons/ajapaik_photo_camera_arror_drop_down_mashup.svg')")
//            .css("margin-left", "-8px")
//            .css("margin-top", "-9px");

        $.jQee('space', function () {
            if (!locationToolsOpen) {
                $('.ajapaik-game-specify-location-button').click();
            }
        });

        $.jQee('enter', function () {
            if (locationToolsOpen) {
                if (guessResponseReceived) {
                    $('.ajapaik-game-feedback-next-button').click();
                } else {
                    $('.ajapaik-game-save-location-button').click();
                }
            }
        });

        $.jQee("esc", function () {
            if (locationToolsOpen) {
                $('.ajapaik-game-skip-photo-button').click();
            }
        });

        $.jQee('up', function () {
            if (!locationToolsOpen) {
                $('.ajapaik-game-show-description-button').click();
            }
        });

        $.jQee('right', function () {
            if (!locationToolsOpen) {
                $('.ajapaik-game-next-photo-button').click();
            }
        });

        $('#google-plus-login-button').click(function () {
            _gaq.push(["_trackEvent", "Game", "Google+ login"]);
        });

        $('#logout-button').click(function () {
            _gaq.push(["_trackEvent", "Game", "Logout"]);
        });

        $('.ajapaik-game-specify-location-button').click(function () {
            $('#ajapaik-game-photo-modal').modal('hide');
            setCursorToAuto();
            $('#ajapaik-game-guess-photo-js-panel-content').find('img').prop('src', mediaUrl + photos[currentPhotoIdx].big.url);
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').hide();
                $('.ajapaik-fullscreen-overlay-button').hide();
            }
            guessPhotoPanel = $('#ajapaik-game-map-container').jsPanel({
                content: $('#ajapaik-game-guess-photo-js-panel-content').html(),
                controls: {buttons: false},
                title: false,
                header: false,
                draggable: {
                    handle: '.panel-body',
                    containment: '#ajapaik-game-map-container'
                },
                size: {width: 'auto', height: 'auto'},
                id: 'ajapaik-game-guess-photo-js-panel'
            });
            $('.ajapaik-game-save-location-button').show();
            $('.ajapaik-game-skip-photo-button').show();
            disableNext = false;
            locationToolsOpen = true;
        });

        $('.ajapaik-game-skip-photo-button').click(function () {
            firstDragDone = false;
            setCursorToAuto();
            if (!disableNext) {
                var data = {photo_id: photos[currentPhotoIdx].id};
                $.post(window.saveLocationURL, data, function () {
                    currentPhotoIdx += 1;
                    nextPhoto();
                });
                $('#ajapaik-game-photo-modal').modal();
                $('#ajapaik-game-guess-photo').hide();
                $('.ajapaik-game-save-location-button').hide();
                $('.ajapaik-game-skip-photo-button').hide();
                if (feedbackPanel) {
                    feedbackPanel.close();
                }
                if (guessPhotoPanel) {
                    guessPhotoPanel.close();
                }
                _gaq.push(['_trackEvent', 'Game', 'Skip photo']);
            }
        });

        $('.ajapaik-game-next-photo-button').click(function (e) {
            firstDragDone = false;
            setCursorToAuto();
            e.preventDefault();
            var data = {photo_id: photos[currentPhotoIdx].id};
            $.post(window.saveLocationURL, data, function () {
                currentPhotoIdx += 1;
                nextPhoto();
            });
            _gaq.push(['_trackEvent', 'Game', 'Skip photo']);
        });

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
            _gaq.push(['_trackEvent', 'Game', 'Full leaderboard']);
        });

        $('.ajapaik-game-save-location-button').click(function () {
            firstDragDone = false;
            setCursorToAuto();
            if (disableSave) {
                _gaq.push(['_trackEvent', 'Game', 'Forgot to move marker']);
                alert(gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view.'));
            } else {
                window.saveLocation(marker, photos[currentPhotoIdx].id, photos[currentPhotoIdx].flip, hintUsed, userFlippedPhoto, degreeAngle, azimuthLineEndPoint);
                if (saveDirection) {
                    _gaq.push(['_trackEvent', 'Game', 'Save location and direction']);
                } else {
                    _gaq.push(['_trackEvent', 'Game', 'Save location only']);
                }
            }
        });

        $(document).on('click', '.ajapaik-game-feedback-next-button', function () {
            var data = {
                level: $('input[name=difficulty]:checked', 'ajapaik-game-guess-feedback-difficulty-form').val(),
                photo_id: photos[currentPhotoIdx].id
            };
            $.post(difficultyFeedbackURL, data, function () {
                $.noop();
            });
            $('#ajapaik-game-photo-modal').modal();
            $('.ajapaik-game-save-location-button').hide();
            $('.ajapaik-game-skip-photo-button').hide();
            $('#ajapaik-game-guess-photo-js-panel').hide();
            if (feedbackPanel) {
                feedbackPanel.close();
            }
            if (guessPhotoPanel) {
                guessPhotoPanel.close();
            }
            window.map.getStreetView().setVisible(false);
            disableNext = false;
            currentPhotoIdx += 1;
            nextPhoto();
        });

        $(document).on('click', '.ajapaik-flip-photo-overlay-button', function () {
            var targets = $('.ajapaik-flip-photo-overlay-button'),
                k;
            for (k = 0; k < targets.length; k += 1) {
                if ($(targets[k]).hasClass('active')) {
                    $(targets[k]).removeClass('active');
                } else {
                    $(targets[k]).addClass('active');
                }
            }
            window.flipPhoto();
        });

        $(document).on('click', '.ajapaik-fullscreen-overlay-button', function () {
            if (BigScreen.enabled) {
                BigScreen.request($('#ajapaik-game-fullscreen-image-container')[0]);
                _gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'historic-' + this.rel]);
            }
        });

        $('.full-box div').on('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.exit();
            }
        });

        $('#ajapaik-game-full-screen-link').on('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.request($('#ajapaik-game-fullscreen-image-container')[0]);
                _gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'historic-' + this.rel]);
            }
        });

        $('a.fullscreen').on('click', function (e) {
            e.preventDefault();
            if (BigScreen.enabled) {
                BigScreen.request($('#ajapaik-game-full-screen-image'));
                _gaq.push(['_trackEvent', 'Game', 'Full-screen', 'historic-' + this.rel]);
            }
        });

        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

        $('#ajapaik-game-modal-body').hoverIntent(function () {
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
            }
        }, function () {
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').hide();
            }
        });

        $('.ajapaik-game-show-description-button').click(function () {
            $(this).hide();
            hintUsed = true;
            $('#ajapaik-game-photo-description').show();
        });

        $(document).on('mouseover', '#ajapaik-game-guess-photo-js-panel', function () {
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
                $('.ajapaik-fullscreen-overlay-button').show();
            }
        });

        $(document).on('mouseout', '#ajapaik-game-guess-photo-js-panel', function () {
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').hide();
                $('.ajapaik-fullscreen-overlay-button').hide();
            }
        });
    });
}());