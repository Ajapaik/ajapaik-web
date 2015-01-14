(function ($) {
    'use strict';

    var photos = [],
        photoDescription,
        currentPhotoIdx = 0,
        hintUsed = false,
        mediaUrl = '',
        streamUrl = '/stream/',
        difficultyFeedbackURL = '/difficulty_feedback/',
        disableNext = false,
        locationToolsOpen = false,
        photoHasDescription = false,
        photoContainer,
        noticeDiv,
        userFlippedPhoto = false,
        taxiData = [],
        pointArray,
        heatmap,
        playerMarker,
        location,
        i,
        loadPhotos,
        playerLatlng,
        nextPhoto,
        guessPhotoPanel,
        guessPhotoPanelContent,
        currentPhotoWidth,
        feedbackPanel,
        lastStatusMessage,
        flipPhoto,
        photoLoadModalResizeHandler,
        photoLoadModalResizeFunction,
        modalPhoto,
        fullScreenImage,
        tutorialPanelContent,
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
        hintUsed = 0;
        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
        photoContainer.css('visibility', 'visible');
        if (!window.docCookies.getItem('ajapaik_seen_hint_view_popover') && window.languageCode === 'et') {
            $('[data-toggle="popover"]').popover({
                trigger: 'hover',
                'placement': 'bottom',
                title: window.gettext('Vihje vaatamine'),
                html: true,
                content: window.gettext('Pildi kirjeldus muuseumikogus, mis ei pruugi alati olla õige. Kirjelduse vaatamine vähendab asukohapakkumise eest saadavaid punkte veerandi võrra.')
            });
            window.docCookies.setItem('ajapaik_seen_hint_view_popover', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
        }
    };

    nextPhoto = function () {
        nextPhotoLoading = true;
        if (!window.markerLocked) {
            $('.ajapaik-marker-center-lock-button').click();
        }
        photoHasDescription = false;
        photoDescription = $('#ajapaik-game-photo-description');
        photoDescription.hide();
        $('#ajapaik-game-full-screen-description').hide();
        photoContainer = $('#ajapaik-game-modal-photo-container');
        photoContainer.css('visibility', 'hidden');
        window.map.getStreetView().setVisible(false);
        window.disableSave = true;
        locationToolsOpen = false;
        window.azimuthListenerActive = false;
        window.guessResponseReceived = false;
        window.map.setZoom(16);
        window.mapMousemoveListenerActive = false;
        if (window.panoramaMarker) {
            window.panoramaMarker.setMap(null);
        }
        if (window.heatmap) {
            window.heatmap.setMap(null);
        }
        if (window.heatmapEstimatedLocationMarker) {
            window.heatmapEstimatedLocationMarker.setMap(null);
        }
        window.saveLocationButton.removeClass('btn-primary').removeClass('btn-warning').removeClass('btn-success')
            .addClass('btn-default').text(window.gettext('Save location only')).attr('disabled', 'disabled');
        window.google.maps.event.clearListeners(window.map, 'mousemove');
        if (window.dottedAzimuthLine !== undefined) {
            window.dottedAzimuthLine.setVisible(false);
        }
        if (photos.length > currentPhotoIdx) {
            $('img').removeClass('ajapaik-photo-flipped');
            $('.btn').removeClass('active');
            modalPhoto = $('#ajapaik-game-modal-photo');
            modalPhoto.unbind('load');
            modalPhoto.prop('src', mediaUrl + photos[currentPhotoIdx].big.url);
            photoLoadModalResizeHandler = modalPhoto.on('load', photoLoadModalResizeFunction);
            if (photos[currentPhotoIdx].description) {
                photoHasDescription = true;
                $('#ajapaik-game-photo-description').html(photos[currentPhotoIdx].description);
                $('#ajapaik-game-guess-photo-description').html(photos[currentPhotoIdx].description);
                if (window.languageCode === 'et') {
                    $('.ajapaik-game-show-description-button').show();
                }
            } else {
                $('.ajapaik-game-show-description-button').hide();
            }
            fullScreenImage = $('#ajapaik-full-screen-image');
            fullScreenImage.unbind('load');
            fullScreenImage.prop('src', mediaUrl + photos[currentPhotoIdx].large.url).on('load', function () {
                window.prepareFullscreen(photos[currentPhotoIdx].large.size[0], photos[currentPhotoIdx].large.size[1]);
            });
            $('#ajapaik-full-screen-link').prop('rel', photos[currentPhotoIdx].id)
                .prop('href', mediaUrl + photos[currentPhotoIdx].large.url);
            $('#ajapaik-game-map-geotag-count').html(photos[currentPhotoIdx].total_geotags);
            $('#ajapaik-game-map-geotag-with-azimuth-count').html(photos[currentPhotoIdx].geotags_with_azimuth);
            $('#ajapaik-game-map-confidence').html(photos[currentPhotoIdx].confidence.toFixed(2));
            //disableNext = true;
        } else {
            loadPhotos(1);
        }
    };

    loadPhotos = function (next) {
        // IE needs a different URL, sending seconds
        var date = new Date(),
            qs = window.URI.parseQuery(window.location.search);
        if (window.marker) {
            window.marker.setMap(window.map);
            $('.center-marker').show();
        }

        if (window.map) {
            if (!window.mapClickListenerActive) {
                window.google.maps.event.addListener(window.map, 'click', window.mapClickListenerFunction);
                window.mapClickListenerActive = true;
            }
            if (!window.mapIdleListenerActive) {
                window.google.maps.event.addListener(window.map, 'idle', window.mapIdleListenerFunction);
                window.mapIdleListenerActive = true;
            }
            if (!window.mapDragstartListenerActive) {
                window.google.maps.event.addListener(window.map, 'dragstart', window.mapDragstartListenerFunction);
                window.mapDragstartListenerActive = true;
            }
            if (!window.mapMousemoveListenerActive) {
                window.google.maps.event.addListener(window.map, 'mousemove', window.mapMousemoveListenerFunction);
                window.mapMousemoveListenerActive = true;
            }
        }

        if (heatmap) {
            heatmap.setMap(null);
        }

        if (playerMarker) {
            playerMarker.setMap(null);
        }
        // TODO: We don't need to keep these photos any more, currently they're just wasting resources or even causing bugs if the index gets corrupted somehow
        $.getJSON(streamUrl, $.extend({'b': date.getTime()}, qs), function (data) {
            $.merge(photos, data.photos);
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
            if (next || currentPhotoIdx <= 0) {
                nextPhoto();
            }
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
        console.log(guessResponse.currentScore);
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
        setTimeout(function () {
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
        }, 0);
        if (guessResponse.heatmapPoints) {
            window.mapDisplayHeatmapWithEstimatedLocation(guessResponse);
            window.marker.setMap(null);
            $('.center-marker').hide();
            window.mapMousemoveListenerActive = false;
            window.google.maps.event.clearListeners(window.map, 'mousemove');
            window.mapIdleListenerActive = false;
            window.google.maps.event.clearListeners(window.map, 'idle');
            window.mapClickListenerActive = false;
            window.google.maps.event.clearListeners(window.map, 'click');
            window.mapDragstartListenerActive = false;
            window.google.maps.event.clearListeners(window.map, 'dragstart');
            playerLatlng = new window.google.maps.LatLng(window.marker.getPosition().lat(), window.marker.getPosition().lng());
            //$('#ajapaik-game-map-geotag-count').html(guessResponse.heatmapPoints.length);
            //$('#ajapaik-game-map-geotag-with-azimuth-count').html(guessResponse.tagsWithAzimuth);
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
//            taxiData = [];
//            for (i = 0; i < guessResponse.heatmapPoints.length; i += 1) {
//                taxiData.push(new window.google.maps.LatLng(guessResponse.heatmapPoints[i][0], guessResponse.heatmapPoints[i][1]));
//            }
//            pointArray = new window.google.maps.MVCArray(taxiData);
//            heatmap = new window.google.maps.visualization.HeatmapLayer({
//                data: pointArray
//            });
//            heatmap.setOptions({radius: 50, dissipating: true});
//            heatmap.setMap(window.map);
        }
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

        loadPhotos();

        location = new window.google.maps.LatLng(window.start_location[1], window.start_location[0]);

        if (location) {
            window.getMap(location, 15, true);
        } else {
            window.getMap(undefined, undefined, true);
        }

        // To support touchscreens, we have an invisible marker underneath a fake one (otherwise it's laggy)
        window.marker = new window.google.maps.Marker({
            map: window.map,
            draggable: false,
            position: location,
            visible: false,
            icon: '/static/images/material-design-icons/ajapaik_photo_camera_arrow_drop_down_mashup.svg'
        });

        //window.marker.bindTo('position', window.map, 'center');

        window.realMapElement = $('#ajapaik-map-canvas')[0];
        window.realMapElement.addEventListener('mousewheel', window.wheelEventNonFF, true);
        window.realMapElement.addEventListener('DOMMouseScroll', window.wheelEventFF, true);

        window.mapClickListenerActive = true;
        window.google.maps.event.addListener(window.map, 'click', window.mapClickListenerFunction);
        window.mapIdleListenerActive = true;
        window.google.maps.event.addListener(window.map, 'idle', window.mapIdleListenerFunction);
        window.mapDragstartListenerActive = true;
        window.google.maps.event.addListener(window.map, 'dragstart', window.mapDragstartListenerFunction);

        window.google.maps.event.addListener(window.map, 'drag', function () {
            window.firstDragDone = true;
            window.setCursorToPanorama();
        });

        window.google.maps.event.addListener(window.map, 'dragend', window.mapDragendListenerFunction);

        window.google.maps.event.addDomListener(window, 'resize', window.windowResizeListenerFunction);

        window.google.maps.event.addListener(window.marker, 'position_changed', function () {
            window.disableSave = false;
        });

        // TODO: Re-implement
        //window.infoWindow = new google.maps.InfoWindow({
        //    content: '<div style="overflow:hidden;white-space:nowrap;">' + window.gettext('Point the marker to where the picture was taken from.') + '</div>'
        //});

        $.jQee('space', function () {
            if (window.BigScreen.enabled) {
                window.BigScreen.exit();
                window.fullscreenEnabled = false;
            }
            if (!locationToolsOpen) {
                $('.ajapaik-game-specify-location-button').click();
            }
        });

        $.jQee('enter', function () {
            if (locationToolsOpen) {
                if (window.guessResponseReceived) {
                    $('.ajapaik-game-feedback-next-button').click();
                } else {
                    if (!window.streetPanorama.getVisible()) {
                        // No saving in Street View
                        $('.ajapaik-save-location-button').click();
                    }
                }
            }
        });

        $.jQee('esc', function () {
            if (locationToolsOpen) {
                // Skipping photo on close Street View would be confusing
                if (!window.streetPanorama.getVisible()) {
                    $('.ajapaik-game-skip-photo-button').click();
                } else {
                    // Using escape to close street view must also show save button
                    window.saveLocationButton.show();
                    window.streetPanorama.setVisible(false);
                }
            }
        });

        $.jQee('up', function () {
            if (!locationToolsOpen && window.languageCode === 'et') {
                $('.ajapaik-game-show-description-button').click();
            }
        });

        $.jQee('f', function () {
            $('.ajapaik-flip-photo-overlay-button')[0].click();
        });

        $.jQee('right', function () {
            if (!locationToolsOpen) {
                $('.ajapaik-game-next-photo-button').click();
            } else {
                if (window.fullscreenEnabled) {
                    $('.ajapaik-game-next-photo-button').click();
                }
            }
        });

        //$('#google-plus-login-button').click(function () {
        //    _gaq.push(['_trackEvent', 'Game', 'Google+ login']);
        //});

        $('#logout-button').click(function () {
            _gaq.push(['_trackEvent', 'Game', 'Logout']);
        });

        $('.ajapaik-game-specify-location-button').click(function () {
            if (window.BigScreen.enabled) {
                window.BigScreen.exit();
                window.fullscreenEnabled = false;
            }
            if (!locationToolsOpen) {
                if (window.map.zoom < 17) {
                    window.map.setZoom(17);
                }
                $('#ajapaik-game-photo-modal').modal('hide');
                window.setCursorToAuto();
                $('.ajapaik-marker-center-lock-button').show();
                $('.ajapaik-show-tutorial-button').show();
                guessPhotoPanelContent = $('#ajapaik-game-guess-photo-js-panel-content');
                guessPhotoPanelContent.find('img').prop('src', mediaUrl + photos[currentPhotoIdx].big.url);
                if (!hintUsed) {
                    $('#ajapaik-game-guess-photo-description').hide();
                }
                if (!window.isMobile) {
                    $('.ajapaik-flip-photo-overlay-button').hide();
                    $('.ajapaik-fullscreen-overlay-button').hide();
                    $('.ajapaik-game-map-show-description-overlay-button').hide();
                }
                currentPhotoWidth = $('#ajapaik-game-guess-photo-container').find('img').width();
                guessPhotoPanelSettings.content = guessPhotoPanelContent.html();
                if (window.isMobile) {
                    // TODO: Make draggable and resizable also work on mobile
                    guessPhotoPanelSettings.draggable = false;
                    guessPhotoPanelSettings.resizable = false;
                }
                guessPhotoPanel = $.jsPanel(guessPhotoPanelSettings).css('max-width', currentPhotoWidth + 'px').css('max-height', $(window).height() - 200);
                tutorialPanelContent =  $('#ajapaik-game-tutorial-js-panel-content');
                if (!window.userClosedTutorial) {
                    window.openTutorialPanel();
                }
                $(guessPhotoPanel).css('max-width', currentPhotoWidth + 'px');
                $('#ajapaik-map-button-container').show();
                disableNext = false;
                locationToolsOpen = true;
            }
        });

        $('.ajapaik-game-skip-photo-button').click(function () {
            window.firstDragDone = false;
            window.setCursorToAuto();
            if (!disableNext) {
                var data = {photo_id: photos[currentPhotoIdx].id, origin: 'Game', csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')};
                $.post(window.saveLocationURL, data, function () {
                    currentPhotoIdx += 1;
                    nextPhoto();
                });
                $('#ajapaik-game-photo-modal').modal();
                $('#ajapaik-game-guess-photo').hide();
                $('#ajapaik-map-button-container').hide();
                if (feedbackPanel) {
                    feedbackPanel.close();
                }
                if (guessPhotoPanel) {
                    guessPhotoPanel.close();
                }
                window._gaq.push(['_trackEvent', 'Game', 'Skip photo']);
            }
        });

        $('.ajapaik-game-next-photo-button').click(function (e) {
            if (!nextPhotoLoading) {
                window.firstDragDone = false;
                window.setCursorToAuto();
                e.preventDefault();
                var data = {photo_id: photos[currentPhotoIdx].id, origin: 'Game', csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')};
                $.post(window.saveLocationURL, data, function () {
                    currentPhotoIdx += 1;
                    nextPhoto();
                });
                _gaq.push(['_trackEvent', 'Game', 'Skip photo']);
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

        saveLocationButton.click(function () {
            window.firstDragDone = false;
            window.setCursorToAuto();
            if (window.disableSave) {
                window._gaq.push(['_trackEvent', 'Game', 'Forgot to move marker']);
                window.alert(window.gettext('Drag the map so that the marker is where the photographer was standing. You can then set the direction of the view. You should also zoom the map before submitting your geotag.'));
            } else {
                window.saveLocation(window.marker, photos[currentPhotoIdx].id, photos[currentPhotoIdx].flip, hintUsed, userFlippedPhoto, window.degreeAngle, window.azimuthLineEndPoint, 'Game');
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
                photo_id: photos[currentPhotoIdx].id,
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            };
            $.post(difficultyFeedbackURL, data, function () {
                $.noop();
            });
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
            flipPhoto();
        });

        $(document).on('click', '.ajapaik-fullscreen-overlay-button', function () {
            if (window.BigScreen.enabled) {
                window.fullscreenEnabled = true;
                window.BigScreen.request($('#ajapaik-fullscreen-image-container')[0]);
                window._gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'historic-' + this.rel]);
                $('#ajapaik-game-full-screen-flip-button').show();
                if (hintUsed) {
                    $('#ajapaik-game-full-screen-description').html(photos[currentPhotoIdx].description).show();
                } else {
                    $('#ajapaik-game-full-screen-show-description-button').show();
                }
            }
        });

        $('.full-box img').on('click', function (e) {
            if (window.BigScreen.enabled) {
                e.preventDefault();
                window.BigScreen.exit();
                window.fullscreenEnabled = false;
            }
        });

        $(document).on('click', 'a.fullscreen', function (e) {
            e.preventDefault();
            if (window.BigScreen.enabled) {
                window.fullscreenEnabled = true;
                window.BigScreen.request($('#ajapaik-fullscreen-image-container')[0]);
                $('#ajapaik-game-full-screen-flip-button').show();
                if (hintUsed) {
                    $('#ajapaik-game-full-screen-description').html(photos[currentPhotoIdx].description).show();
                } else {
                    $('#ajapaik-game-full-screen-show-description-button').show();
                }
                window._gaq.push(['_trackEvent', 'Map', 'Full-screen', 'historic-' + this.rel]);
            }
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

        $('.ajapaik-game-show-description-button').click(function () {
            if (!hintUsed && photoHasDescription && window.languageCode === 'et') {
                $('.ajapaik-game-show-description-button').hide();
                hintUsed = true;
                $('#ajapaik-game-photo-description').show();
                $('#ajapaik-game-full-screen-description').html(photos[currentPhotoIdx].description).show();
                $('#ajapaik-game-full-screen-show-description-button').hide();
            }
        });

        $(document).on('mouseover', '#ajapaik-game-guess-photo-js-panel', function () {
            if (!window.isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
                $('.ajapaik-fullscreen-overlay-button').show();
                if (window.languageCode === 'et' && photoHasDescription && !hintUsed) {
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

        $(document).on('click', '.ajapaik-game-map-show-description-overlay-button', function () {
            // Weird selector to fix display remaining 'none' despite show()
            $(this).hide();
            hintUsed = true;
            $('#ajapaik-game-guess-photo-js-panel-footer div').show();
            $('#ajapaik-game-full-screen-description').html(photos[currentPhotoIdx].description).show();
            $('#ajapaik-game-full-screen-show-description-button').hide();
        });
    });
}(jQuery));