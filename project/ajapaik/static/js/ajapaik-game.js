(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    var currentPhoto,
        initializeGuessingState,
        mediaUrl = '',
        streamUrl = '/stream/',
        difficultyFeedbackURL = '/difficulty_feedback/',
        noticeDiv,
        noticeDivXs,
        playerMarker,
        location,
        playerLatlng,
        lastStatusMessage,
        clearBothersomeListeners,
        reinstateBothersomeListeners,
        photoLoadModalResizeFunction,
        modalPhoto,
        fullScreenImage,
        toggleFlipButtons,
        guessPanelContainer,
        nextPhotoLoading = false;
    window.locationToolsOpen = false;
    window.photoHistory = [];
    window.descriptionViewHistory = {};
    window.photoHistoryIndex = null;
    window.straightToSpecify = false;
    window.startGuessLocation = function () {

    };
    photoLoadModalResizeFunction = function () {
        var trigger = 'manual';
        window.popover = $('[data-toggle="popover"]').popover({
            trigger: trigger,
            'placement': 'bottom',
            title: window.gettext('Vihje vaatamine'),
            html: true,
            content: window.gettext('Pildi kirjeldus muuseumikogus, mis ei pruugi alati olla õige. Kirjelduse vaatamine vähendab asukohapakkumise eest saadavaid punkte veerandi võrra.')
        });
        window.showPhotoMapIfApplicable();
        window.docCookies.setItem('ajapaik_seen_hint_view_popover', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
    };
    clearBothersomeListeners = function () {
        window.google.maps.event.clearListeners(window.map, 'mousemove');
        window.mapMousemoveListenerActive = false;
        window.google.maps.event.clearListeners(window.map, 'idle');
        window.mapIdleListenerActive = false;
        window.google.maps.event.clearListeners(window.map, 'dragstart');
        window.mapDragstartListenerActive = false;
        window.google.maps.event.clearListeners(window.map, 'dragend');
        window.mapDragendListenerActive = false;
        window.google.maps.event.clearListeners(window.map, 'drag');
        window.mapDragListenerActive = false;
    };
    reinstateBothersomeListeners = function () {
        window.google.maps.event.addListener(window.map, 'mousemove', window.mapMousemoveListenerFunction);
        window.mapMousemoveListenerActive = true;
        window.google.maps.event.addListener(window.map, 'idle', window.mapIdleListenerFunction);
        window.mapIdleListenerActive = true;
        window.google.maps.event.addListener(window.map, 'dragstart', window.mapDragstartListenerFunction);
        window.mapDragstartListenerActive = true;
        window.google.maps.event.addListener(window.map, 'dragend', window.mapDragendListenerFunction);
        window.mapDragendListenerActive = true;
        window.google.maps.event.addListener(window.map, 'drag', function () {
            window.firstDragDone = true;
            $('.ajapaik-marker-center-lock-button').show();
            window.setCursorToPanorama();
        });
        window.mapDragListenerActive = true;
    };
    initializeGuessingState = function () {
        if (window.marker) {
            window.marker.setVisible(false);
            $('.center-marker').hide();
        }
        window.gameHintUsed = false;
        var mq = window.matchMedia('(min-width: 481px)');
        if (!mq.matches) {
            $('#ajapaik-guess-panel-container-xs').animate({height: 0, complete: function () {
                $('#ajapaik-guess-panel-container-xs').hide();
            }});
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
        $('#ajapaik-game-photo-modal').modal();
        $('#ajapaik-map-button-container').show();
        $('#ajapaik-map-button-container-xs').show();
        $('#ajapaik-guess-feedback-panel').hide();
        $('#ajapaik-guess-feedback-panel-xs').hide();
        //$('#ajapaik-guess-panel-info-panel-xs').show();
        $('#ajapaik-guess-panel-photo-container-xs').show();
        window.map.getStreetView().setVisible(false);
        if (window.markerLocked === false) {
            $('.ajapaik-marker-center-lock-button').click();
        }
        $('.ajapaik-marker-center-lock-button').hide();
        window.hideDescriptions();
        window.showDescriptionButtons();
        window.disableSave = true;
        window.guessResponseReceived = false;
        window.firstDragDone = false;
        if (window.panoramaMarker) {
            window.panoramaMarker.setMap(null);
        }
        if (window.heatmap) {
            window.heatmap.setMap(null);
        }
        if (window.heatmapEstimatedLocationMarker) {
            window.heatmapEstimatedLocationMarker.setMap(null);
        }
        if (window.dottedAzimuthLine !== undefined) {
            window.dottedAzimuthLine.setVisible(false);
        }
        if (playerMarker) {
            playerMarker.setMap(null);
        }
        window.saveLocationButton.removeClass('btn-primary').removeClass('btn-warning').removeClass('btn-success')
            .addClass('btn-default').text(window.gettext('Save location only')).attr('disabled', 'disabled');
        $('img').removeClass('ajapaik-photo-flipped');
        $('.btn').removeClass('active');
        window.locationToolsOpen = false;
    };
    window.nextPhoto = function (previous) {
        nextPhotoLoading = true;
        window.userFlippedPhoto = false;
        $('#pac-input').val(null);
        $('#pac-input-mapview').val(null);
        if (window.popoverShown) {
            $('[data-toggle="popover"]').popover('hide');
            window.popoverShown = false;
        }
        if (window.tutorialPanel) {
            window.tutorialPanel.close();
            window.tutorialPanel = undefined;
        }
        $('#ajapaik-guess-panel-stats').show();
        initializeGuessingState();
        modalPhoto = $('#ajapaik-game-modal-photo');
        modalPhoto.unbind('load');
        var request = {
            b: new Date().getTime()
        };
        if (window.preselectedPhotoId) {
            request.photo = window.preselectedPhotoId;
            window.preselectedPhotoId = null;
        } else {
            // User wants to go back or not
            if (previous) {
                // We can only go back if we have history and we haven't reached the beginning
                if (window.photoHistory.length > 0 && window.photoHistoryIndex >= 0) {
                    // Move back 1 step, don't go to -1
                    if (window.photoHistoryIndex > 0) {
                        window.photoHistoryIndex -= 1;
                    }
                    // Get the photo id to load from history
                    request.photo = window.photoHistory[window.photoHistoryIndex];
                }
            } else {
                // There's no history or we've reached the end, load a new photo
                if (window.photoHistory.length === 0 || window.photoHistoryIndex === (window.photoHistory.length - 1)) {
                    if (window.albumId) {
                        request.album = window.albumId;
                    } else if (window.areaId) {
                        request.area = window.areaId;
                    }
                } else {
                    // There's history and we haven't reached the end
                    window.photoHistoryIndex += 1;
                    request.photo = window.photoHistory[window.photoHistoryIndex];
                }
            }
        }
        var previousButtons = $('.ajapaik-game-previous-photo-button');
        if (window.photoHistory.length > 0 && window.photoHistoryIndex > 0) {
            previousButtons.removeClass('ajapaik-photo-modal-previous-button-disabled');
        } else {
            previousButtons.addClass('ajapaik-photo-modal-previous-button-disabled');
        }
        // TODO: Why not POST?
        if (request.photo || request.album || request.area) {
            $.getJSON(streamUrl, request, function (data) {
                if (data.photo.description) {
                    window.currentPhotoDescription = data.photo.description.replace(/(\r\n|\n|\r)/gm, '');
                }
                currentPhoto = data.photo;
                // Not a history request
                if (!request.photo || window.preselectedPhotoId) {
                    window.photoHistory.push(currentPhoto.id);
                    window.photoHistoryIndex = window.photoHistory.length - 1;
                    window.preselectPhotoId = null;
                }
                var textTarget = $('#ajapaik-game-status-message'),
                    message;
                textTarget.hide();
                if (data.nothing_more_to_show) {
                    message = window.gettext("You've seen all the pictures in this album, we are now showing you random photos.");
                } else if (data.user_seen_all) {
                    message = window.gettext('You have seen all the pictures from this album.');
                }
                if (message !== lastStatusMessage) {
                    textTarget.html(message);
                    textTarget.show();
                }
                lastStatusMessage = message;
                modalPhoto.prop('src', mediaUrl + currentPhoto.big.url);
                modalPhoto.on('load', photoLoadModalResizeFunction);
                if (currentPhoto.description) {
                    $('#ajapaik-guess-panel-description').html(currentPhoto.description);
                    $('#ajapaik-guess-panel-info-panel-xs').show();
                    $('#ajapaik-guess-panel-description-xs').html(currentPhoto.description);
                    $('#ajapaik-game-photo-description').html(currentPhoto.description);
                    if (currentPhoto.source_url) {
                        $('#ajapaik-game-photo-identifier').html('<a target="_blank" id="ajapaik-game-source-link" href="' + currentPhoto.source_url + '">' + currentPhoto.source_name + " " + currentPhoto.source_key + '</a>');
                    } else {
                        $('#ajapaik-game-photo-identifier').empty();
                    }
                    window.showDescriptionButtons();
                } else {
                    window.hideDescriptionButtons();
                }
                fullScreenImage = $('#ajapaik-full-screen-image');
                fullScreenImage.prop('src', mediaUrl + currentPhoto.large.url).on('load', function () {
                    window.prepareFullscreen(currentPhoto.large.size[0], currentPhoto.large.size[1]);
                    $('#ajapaik-game-full-screen-description').html(currentPhoto.description);
                    fullScreenImage.unbind('load');
                });
                fullScreenImage.removeClass('ajapaik-photo-flipped');
                modalPhoto.removeClass('ajapaik-photo-flipped');
                if (currentPhoto.flip) {
                    fullScreenImage.addClass('ajapaik-photo-flipped');
                    modalPhoto.addClass('ajapaik-photo-flipped');
                }
                //$('#ajapaik-full-screen-link').prop('rel', currentPhoto.id).prop('href', mediaUrl + currentPhoto.large.url);
                $('#ajapaik-guess-panel-full-screen-link').prop('href', mediaUrl + currentPhoto.large.url);
                $('#ajapaik-guess-panel-full-screen-link-xs').prop('href', mediaUrl + currentPhoto.large.url);
                window.photoModalGeotaggingUserCount = currentPhoto.total_geotags;
                window.photoModalPhotoLat = currentPhoto.lat;
                window.photoModalPhotoLng = currentPhoto.lon;
                window.photoModalPhotoAzimuth = currentPhoto.azimuth;
                window.photoModalCurrentlyOpenPhotoId = currentPhoto.id;
                if (currentPhoto.total_geotags > 0) {
                    $('#ajapaik-game-number-of-geotags').html(currentPhoto.total_geotags);
                    $('#ajapaik-game-number-of-geotags').show();
                    $('#ajapaik-game-number-of-geotags-hidden-xs').html(currentPhoto.total_geotags);
                    $('#ajapaik-game-number-of-geotags-hidden-xs').show();
                } else {
                    $('#ajapaik-game-number-of-geotags').hide();
                    $('#ajapaik-game-number-of-geotags-hidden-xs').hide();
                }
                $('#ajapaik-game-map-geotag-count').html(currentPhoto.total_geotags);
                $('#ajapaik-game-map-geotag-with-azimuth-count').html(currentPhoto.geotags_with_azimuth);
                var azimuthIndicator = $('#ajapaik-photo-modal-location-with-azimuth'),
                    locationIndicator = $('#ajapaik-photo-modal-location-without-azimuth'),
                    noLocationIndicator = $('#ajapaik-photo-modal-no-location');
                if (currentPhoto.has_azimuth) {
                    azimuthIndicator.show();
                    locationIndicator.hide();
                    noLocationIndicator.hide();
                } else if (currentPhoto.has_coordinates) {
                    azimuthIndicator.hide();
                    locationIndicator.show();
                    noLocationIndicator.hide();
                } else {
                    azimuthIndicator.hide();
                    locationIndicator.hide();
                    noLocationIndicator.show();
                }
                reinstateBothersomeListeners();
                if (currentPhoto.user_already_confirmed) {
                    window.photoModalUserHasConfirmedThisLocation = true;
                } else {
                    window.photoModalUserHasConfirmedThisLocation = false;
                }
                nextPhotoLoading = false;
                if (currentPhoto.lat && currentPhoto.lon) {
                    window.map.setCenter(new window.google.maps.LatLng(currentPhoto.lat, currentPhoto.lon));
                }
                var descStatus = window.descriptionViewHistory[currentPhoto.id];
                if (descStatus || window.straightToSpecify) {
                    window.showDescriptions();
                    window.hideDescriptionButtons();
                    if (window.straightToSpecify) {
                        window.setTimeout(function () {
                            $('#ajapaik-photo-modal-specify-location').click();
                            window.straightToSpecify = false;
                            $('.modal-backdrop').hide();
                        }, 500);
                        window.straightToSpecify = false;
                    }
                }
            });
        } else {
            nextPhotoLoading = false;
        }
    };
    window.flipPhoto = function () {
        window.userFlippedPhoto = !userFlippedPhoto;
        currentPhoto.flip = !currentPhoto.flip;
        var photoElement = $('#ajapaik-game-modal-photo'),
            guessPhotoElement = $('#ajapaik-guess-panel-photo'),
            guessPhotoElementXs = $('#ajapaik-guess-panel-photo-xs');
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
        if (guessPhotoElementXs.hasClass('ajapaik-photo-flipped')) {
            guessPhotoElementXs.removeClass('ajapaik-photo-flipped');
        } else {
            guessPhotoElementXs.addClass('ajapaik-photo-flipped');
        }
    };
    // TODO: Lots of duplicate code in this function in every mode (map, grid, game)
    window.handleGuessResponse = function (guessResponse) {
        window.guessResponseReceived = true;
        window.updateLeaderboard();
        $('input[name="difficulty"]').prop('checked', false);
        $('.ajapaik-marker-center-lock-button').hide();
        $('#ajapaik-map-button-container').hide();
        $('#ajapaik-map-button-container-xs').hide();
        $('#ajapaik-guess-panel-photo-container-xs').hide();
        $('#ajapaik-guess-panel-info-panel-xs').hide();
        noticeDiv = $('#ajapaik-guess-feedback-panel');
        noticeDivXs = $('#ajapaik-guess-feedback-panel-xs');
        if (guessResponse.hideFeedback) {
            noticeDiv.find('#ajapaik-game-guess-feedback-difficulty-prompt').hide();
            noticeDiv.find('#ajapaik-game-guess-feedback-difficulty-form').hide();
            noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').hide();
            noticeDivXs.find('#ajapaik-game-guess-feedback-points-gained-xs').hide();
        } else {
            noticeDiv.find('#ajapaik-game-guess-feedback-difficulty-prompt').show();
            noticeDiv.find('#ajapaik-game-guess-feedback-difficulty-form').show();
            noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').show();
            noticeDivXs.find('#ajapaik-game-guess-feedback-points-gained-xs').show();
        }
        noticeDiv.find('#ajapaik-game-guess-feedback-message').html(guessResponse.feedbackMessage);
        noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').text(window.gettext('Points awarded') + ': ' + guessResponse.currentScore);
        noticeDivXs.find('#ajapaik-game-guess-feedback-message-xs').html(guessResponse.feedbackMessage);
        noticeDivXs.find('#ajapaik-game-guess-feedback-points-gained-xs').text(window.gettext('Points awarded') + ': ' + guessResponse.currentScore);
        noticeDiv.show();
        var mq = window.matchMedia('(min-width: 481px)');
        if (!mq.matches) {
            noticeDivXs.show();
        }
        if (guessResponse.heatmapPoints) {
            window.mapDisplayHeatmapWithEstimatedLocation(guessResponse);
            window.marker.setMap(null);
            $('.center-marker').hide();
            playerLatlng = new window.google.maps.LatLng(window.marker.getPosition().lat(), window.marker.getPosition().lng());
            var markerImage = new window.google.maps.MarkerImage('/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.png');
            markerImage.size = new window.google.maps.Size(24, 33);
            markerImage.scaledSize = new window.google.maps.Size(24, 33);
            markerImage.anchor = new window.google.maps.Point(12, 33);
            playerMarker = new window.google.maps.Marker({
                position: playerLatlng,
                map: window.map,
                title: window.gettext('Your guess'),
                draggable: false,
                icon: markerImage
            });
        }
    };
    window.syncMapStateToURL = function () {
        //var historyReplacementString = '/game/';
        //if (window.albumId) {
        //    historyReplacementString += '?album=' + window.albumId;
        //} else if (window.areaId) {
        //    historyReplacementString += '?area=' + window.areaId;
        //}
        //window.history.replaceState(null, window.title, historyReplacementString);
    };
    window.showDescriptions = function () {
        if (window.popoverShown) {
            $('[data-toggle="popover"]').popover('hide');
            window.popoverShown = false;
        }
        if (!nextPhotoLoading) {
            window.gameHintUsed = true;
            window.descriptionViewHistory[currentPhoto.id] = true;
            $('#ajapaik-game-photo-description').show();
            $('#ajapaik-game-photo-identifier').show();
            $('#ajapaik-game-full-screen-description').show();
            $('#ajapaik-guess-panel-description').show();
            $('#ajapaik-guess-panel-description-xs').show();
            window._gaq.push(['_trackEvent', 'Game', 'Show description']);
        }
    };
    window.showDescriptionButtons = function () {
        $('.ajapaik-game-show-description-button').show();
        $('.ajapaik-game-map-show-description-overlay-button').show();
        $('#ajapaik-game-full-screen-show-description-button').show();
    };
    window.hideDescriptions = function () {
        $('#ajapaik-game-full-screen-description').hide();
        $('#ajapaik-guess-panel-description').hide();
        $('#ajapaik-guess-panel-description-xs').hide();
        $('#ajapaik-game-photo-description').hide();
        $('#ajapaik-game-photo-identifier').hide();
    };
    window.hideDescriptionButtons = function () {
        $('.ajapaik-game-show-description-button').hide();
        $('.ajapaik-game-map-show-description-overlay-button').hide();
        $('#ajapaik-game-full-screen-show-description-button').hide();
    };
    $(document).ready(function () {
        window.updateLeaderboard();
        window.isGame = true;
        window.mapInfoPanelGeotagCountElement = $('#ajapaik-game-map-geotag-count');
        window.mapInfoPanelAzimuthCountElement = $('#ajapaik-game-map-geotag-with-azimuth-count');
        guessPanelContainer = $('#ajapaik-guess-panel-container');
        if (window.docCookies.getItem('ajapaik_closed_tutorial')) {
            window.userClosedTutorial = true;
        }
        window.saveLocationButton =  $('.ajapaik-save-location-button');
        if (!window.isMobile) {
            $('.ajapaik-flip-photo-overlay-button').hide();
        }
        $('#ajapaik-game-photo-modal').modal({
            backdrop: 'static',
            keyboard: 'false'
        });
        location = new window.google.maps.LatLng(window.start_location[1], window.start_location[0]);
        if (location) {
            window.getMap(location, 15, true);
        } else {
            window.getMap(undefined, undefined, true);
        }
        window.nextPhoto();
        // To support touchscreens, we have an invisible marker underneath a fake one (otherwise it's laggy)
        window.marker = new window.google.maps.Marker({
            map: window.map,
            draggable: false,
            position: location,
            visible: false,
            icon: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg'
        });
        window.realMapElement = $('#ajapaik-map-canvas')[0];
        window.realMapElement.addEventListener('mousewheel', window.wheelEventNonFF, true);
        window.realMapElement.addEventListener('DOMMouseScroll', window.wheelEventFF, true);
        window.mapClickListenerActive = true;
        window.mapClickListener = window.google.maps.event.addListener(window.map, 'click', window.mapClickListenerFunction);
        window.mapIdleListenerActive = true;
        window.mapGameIdleListener = window.google.maps.event.addListener(window.map, 'idle', window.mapIdleListenerFunction);
        window.mapDragstartListenerActive = true;
        window.mapDragstartListener = window.google.maps.event.addListener(window.map, 'dragstart', window.mapDragstartListenerFunction);
        window.mapDragListenerActive = true;
        window.mapDragListener = window.google.maps.event.addListener(window.map, 'drag', function () {
            window.firstDragDone = true;
            $('.ajapaik-marker-center-lock-button').show();
            window.setCursorToPanorama();
        });
        window.mapDragendListener = window.google.maps.event.addListener(window.map, 'dragend', window.mapDragendListenerFunction);
        window.windowResizeListener = window.google.maps.event.addDomListener(window, 'resize', window.windowResizeListenerFunction);
        window.mapMarkerPositionChangedListener = window.google.maps.event.addListener(window.marker, 'position_changed', function () {
            window.disableSave = false;
        });
        // TODO: DRY
        //if (window.albumId && window.infoModalURL && !window.getQueryParameterByName('fromButton')) {
        //    var targetDiv = $('#ajapaik-info-modal');
        //    $.ajax({
        //        url: window.infoModalURL + window.albumId,
        //        data: {
        //            'linkToGame': false,
        //            'linkToMap': true
        //        },
        //        success: function (resp) {
        //            targetDiv.html(resp);
        //            targetDiv.modal().on('shown.bs.modal', function () {
        //                window.FB.XFBML.parse($('#ajapaik-photo-modal-like').get(0));
        //            });
        //        }
        //    });
        //}
        if (window.getQueryParameterByName('photo')) {
            window.straightToSpecify = true;
        }
        $('#ajapaik-game-photo-modal').on('shown.bs.modal', function () {
            window.showPhotoMapIfApplicable();
        });
        window.handleAlbumChange = function () {
            if (window.albumId) {
                window.location.href = '/geotag?album=' + window.albumId;
            }
        };
        $('.ajapaik-navmenu').on('shown.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').show();
            //if (window.albumId) {
                //$('#ajapaik-album-selection-navmenu').scrollTop($(".ajapaik-album-selection-item[data-id='" + window.albumId + "']").offset().top);
            //}
        }).on('hidden.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').hide();
        });
        $('#ajapaik-album-name-container').css('visibility', 'visible');
        //$('#ajapaik-header-map-button').show();
        //$('#ajapaik-header-grid-button').show();
        $(window.input).show();
        window.syncMapStateToURL();

        $('#logout-button').click(function () {
            window._gaq.push(['_trackEvent', 'Game', 'Logout']);
        });
        $('.ajapaik-game-specify-location-button').click(function () {
            if (window.fullscreenEnabled) {
                window.BigScreen.exit();
                window.fullscreenEnabled = false;
            }
            if (!window.locationToolsOpen && !nextPhotoLoading) {
                if (window.map.zoom < 17) {
                    window.map.setZoom(17);
                }
                var mq = window.matchMedia('(min-width: 481px)');
                if (mq.matches) {
                    $('#ajapaik-map-container').animate({width: '70%'});
                    guessPanelContainer.show();
                    guessPanelContainer.animate({width: '30%'}, {complete: function () {
                        $('#ajapaik-guess-panel-container-xs').hide();
                        $('#ajapaik-map-button-container-xs').hide(function () {
                            window.google.maps.event.trigger(window.map, 'resize');
                        });
                    }});
                    $('#ajapaik-geotag-info-panel-container').animate({width: '30%'});
                } else {
                    $('#ajapaik-map-canvas').animate({height: '70%'});
                    $('#ajapaik-guess-panel-container-xs').animate({height: '30%'}, {complete: function () {
                        guessPanelContainer.hide();
                        $('#ajapaik-map-button-container-xs').show();
                        window.google.maps.event.trigger(window.map, 'resize');
                    }});
                }
                window.guessLocationStarted = true;
                $('.center-marker').show();
                $('#ajapaik-game-photo-modal').modal('hide');
                window.setCursorToAuto();
                //$('.ajapaik-marker-center-lock-button').show();
                $('#ajapaik-guess-panel-photo').prop('src', mediaUrl + currentPhoto.big.url).removeClass('ajapaik-photo-flipped');
                if (currentPhoto.flip) {
                    $('#ajapaik-guess-panel-photo').addClass('ajapaik-photo-flipped');
                }
                if (!mq.matches) {
                    $('#ajapaik-guess-panel-photo-xs').prop('src', mediaUrl + currentPhoto.big.url);
                    if (currentPhoto.flip) {
                        $('#ajapaik-guess-panel-photo-xs').addClass('ajapaik-photo-flipped');
                    }
                }
                if (!window.gameHintUsed) {
                    $('#ajapaik-guess-panel-description').hide();
                    $('#ajapaik-guess-panel-description-xs').hide();
                }
                if (!window.isMobile) {
                    $('.ajapaik-flip-photo-overlay-button').hide();
                }
                //if (!window.userClosedTutorial) {
                //    window.openTutorialPanel();
                //}
                window.locationToolsOpen = true;
                window._gaq.push(['_trackEvent', 'Game', 'Specify location']);
            }
        });
        $(document).on('click', '#ajapaik-game-source-link', function () {
            window._gaq.push(['_trackEvent', 'Game', 'Source link click']);
        });
        $(document).on('click', '.ajapaik-game-next-photo-button', function () {
            if (!nextPhotoLoading) {
                var data = {
                    photo_id: currentPhoto.id,
                    origin: 'Game',
                    csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
                };
                $.post(window.saveLocationURL, data, function () {
                    window.nextPhoto();
                });
                window._gaq.push(['_trackEvent', 'Game', 'Next photo']);
            }
        });
        $(document).on('click', '.ajapaik-game-previous-photo-button', function () {
            if (!nextPhotoLoading && !$(this).hasClass('ajapaik-game-previous-photo-button-disabled')) {
                window.nextPhoto(true);
                window._gaq.push(['_trackEvent', 'Game', 'Previous photo']);
            }
        });
        $(document).on('click', '#ajapaik-game-close-game-modal', function () {
            window.location.href = '/map?album=' + window.albumId;
        });
        window.saveLocationButton.click(function () {
            if (window.disableSave) {
                window.alert(window.gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view.'));
                window._gaq.push(['_trackEvent', 'Game', 'Forgot to move marker']);
            } else {
                $('#ajapaik-guess-panel-stats').hide();
                window.setCursorToAuto();
                clearBothersomeListeners();
                window.saveLocation(window.marker, currentPhoto.id, currentPhoto.flip, window.gameHintUsed, window.userFlippedPhoto, window.degreeAngle, window.azimuthLineEndPoint, 0);
                if (window.saveDirection) {
                    window._gaq.push(['_trackEvent', 'Game', 'Save location and direction']);
                } else {
                    window._gaq.push(['_trackEvent', 'Game', 'Save location only']);
                }
            }
        });
        $(document).on('click', '.ajapaik-game-feedback-next-button', function () {
            var data = {
                level: $('input[name=difficulty]:checked').val(),
                photo_id: currentPhoto.id,
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            };
            $.post(difficultyFeedbackURL, data, function () {
                $.noop();
            });
            window.nextPhoto();
        });
        toggleFlipButtons = function () {
            var targets = $('.ajapaik-flip-photo-overlay-button'),
                loneButton = $('#ajapaik-game-flip-photo-button'),
                k;
            for (k = 0; k < targets.length; k += 1) {
                if ($(targets[k]).hasClass('active')) {
                    $(targets[k]).removeClass('active');
                } else {
                    $(targets[k]).addClass('active');
                }
            }
            if (loneButton.hasClass('active')) {
                loneButton.removeClass('active');
            } else {
                loneButton.addClass('active');
            }
        };
        $(document).on('click', '#ajapaik-game-flip-photo-button', function () {
            var $this = $(this);
            if ($this.hasClass('active')) {
                $this.removeClass('active');
            } else {
                $this.addClass('active');
            }
            $('.ajapaik-flip-photo-overlay-button')[0].click();
        });
        $(document).on('click', 'a.fullscreen', function (e) {
            e.preventDefault();
            if (window.BigScreen.enabled) {
                window.BigScreen.request($('#ajapaik-fullscreen-image-container')[0]);
                $('#ajapaik-game-full-screen-flip-button').show();
                window.fullscreenEnabled = true;
                window._gaq.push(['_trackEvent', 'Game', 'Full-screen']);
            }
        });
/*        $('.full-box img').on('click', function (e) {
            e.preventDefault();
            if (window.BigScreen.enabled) {
                window.BigScreen.exit();
                window.fullscreenEnabled = false;
            }
        });*/
        $(document).on('click', '.ajapaik-game-show-description-button', function () {
            window.showDescriptions();
            window.hideDescriptionButtons();
        });
        $('#ajapaik-game-modal-body').mouseenter(function () {
            if (!window.isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
                $('.ajapaik-photo-modal-next-button').show();
                $('.ajapaik-photo-modal-previous-button').show();
            }
        }).mouseleave(function () {
            if (!window.isMobile && !window.fullscreenEnabled) {
                $('.ajapaik-flip-photo-overlay-button').hide();
                $('.ajapaik-photo-modal-next-button').hide();
                $('.ajapaik-photo-modal-previous-button').hide();
            }
        });
    });
}(jQuery));