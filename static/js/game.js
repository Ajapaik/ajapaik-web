(function ($) {
    'use strict';

    var currentPhoto,
        initializeGuessingState,
        hintUsed = false,
        mediaUrl = '',
        streamUrl = '/stream/',
        difficultyFeedbackURL = '/difficulty_feedback/',
        locationToolsOpen = false,
        noticeDiv,
        userFlippedPhoto = false,
        playerMarker,
        location,
        playerLatlng,
        nextPhoto,
        guessPhotoPanel,
        guessPhotoPanelContent,
        feedbackPanel,
        lastStatusMessage,
        flipPhoto,
        showDescriptions,
        hideDescriptions,
        showDescriptionButtons,
        hideDescriptionButtons,
        clearBothersomeListeners,
        reinstateBothersomeListeners,
        photoLoadModalResizeFunction,
        modalPhoto,
        fullScreenImage,
        guessPhotoPanelSettings = {
            selector: '#ajapaik-map-container',
            removeHeader: true,
            position: {
                top: 50,
                left: 50
            },
            draggable: {
                handle: '.jsPanel-content',
                containment: '#ajapaik-map-container'
            },
            size: 'auto',
            id: 'ajapaik-game-guess-photo-js-panel'
        },
        nextPhotoLoading = false;

    photoLoadModalResizeFunction = function () {
        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
        // Show information about viewing hints to Estonians that haven't seen it before (hints are in Estonian)
        if (!window.docCookies.getItem('ajapaik_seen_hint_view_popover') && window.languageCode === 'et') {
            $('[data-toggle="popover"]').popover({
                trigger: 'hover',
                'placement': 'bottom',
                title: window.gettext('Vihje vaatamine'),
                html: true,
                content: window.gettext('Pildi kirjeldus muuseumikogus, mis ei pruugi alati olla õige. Kirjelduse vaatamine vähendab asukohapakkumise eest saadavaid punkte veerandi võrra.')
            });
            // TODO: What if he didn't hover over it still?
            window.docCookies.setItem('ajapaik_seen_hint_view_popover', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
        }
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
        hintUsed = false;
        $('#ajapaik-game-photo-modal').modal();
        $('#ajapaik-map-button-container').hide();
        $('#ajapaik-game-guess-photo-js-panel').hide();
        if (feedbackPanel) {
            feedbackPanel.close();
        }
        if (guessPhotoPanel) {
            guessPhotoPanel.close();
        }
        window.map.getStreetView().setVisible(false);
        if (!window.markerLocked) {
            $('.ajapaik-marker-center-lock-button').click();
        }
        hideDescriptions();
        showDescriptionButtons();
        window.map.getStreetView().setVisible(false);
        window.disableSave = true;
        window.guessResponseReceived = false;
        window.firstDragDone = false;
        $('.ajapaik-marker-center-lock-button').hide();
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
        locationToolsOpen = false;
    };

    nextPhoto = function () {
        nextPhotoLoading = true;
        initializeGuessingState();
        modalPhoto = $('#ajapaik-game-modal-photo');
        modalPhoto.unbind('load');
        $.getJSON(streamUrl, $.extend({'b': new Date().getTime()}, window.URI.parseQuery(window.location.search)), function (data) {
            currentPhoto = data.photo;
            var textTarget = $('#ajapaik-game-status-message'),
                message;
            textTarget.hide();
            if (data.nothing_more_to_show) {
                message = window.gettext('We are now showing you random photos.');
            } else if (data.user_seen_all) {
                message = window.gettext('You have seen all the pictures we have for this area.');
            }
            if (message !== lastStatusMessage) {
                textTarget.html(message);
                textTarget.show();
            }
            lastStatusMessage = message;
            modalPhoto.prop('src', mediaUrl + currentPhoto.big.url);
            modalPhoto.on('load', photoLoadModalResizeFunction);
            if (currentPhoto.description) {
                $('#ajapaik-game-photo-description').html(currentPhoto.description);
                $('#ajapaik-game-guess-photo-js-panel-content').find('.row').html(currentPhoto.description);
            }
            fullScreenImage = $('#ajapaik-full-screen-image');
            fullScreenImage.prop('src', mediaUrl + currentPhoto.large.url).on('load', function () {
                window.prepareFullscreen(currentPhoto.large.size[0], currentPhoto.large.size[1]);
                $('#ajapaik-game-full-screen-description').html(currentPhoto.description);
                fullScreenImage.unbind('load');
            });
            $('#ajapaik-full-screen-link').prop('rel', currentPhoto.id).prop('href', mediaUrl + currentPhoto.large.url);
            $('#ajapaik-game-map-geotag-count').html(currentPhoto.total_geotags);
            $('#ajapaik-game-map-geotag-with-azimuth-count').html(currentPhoto.geotags_with_azimuth);
            $('#ajapaik-game-map-confidence').html(currentPhoto.confidence.toFixed(2));
            reinstateBothersomeListeners();
            nextPhotoLoading = false;
        });
    };

    flipPhoto = function () {
        userFlippedPhoto = !userFlippedPhoto;
        var photoElement = $('#ajapaik-game-modal-photo'),
            guessPhotoElement = $('#ajapaik-game-guess-photo-container').find('img'),
            guessPhotoElementDynamic = $('#ajapaik-game-guess-photo-js-panel').find('img'),
            fullscreenPhotoElement = $('#ajapaik-full-screen-image');
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

    // TODO: Lots of duplicate code in this function in every mode
    window.handleGuessResponse = function (guessResponse) {
        window.guessResponseReceived = true;
        window.updateLeaderboard();
        noticeDiv = $('#ajapaik-game-feedback-js-panel-content');
        if (guessResponse.hideFeedback) {
            noticeDiv.find('#ajapaik-game-guess-feedback-difficulty-prompt').hide();
            noticeDiv.find('#ajapaik-game-guess-feedback-difficulty-form').hide();
            noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').hide();
        }
        noticeDiv.find('#ajapaik-game-guess-feedback-message').html(guessResponse.feedbackMessage);
        noticeDiv.find('#ajapaik-game-guess-feedback-points-gained').text(window.gettext('Points awarded') + ': ' + guessResponse.currentScore);
        feedbackPanel = $.jsPanel({
            selector: '#ajapaik-map-container',
            content: noticeDiv.html(),
            removeHeader: true,
            title: false,
            size: {
                width: function () {
                    return $(window).width() / 3;
                },
                height: 'auto'
            },
            draggable: false,
            resizable: false,
            id: 'ajapaik-game-feedback-panel'
        });
        if (guessResponse.heatmapPoints) {
            window.mapDisplayHeatmapWithEstimatedLocation(guessResponse);
            window.marker.setMap(null);
            $('.center-marker').hide();
            playerLatlng = new window.google.maps.LatLng(window.marker.getPosition().lat(), window.marker.getPosition().lng());
            var markerImage = {
                url: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg'
            };
            playerMarker = new window.google.maps.Marker({
                position: playerLatlng,
                map: window.map,
                title: window.gettext('Your guess'),
                draggable: false,
                icon: markerImage
            });
        }
    };

    showDescriptions = function () {
        if (!nextPhotoLoading && window.languageCode === 'et') {
            hintUsed = true;
            $('#ajapaik-game-guess-photo-js-panel').find('.ajapaik-photo-modal-row').show();
            $('#ajapaik-game-guess-photo-js-panel-content').find('.ajapaik-photo-modal-row').show();
            $('#ajapaik-game-full-screen-description').show();
            $('#ajapaik-game-photo-description').show();
        }
    };

    showDescriptionButtons = function () {
        if (window.languageCode === 'et') {
            $('.ajapaik-game-show-description-button').show();
            $('.ajapaik-game-map-show-description-overlay-button').show();
            $('#ajapaik-game-full-screen-show-description-button').show();
        }
    };

    hideDescriptions = function () {
        $('#ajapaik-game-guess-photo-js-panel').find('.ajapaik-photo-modal-row').hide();
        $('#ajapaik-game-full-screen-description').hide();
        $('#ajapaik-game-photo-description').hide();
        $('#ajapaik-game-guess-photo-js-panel-content').find('.ajapaik-photo-modal-row').hide();
    };

    hideDescriptionButtons = function () {
        $('.ajapaik-game-show-description-button').hide();
        $('.ajapaik-game-map-show-description-overlay-button').hide();
        $('#ajapaik-game-full-screen-show-description-button').hide();
    };

    $(document).ready(function () {
        window.updateLeaderboard();

        window.mapInfoPanelGeotagCountElement = $('#ajapaik-game-map-geotag-count');
        window.mapInfoPanelAzimuthCountElement = $('#ajapaik-game-map-geotag-with-azimuth-count');
        window.mapInfoPanelConfidenceElement = $('#ajapaik-game-map-confidence');

        if (window.docCookies.getItem('ajapaik_closed_tutorial')) {
            window.userClosedTutorial = true;
        }

        window.saveLocationButton =  $('.ajapaik-save-location-button');

        if (!window.isMobile) {
            $('.ajapaik-flip-photo-overlay-button').hide();
        }

        $('#ajapaik-game-photo-modal').modal({
            backdrop: 'static',
            keyboard: false
        });

        location = new window.google.maps.LatLng(window.start_location[1], window.start_location[0]);

        if (location) {
            window.getMap(location, 15, true);
        } else {
            window.getMap(undefined, undefined, true);
        }

        nextPhoto();

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

        // TODO: Re-implement
        //window.infoWindow = new google.maps.InfoWindow({
        //    content: '<div style="overflow:hidden;white-space:nowrap;">' + window.gettext('Point the marker to where the picture was taken from.') + '</div>'
        //});

        $.jQee('space', function () {
            if (window.fullscreenEnabled) {
                window.BigScreen.exit();
                window.fullscreenEnabled = false;
            }
            if (!locationToolsOpen) {
                $('.ajapaik-game-specify-location-button')[0].click();
            }
        });

        $.jQee('enter', function () {
            if (locationToolsOpen) {
                if (window.guessResponseReceived) {
                    $('.ajapaik-game-feedback-next-button')[0].click();
                } else {
                    if (!window.streetPanorama.getVisible()) {
                        // No saving in Street View
                        $('.ajapaik-save-location-button')[0].click();
                    }
                }
            }
        });

        $.jQee('esc', function () {
            if (locationToolsOpen) {
                // Skipping photo on close Street View would be confusing
                if (!window.streetPanorama.getVisible()) {
                    $('.ajapaik-game-next-photo-button')[0].click();
                } else {
                    // Using escape to close street view must also show save button
                    //window.saveLocationButton.show();
                    window.streetPanorama.setVisible(false);
                }
            }
        });

        $.jQee('up', function () {
            showDescriptions();
            hideDescriptionButtons();
        });

        $.jQee('f', function () {
            $('.ajapaik-flip-photo-overlay-button')[0].click();
        });

        $.jQee('right', function () {
            if (!nextPhotoLoading) {
                //Many buttons, click only 1
                $('.ajapaik-game-next-photo-button')[0].click();
            }
        });

        $('#logout-button').click(function () {
            window._gaq.push(['_trackEvent', 'Game', 'Logout']);
        });

        $('.ajapaik-game-specify-location-button').click(function () {
            if (window.fullscreenEnabled) {
                window.BigScreen.exit();
                window.fullscreenEnabled = false;
            }
            if (!locationToolsOpen && !nextPhotoLoading) {
                if (window.map.zoom < 17) {
                    window.map.setZoom(17);
                }
                $('.center-marker').show();
                $('#ajapaik-game-photo-modal').modal('hide');
                window.setCursorToAuto();
                $('.ajapaik-marker-center-lock-button').show();
                //$('.ajapaik-show-tutorial-button').show();
                guessPhotoPanelContent = $('#ajapaik-game-guess-photo-js-panel-content');
                guessPhotoPanelContent.find('img').prop('src', mediaUrl + currentPhoto.big.url);
                if (!hintUsed) {
                    $('#ajapaik-game-guess-photo-description').hide();
                }
                if (!window.isMobile) {
                    $('.ajapaik-flip-photo-overlay-button').hide();
                    $('.ajapaik-fullscreen-overlay-button').hide();
                    $('.ajapaik-game-map-show-description-overlay-button').hide();
                }
                guessPhotoPanelSettings.content = guessPhotoPanelContent.html();
                if (window.isMobile) {
                    // TODO: Make draggable and resizable also work on mobile
                    guessPhotoPanelSettings.draggable = false;
                    guessPhotoPanelSettings.resizable = false;
                }
                guessPhotoPanel = $.jsPanel(guessPhotoPanelSettings).css('max-width', ($(window).width * 0.4) + 'px').css('max-height', $(window).height() - 200);
                guessPhotoPanel.on('jspanelloaded', function () {
                    $('#ajapaik-game-guess-photo-js-panel').find('img').show();
                });
                if (!window.userClosedTutorial) {
                    window.openTutorialPanel();
                }
                $('#ajapaik-map-button-container').show();
                locationToolsOpen = true;
            }
        });

        $(document).on('click', '.ajapaik-game-next-photo-button', function () {
            if (!nextPhotoLoading) {
                //window.firstDragDone = false;
                //window.setCursorToAuto();
                var data = {photo_id: currentPhoto.id, origin: 'Game', csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')};
                $.post(window.saveLocationURL, data, function () {
                    nextPhoto();
                });
                window._gaq.push(['_trackEvent', 'Game', 'Skip photo']);
            }
        });

        $('#full_leaderboard').bind('click', function (e) {
            e.preventDefault();
            $.ajax({
                url: window.leaderboardFullURL,
                success: function (response) {
                    var modalWindow = $('#ajapaik-full-leaderboard-modal');
                    modalWindow.find('.scoreboard').html(response);
                    modalWindow.modal().on('shown.bs.modal', function () {
                        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                    });
                }
            });
            window._gaq.push(['_trackEvent', 'Game', 'Full leaderboard']);
        });

        window.saveLocationButton.click(function () {
            if (window.disableSave) {
                window.alert(window.gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view. You should also zoom the map before submitting your geotag.'));
                window._gaq.push(['_trackEvent', 'Game', 'Forgot to move marker']);
            } else {
                window.setCursorToAuto();
                clearBothersomeListeners();
                window.saveLocation(window.marker, currentPhoto.id, currentPhoto.flip, hintUsed, userFlippedPhoto, window.degreeAngle, window.azimuthLineEndPoint, 'Game');
                if (window.saveDirection) {
                    window._gaq.push(['_trackEvent', 'Game', 'Save location and direction']);
                } else {
                    window._gaq.push(['_trackEvent', 'Game', 'Save location only']);
                }
            }
        });

        $(document).on('click', '.ajapaik-game-feedback-next-button', function () {
            var data = {
                level: $('input[name=difficulty]:checked', 'ajapaik-game-guess-feedback-difficulty-form').val(),
                photo_id: currentPhoto.id,
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            };
            $.post(difficultyFeedbackURL, data, function () {
                $.noop();
            });
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
            flipPhoto();
        });

        $(document).on('click', '.ajapaik-fullscreen-overlay-button', function () {
            if (window.BigScreen.enabled) {
                window.BigScreen.request($('#ajapaik-fullscreen-image-container')[0]);
                $('#ajapaik-game-full-screen-flip-button').show();
                window.fullscreenEnabled = true;
                window._gaq.push(['_trackEvent', 'Photo', 'Full-screen']);
            }
        });

        $(document).on('click', 'a.fullscreen', function (e) {
            e.preventDefault();
            if (window.BigScreen.enabled) {
                window.BigScreen.request($('#ajapaik-fullscreen-image-container')[0]);
                $('#ajapaik-game-full-screen-flip-button').show();
                window.fullscreenEnabled = true;
                window._gaq.push(['_trackEvent', 'Map', 'Full-screen']);
            }
        });

        $('.full-box img').on('click', function (e) {
            e.preventDefault();
            if (window.BigScreen.enabled) {
                window.BigScreen.exit();
                window.fullscreenEnabled = false;
            }
        });

        $(document).on('click', '.ajapaik-game-show-description-button', function () {
            showDescriptions();
            hideDescriptionButtons();
        });

        $(document).on('click', '.ajapaik-game-map-show-description-overlay-button', function () {
            showDescriptions();
            hideDescriptionButtons();
        });

        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

        $('#ajapaik-game-modal-body').hoverIntent(function () {
            if (!window.isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
            }
        }, function () {
            if (!window.isMobile && !window.fullscreenEnabled) {
                $('.ajapaik-flip-photo-overlay-button').hide();
            }
        });

        $(document).on('mouseover', '#ajapaik-game-guess-photo-js-panel', function () {
            if (!window.isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
                $('.ajapaik-fullscreen-overlay-button').show();
                if (window.languageCode === 'et' && currentPhoto.description && !hintUsed) {
                    $('.ajapaik-game-map-show-description-overlay-button').show();
                }
            }
        });

        $(document).on('mouseout', '#ajapaik-game-guess-photo-js-panel', function () {
            if (!window.isMobile) {
                if (!window.fullscreenEnabled) {
                    $('.ajapaik-flip-photo-overlay-button').hide();
                }
                $('.ajapaik-fullscreen-overlay-button').hide();
                $('.ajapaik-game-map-show-description-overlay-button').hide();
            }
        });
    });
}(jQuery));