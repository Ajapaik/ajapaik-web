(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global google */
    /*global leaderboardUpdateURL */
    /*global flipFeedbackURL */
    /*global saveLocationURL */
    /*global leaderboardFullURL */
    /*global start_location */
    /*global cityId */
    /*global _gaq */
    /*global gettext */
    /*global language_code */
    /*global FB */
    /*global isMobile */
    /*global $ */
    /*global URI */

    var photos = [],
        gameOffset = 0,
        gameWidth = 0,
        currentPhotoIdx = 0,
        currentPhoto,
        hintUsed = 0,
        mediaUrl = '',
        streamUrl = '/stream/',
        difficultyFeedbackURL = '/difficulty_feedback/',
        disableNext = false,
        disableSave = true,
        disableContinue = true,
        locationToolsOpen = false,
        mobileMapMinimized = false,
        infowindow,
        photosDiv,
        noticeDiv,
        lat,
        lon,
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
        updateLeaderboard,
        marker,
        location,
        lastTriggeredWheeling,
        now,
        realMapElement,
        wheelEventFF,
        wheelEventNonFF,
        toggleTouchPhotoView,
        i,
        playerLatlng,
        centerMarker = $('.center-marker'),
        showNothingMoreToShowMessage,
        showSeenAllMessage,
        nextPhoto,
        hideTools,
        scrollPhotos,
        photosDivSlidInPlace = false;

    updateLeaderboard = function () {
        $('.score_container').find('.scoreboard').load(leaderboardUpdateURL);
    };

    toggleTouchPhotoView = function () {
        //TODO: Renew
        /*if (isMobile && locationToolsOpen) {
            if (mobileMapMinimized) {
                $('#tools').css({left: '15%'});
                mobileMapMinimized = false;
            } else {
                var photoWidthPercent = Math.round(($(currentPhoto).width()) / ($(document).width()) * 100);
                $('#tools').css({left: photoWidthPercent + '%'});
                mobileMapMinimized = true;
            }
        }*/
        $.noop();
    };

    mapClickListenerFunction = function (e) {
        if (infowindow !== undefined) {
            centerMarker.show();
            infowindow.close();
            infowindow = undefined;
        }
        if (mobileMapMinimized) {
            toggleTouchPhotoView();
        }
        radianAngle = window.getAzimuthBetweenMouseAndMarker(e, marker);
        azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
        degreeAngle = Math.degrees(radianAngle);
        if (azimuthListenerActive) {
            mapMousemoveListenerActive = false;
            google.maps.event.clearListeners(window.map, 'mousemove');
            saveDirection = true;
            $('.ajapaik-game-save-location-button').text(gettext('Save location and direction'));
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
        $('.ajapaik-game-save-location-button').text(gettext('Save location only'));
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

    mapIdleListenerFunction = function () {
        if (firstDragDone) {
            marker.position = window.map.center;
            azimuthListenerActive = true;
            centerMarker
                .css('background-image', 'url("http://maps.gstatic.com/intl/en_ALL/mapfiles/drag_cross_67_16.png")')
                .css('margin-left', '-8px')
                .css('margin-top', '-9px');
            //TODO: This is probably causing a bug with the azimuth line appearing/disappearing abnormally
            if (!mapMousemoveListenerActive) {
                google.maps.event.addListener(window.map, 'mousemove', mapMousemoveListenerFunction);
                mapMousemoveListenerActive = true;
            }
        }
    };

    mapDragstartListenerFunction = function () {
        centerMarker = $('.center-marker');
        if (mobileMapMinimized) {
            toggleTouchPhotoView();
        }
        window.dottedAzimuthLine.setVisible(false);
        if (infowindow !== undefined) {
            centerMarker.show();
            infowindow.close();
            infowindow = undefined;
        }
        centerMarker
            .css('background-image', 'url("/static/images/ajapaik_marker_35px_cross.png")')
            .css('margin-left', '-17px')
            .css('margin-top', '-55px')
            .css('height', '60px');
        $('.ajapaik-game-save-location-button').text(gettext('Save location only'));
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

    showNothingMoreToShowMessage = function () {
        $('#ajapaik-game-user-message-container').show();
        $('#ajapaik-game-user-seen-all-message').hide();
        $('#ajapaik-game-nothing-more-to-show-message').show();
    };

    showSeenAllMessage = function () {
        $('#ajapaik-game-user-message-container').show();
        $('#ajapaik-game-nothing-more-to-show-message').hide();
        $('#ajapaik-game-user-seen-all-message').show();
    };

    //TODO: Remove?
    /*hideTools = function () {
        $(currentPhoto).find('.game-photo-tools').hide();
    };*/

    /*scrollPhotos = function () {
        gameOffset = ($(document).width() / 2) + ($(currentPhoto).width() / 2) - gameWidth;
        $('#photos').animate({ left: gameOffset }, 1000, function () {
            disableNext = false;
            $('.skip-photo').animate({ 'opacity': 1 });
        });
    };*/

    nextPhoto = function () {
        hintUsed = 0;
        disableSave = true;
        //photosDivSlidInPlace = false;
        //photosDiv.removeClass('map-open-hide-photos');
        azimuthListenerActive = false;
        window.map.setZoom(16);
        mapMousemoveListenerActive = false;
        //hideTools();
        google.maps.event.clearListeners(window.map, 'mousemove');
        if (window.dottedAzimuthLine !== undefined) {
            window.dottedAzimuthLine.setVisible(false);
        }
        if (photos.length > currentPhotoIdx) {
            disableNext = true;
            $('#ajapaik-game-modal-photo').prop('src', mediaUrl + photos[currentPhotoIdx].large.url).on('load', function () {
                $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
            });
            disableNext = true;
            if (typeof FB !== 'undefined') {
                FB.XFBML.parse();
            }
            /*$('.skip-photo').animate({ 'opacity': 0.4 });
            $(currentPhoto).find('img').animate({ 'opacity': 0.4 });
            $(currentPhoto).find('.show-description').hide();
            photosDiv = $('#photos');
            photosDiv.append('<div class="photo photo' + currentPhotoIdx + '"></div>');
            currentPhoto = photosDiv.find('.photo' + currentPhotoIdx);
            var newContainer = document.createElement('div'),
                newFullscreen = document.createElement('a'),
                newFullscreenImage = document.createElement('img');
            if (photos[currentPhotoIdx].flip) {
                $(newFullscreenImage).addClass('flip-photo');
            }
            $(newFullscreenImage).attr('src', mediaUrl + photos[currentPhotoIdx].big.url);
            $(newFullscreen).attr('rel', photos[currentPhotoIdx].id).append(newFullscreenImage);
            $(newContainer).append(newFullscreen);
            $(currentPhoto).append(
                '<div class="container"><a class="fullscreen" rel="' + photos[currentPhotoIdx].id + '"><img ' + (photos[currentPhotoIdx].flip ? 'class="flip-photo "' : '') + 'src="' + mediaUrl + photos[currentPhotoIdx].big.url + '" /></a><div class="game-photo-tools"><a onclick="window.flipPhoto();" class="btn flip" href="#" class="btn medium"></a><div class="fb-like"><fb:like href="' + permalinkURL + photos[currentPhotoIdx].id + '/" layout="button_count" send="false" show_faces="false" action="recommend"></fb:like></div>' + (language_code == 'et' ? '<a href="#" class="id' + photos[currentPhotoIdx].id + ' btn small show-description">' + gettext('Show description') + '</a>' : '') + '</div><div class="description">' + photos[currentPhotoIdx].description + '</div></div>'
            ).find('img').load(function () {
                currentPhoto.css({ 'visibility': 'visible' });
                $(this).fadeIn('slow', function () {
                    gameWidth += $(currentPhoto).width();
                    $('#photos').width(gameWidth);
                    scrollPhotos();
                });
            });
            $('#full-photos').append('<div class="full-box" style="*//*chrome fullscreen fix*//*"><div class="full-pic" id="game-full' + photos[currentPhotoIdx].id + '"><img ' + (photos[currentPhotoIdx].flip ? 'class="flip-photo "' : '') + 'src="' + mediaUrl + photos[currentPhotoIdx].large.url + '" border="0" /></div>');
            prepareFullscreen();
            currentPhotoIdx += 1;*/
        } else {
            loadPhotos(1);
        }
    };

    function loadPhotos(next) {
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
            if (data.nothing_more_to_show) {
                showNothingMoreToShowMessage();
            } else if (data.user_seen_all) {
                showSeenAllMessage();
            }
            if (next || currentPhotoIdx <= 0) {
                nextPhoto();
            }
        });
    }

    window.flipPhoto = function () {
        userFlippedPhoto = !userFlippedPhoto;
        var photoElement = $('.photo' + (currentPhotoIdx - 1)).find('img'),
            photoFullscreenElement = $('#game-full' + photos[currentPhotoIdx - 1].id).find('img');
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

    $(document).ready(function () {
        updateLeaderboard();

        $.jQee("esc", function () {
            $("#close-photo-drawer").click();
            $("#close-location-tools").click();
        });

        $.jQee("shift+r", function () {
            $("#random-photo").click();
        });

        $('#ajapaik-game-photo-modal').modal({
            backdrop: 'static',
            keyboard: false
        });

        loadPhotos();

        location = new google.maps.LatLng(start_location[1], start_location[0]);

        if (cityId) {
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
        });
        google.maps.event.addListener(marker, 'position_changed', function () {
            disableSave = false;
        });

        infowindow = new google.maps.InfoWindow({
            content: '<div style="overflow:hidden;white-space:nowrap;">' + gettext('Point the marker to where the picture was taken from.') + '</div>'
        });

        //$(".center-marker").hide();
        $(".center-marker")
            .css("background-image", "url('http://maps.gstatic.com/intl/en_ALL/mapfiles/drag_cross_67_16.png')")
            .css("margin-left", "-8px")
            .css("margin-top", "-9px");

        $.jQee('space', function () {
            // If tools is open, continue game
            if (locationToolsOpen && !disableContinue) {
                $('#continue-game').click();
            } else if (locationToolsOpen) {
                // Remove notice and center marker
                if (infowindow !== undefined) {
                    $(".center-marker").show();
                    infowindow.close();
                    infowindow = undefined;
                }
                marker.setMap(window.map);
                marker.setPosition(window.map.getCenter());
            } else {
                // Otherwise open tools
                $('#open-location-tools').click();
            }
        });

        $.jQee('enter', function () {
            // Save location only if Tools open and no result window
            if (locationToolsOpen && disableContinue) {
                $('#save-location').click();
            } else {
                continueGame();
            }
        });

        $.jQee('up', function () {
            $('.show-description').click();
        });

        $.jQee('right', function () {
            $('#skip-photo').click();
        });

        $('.ajapaik-game-next-photo-button').click(function (e) {
            firstDragDone = false;
            e.preventDefault();
            if (disableNext == false) {
                var data = {photo_id: photos[currentPhotoIdx - 1].id};
                $.post(saveLocationURL, data, function () {
                    nextPhoto();
                });
                _gaq.push(['_trackEvent', 'Game', 'Skip photo']);
            }
        });

        $('#open-location-tools').click(function (e) {
            e.preventDefault();
            _gaq.push(["_trackEvent", "Game", "Opened location tools"]);
            openLocationTools();
        });

        $('#close-location-tools').click(function (e) {
            e.preventDefault();
            _gaq.push(["_trackEvent", "Game", "Closed location tools"]);
            closeLocationTools();
        });

        $('#google-plus-login-button').click(function () {
            _gaq.push(["_trackEvent", "Game", "Google+ login"]);
        });

        $('#logout-button').click(function () {
            _gaq.push(["_trackEvent", "Game", "Logout"]);
        });

        $('#continue-game').click(function (e) {
            e.preventDefault();
            continueGame();
        });

        $('.ajapaik-game-specify-location-button').click(function () {
            $('#ajapaik-game-photo-modal').modal('hide');
            $('#ajapaik-game-guess-photo').prop('src', mediaUrl + photos[currentPhotoIdx].large.url).show();
            $('.ajapaik-game-save-location-button').show();
            $('.ajapaik-game-skip-photo-button').show();
            disableNext = false;
        });

        $('.ajapaik-game-skip-photo-button').click(function (e) {
            firstDragDone = false;
            e.preventDefault();
            if (disableNext == false) {
                var data = {photo_id: photos[currentPhotoIdx].id};
                $.post(saveLocationURL, data, function () {
                    nextPhoto();
                });
                $('#ajapaik-game-photo-modal').modal();
                $('#ajapaik-game-guess-photo').hide();
                $('.ajapaik-game-save-location-button').hide();
                $('.ajapaik-game-skip-photo-button').hide();
                _gaq.push(['_trackEvent', 'Game', 'Skip photo']);
            }
        });

        $('#full_leaderboard').bind('click', function (e) {
            e.preventDefault();
            $('#leaderboard_browser').find('.scoreboard').load(leaderboardFullURL, function () {
                $('#ajapaik-game-full-leaderboard-modal').modal().on('shown.bs.modal', function () {
                    $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                });
            });
            _gaq.push(['_trackEvent', 'Game', 'Full leaderboard']);
        });

        $('#save-location').click(function (e) {
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

        //TODO: Restore necessary parts
        /*photosDiv = $('#photos');

        photosDiv.delegate('.show-description', 'click', function (e) {
            e.preventDefault();
            hintUsed = 1;
            showDescription();
            _gaq.push(['_trackEvent', 'Game', 'Show description']);
        });

        photosDiv.find('a.fullscreen').live('click', function (e) {
            e.preventDefault();
            if (BigScreen.enabled) {
                BigScreen.request($('#game-full' + this.rel)[0]);
                _gaq.push(['_trackEvent', 'Game', 'Full-screen', 'historic-' + this.rel]);
            }
        });

        $('.full-box div').live('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.exit();
            }
        });

        photosDiv.hoverIntent(function () {
            if (locationToolsOpen === true && !isMobile) {
                showPhotos();
            } else if (locationToolsOpen === false && !isMobile) {
                showTools();
            }
        }, function () {
            if (locationToolsOpen === true && !isMobile) {
                hidePhotos();
            } else if (locationToolsOpen === false && !isMobile) {
                hideTools();
            }
        });

        photosDiv.find('img').live('click', toggleTouchPhotoView).live('mouseover', function () {
            if (locationToolsOpen && photosDivSlidInPlace) {
                $('#photos').addClass('map-open-hide-photos');
            }
        });*/


        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

        function saveLocation() {
            lat = marker.getPosition().lat();
            lon = marker.getPosition().lng();

            var data = {
                photo_id: photos[currentPhotoIdx - 1].id,
                hint_used: hintUsed,
                zoom_level: window.map.zoom
            };

            if (saveDirection) {
                data.azimuth = degreeAngle;
                data.azimuth_line_end_point = azimuthLineEndPoint;
            }

            if (lat && lon) {
                data.lat = lat;
                data.lon = lon;
            }

            if (userFlippedPhoto) {
                data.flip = !photos[currentPhotoIdx - 1].flip;
            }

            $.post(saveLocationURL, data, function (resp) {
                updateLeaderboard();
                var message = '',
                    hide_feedback = false;
                if (resp['is_correct'] == true) {
                    message = gettext('Looks right!');
                    hide_feedback = false;
                    _gaq.push(['_trackEvent', 'Game', 'Correct coordinates']);
                    if (resp['azimuth_false']) {
                        message = gettext('The location seems right, but not the azimuth.');
                    }
                    if (resp['azimuth_uncertain']) {
                        message = gettext('The location seems right, but the azimuth is yet uncertain.');
                    }
                    if (resp['azimuth_uncertain'] && resp['azimuth_tags'] < 2) {
                        message = gettext('The location seems right, your azimuth was first.');
                    }
                } else if (resp['location_is_unclear']) {
                    message = gettext('Correct location is not certain yet.');
                    _gaq.push(['_trackEvent', 'Game', 'Coordinates uncertain']);
                } else if (resp['is_correct'] == false) {
                    message = gettext('We doubt about it.');
                    hide_feedback = true;
                    _gaq.push(['_trackEvent', 'Game', 'Wrong coordinates']);
                } else {
                    message = gettext('Your guess was first.');
                }
                noticeDiv = $("#notice");
                if (hide_feedback) {
                    noticeDiv.find(".difficulty-message").hide();
                    noticeDiv.find("#difficulty-form").hide();
                }
                noticeDiv.find(".message").text(message);
                noticeDiv.find(".points-gained-message").text(gettext("Points awarded") + ": " + resp["current_score"]);
                noticeDiv.find(".geotag-count-message").text(gettext("Amount of geotags for this photo") + ": " + resp["heatmap_points"].length);
                noticeDiv.find(".azimuth-count-message").text(gettext("Amount of azimuths for this photo") + ": " + resp["azimuth_tags"]);
                noticeDiv.modal({escClose: false, autoPosition: false, modal: false});
                disableContinue = false;
                if (resp.heatmap_points) {
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
                    playerLatlng = new google.maps.LatLng(data.lat, data.lon);
                    var markerImage = {
                        url: 'http://maps.gstatic.com/intl/en_ALL/mapfiles/drag_cross_67_16.png',
                        origin: new google.maps.Point(0, 0),
                        anchor: new google.maps.Point(8, 8),
                        scaledSize: new google.maps.Size(16, 16)
                    };
                    playerMarker = new google.maps.Marker({
                        position: playerLatlng,
                        map: window.map,
                        title: gettext("Your guess"),
                        draggable: false,
                        icon: markerImage
                    });
                    taxiData = [];
                    for (i = 0; i < resp.heatmap_points.length; i += 1) {
                        taxiData.push(new google.maps.LatLng(resp.heatmap_points[i][0], resp.heatmap_points[i][1]));
                    }
                    pointArray = new google.maps.MVCArray(taxiData);
                    heatmap = new google.maps.visualization.HeatmapLayer({
                        data: pointArray
                    });
                    heatmap.setOptions({radius: 50, dissipating: true});
                    heatmap.setMap(window.map);
                }
            }, 'json');
        }

        function openLocationTools() {
            disableNext = true;
            if (infowindow !== undefined) {
                // Show info window when the map is opened the first time
                infowindow.open(window.map, marker);
            }
            $("#photos").addClass("map-open-show-photos");
            $('#tools').animate({ left: '15%' }, function () {
                locationToolsOpen = true;
                var photosLeft = gameOffset - ($(document).width() / 2) + ($(currentPhoto).width() / 2);
                $('#photos').animate({ left: photosLeft + 'px' }, function () {
                    photosDivSlidInPlace = true;
                });
                $('#open-location-tools').fadeOut();
            });
        }

        function continueGame() {
            var data = {
                level: $('input[name=difficulty]:checked', '#difficulty-form').val(),
                photo_id: photos[currentPhotoIdx - 1].id
            };
            $.post(difficultyFeedbackURL, data, function () {
            });
            $.modal.close();
            closeLocationTools(1);
            disableContinue = true;
        }

        function closeLocationTools(next) {
            locationToolsOpen = false;
            $("#photos").removeClass("map-open-show-photos");
            $('#photos').animate({ left: gameOffset });
            $('#tools').animate({ left: '100%' }, function () {
                var panorama = window.map.getStreetView();
                panorama.setVisible(false);
                disableNext = false;
                $('#open-location-tools').fadeIn();
                if (parseInt(next) === 1) {
                    nextPhoto();
                }
            });
        }

        //TODO: Restore necessary
        /*function showPhotos() {
            //var photoWidthPercent = Math.round(($(currentPhoto).width()) / ($(document).width()) * 100);
            //$('#tools').animate({ left: photoWidthPercent + '%' });
            $("#photos").hide();
        }

        function showTools() {
            //$("a.btn.flip").show();
            //$(".fb-like").show();
            //$(".show-description").show();
            $(currentPhoto).find(".game-photo-tools").show();
        }

        function hidePhotos() {
            $('#tools').animate({ left: '15%' });
            $("#photos").show();
        }

        function showDescription() {
            $(currentPhoto).find('.show-description').fadeOut(function () {
                $(this).parent().parent().find('.description').fadeIn();
            });
        }*/
    });
}());