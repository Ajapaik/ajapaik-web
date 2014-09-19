(function () {
    "use strict";
    /*jslint nomen: true*/
    /*global google */
    /*global leaderboardUpdateURL */
    /*global flipFeedbackURL */
    /*global saveLocationURL */
    /*global leaderboardFullURL */
    /*global start_location */
    /*global city_id */
    /*global _gaq */
    /*global gettext */
    /*global language_code */
    /*global FB */
    /*global isMobile */
    /*global $ */
    /*global URI */

    // TODO: Sort global functionality into init.js, specific into game.js and browse.js respectively

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
        relativeVector = {},
        radianAngle,
        degreeAngle,
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
        reCalculateAzimuthOfMouseAndMarker,
        updateLeaderboard,
        marker,
        location,
        dottedLineSymbol,
        line,
        lastTriggeredWheeling,
        now,
        realMapElement,
        wheelEventFF,
        wheelEventNonFF,
        toggleTouchPhotoView,
        i,
        playerLatlng;

    updateLeaderboard = function () {
        $('#top').find('.score_container .scoreboard').load(leaderboardUpdateURL);
    };

    reCalculateAzimuthOfMouseAndMarker = function (e) {
        relativeVector.x = e.latLng.lat() - marker.position.lat();
        relativeVector.y = e.latLng.lng() - marker.position.lng();
        radianAngle = Math.atan2(relativeVector.y, relativeVector.x);
        degreeAngle = radianAngle * (180 / Math.PI);
        if (degreeAngle < 0) {
            degreeAngle += 360;
        }
    };

    toggleTouchPhotoView = function () {
        if (isMobile && locationToolsOpen) {
            if (mobileMapMinimized) {
                $('#tools').css({left: '15%'});
                mobileMapMinimized = false;
            } else {
                var photoWidthPercent = Math.round(($(currentPhoto).width()) / ($(document).width()) * 100);
                $('#tools').css({left: photoWidthPercent + '%'});
                mobileMapMinimized = true;
            }
        }
    };

    mapClickListenerFunction = function (e) {
        if (infowindow !== undefined) {
            infowindow.close();
            infowindow = undefined;
        }
        if (mobileMapMinimized) {
            toggleTouchPhotoView();
        }
        reCalculateAzimuthOfMouseAndMarker(e);
        if (azimuthListenerActive) {
            mapMousemoveListenerActive = false;
            google.maps.event.clearListeners(window.map, 'mousemove');
            saveDirection = true;
            $("#save-location").text(gettext('Save location and direction')).removeClass("medium").addClass("green");
            line.icons[0].repeat = '2px';
            line.setPath([marker.position, e.latLng]);
            line.setVisible(true);
        } else {
            if (!mapMousemoveListenerActive) {
                google.maps.event.addListener(window.map, 'mousemove', mapMousemoveListenerFunction);
                mapMousemoveListenerActive = true;
                google.maps.event.trigger(window.map, "mousemove", e);
            }
        }
        azimuthListenerActive = !azimuthListenerActive;
    };

    mapMousemoveListenerFunction = function (e) {
        // The mouse is moving, therefore we haven't locked on a direction
        $("#save-location").text(gettext('Save location only')).removeClass("medium").addClass("green");
        saveDirection = false;
        reCalculateAzimuthOfMouseAndMarker(e);
        if (!isMobile) {
            line.setPath([marker.position, e.latLng]);
            line.icons = [
                {icon: dottedLineSymbol, offset: '0', repeat: '7px'}
            ];
            line.setVisible(true);
        } else {
            line.setVisible(false);
        }
    };

    mapIdleListenerFunction = function () {
        if (firstDragDone) {
            marker.position = window.map.center;
            azimuthListenerActive = true;
            if (!mapMousemoveListenerActive) {
                google.maps.event.addListener(window.map, 'mousemove', mapMousemoveListenerFunction);
                mapMousemoveListenerActive = true;
            }

        }
    };

    mapDragstartListenerFunction = function () {
        if (mobileMapMinimized) {
            toggleTouchPhotoView();
        }
        line.setVisible(false);
        if (infowindow !== undefined) {
            infowindow.close();
            infowindow = undefined;
        }
        $("#save-location").text(gettext('Save location only')).removeClass("medium").addClass("green");
        azimuthListenerActive = false;
        line.setVisible(false);
        mapMousemoveListenerActive = false;
        google.maps.event.clearListeners(window.map, 'mousemove');
    };

    // Our own custom zooming functions to fix the otherwise laggy zooming
    wheelEventFF = function (e) {
        now = new Date().getTime();
        if (!lastTriggeredWheeling) {
            lastTriggeredWheeling = now - 250;
        }
        if (now - 250 > lastTriggeredWheeling) {
            lastTriggeredWheeling = now;
            if (e.detail > 0) {
                if (window.map.zoom < 18) {
                    window.map.setZoom(window.map.zoom + 1);
                }
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
                if (window.map.zoom < 18) {
                    window.map.setZoom(window.map.zoom + 1);
                }
            } else {
                if (window.map.zoom > 14) {
                    window.map.setZoom(window.map.zoom - 1);
                }
            }
        }
    };

    window.flipPhoto = function () {
        userFlippedPhoto = !userFlippedPhoto;
        var photoElement = $(".photo" + (currentPhotoIdx - 1)).find("img"),
            photoFullscreenElement = $("#game-full" + photos[currentPhotoIdx - 1].id).find("img");
        if (photoElement.hasClass("flip-photo")) {
            photoElement.removeClass("flip-photo");
        } else {
            photoElement.addClass("flip-photo");
        }
        if (photoFullscreenElement.hasClass("flip-photo")) {
            photoFullscreenElement.removeClass("flip-photo");
        } else {
            photoFullscreenElement.addClass("flip-photo");
        }
    };

    $(document).ready(function () {
        updateLeaderboard();

        loadPhotos();

        location = new google.maps.LatLng(start_location[1], start_location[0]);

        if (city_id) {
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

        dottedLineSymbol = {
            path: google.maps.SymbolPath.CIRCLE,
            strokeOpacity: 1,
            strokeWeight: 1.5,
            strokeColor: 'red',
            scale: 0.75
        };

        line = new google.maps.Polyline({
            geodesic: true,
            strokeOpacity: 0,
            icons: [
                {
                    icon: dottedLineSymbol,
                    offset: '0',
                    repeat: '7px'
                }
            ],
            visible: false,
            map: window.map,
            clickable: false
        });

        marker.bindTo('position', window.map, 'center');

        realMapElement = $("#map_canvas")[0];
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

        $.jQee('space', function () {
            // If tools is open, continue game
            if (locationToolsOpen && !disableContinue) {
                $('#continue-game').click();
            } else if (locationToolsOpen) {
                // Remove notice and center marker
                if (infowindow !== undefined) {
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

        $('.skip-photo').click(function (e) {
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

        photosDiv = $('#photos');

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
            }
        }, function () {
            if (locationToolsOpen === true && !isMobile) {
                hidePhotos();
            }
        });

        photosDiv.find('img').live('click', toggleTouchPhotoView);

        $('#top').find('.score_container').hoverIntent(showScoreboard, hideScoreboard);

        $('#full_leaderboard').bind('click', function (e) {
            e.preventDefault();
            $('#leaderboard_browser').find('.scoreboard').load(leaderboardFullURL, function () {
                $('#leaderboard_browser').modal({overlayClose: true});
            });
            _gaq.push(['_trackEvent', 'Game', 'Full leaderboard']);
        });

        function saveLocation() {
            lat = marker.getPosition().lat();
            lon = marker.getPosition().lng();

            var data = {
                photo_id: photos[currentPhotoIdx - 1].id,
                hint_used: hintUsed,
                zoom_level: window.map.zoom
            };

            if (saveDirection) {
                data['azimuth'] = degreeAngle;
            }

            if (lat && lon) {
                data['lat'] = lat;
                data['lon'] = lon;
            }

            if (userFlippedPhoto) {
                data['flip'] = !photos[currentPhotoIdx - 1].flip;
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
                    if (resp['azimuth_uncertain'] && resp['azimuth_false']) {
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

            $('#tools').animate({ left: '15%' }, function () {
                locationToolsOpen = true;
                var photosLeft = gameOffset - ($(document).width() / 2) + ($(currentPhoto).width() / 2);
                $('#photos').animate({ left: photosLeft + 'px' });
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

        function showPhotos() {
            var photoWidthPercent = Math.round(($(currentPhoto).width()) / ($(document).width()) * 100);
            $('#tools').animate({ left: photoWidthPercent + '%' });
        }

        function hidePhotos() {
            $('#tools').animate({ left: '15%' });
        }

        function showSeenAllMessage() {
            $('#user-message-container').show();
            $('#nothing-more-to-show').hide();
            $('#user-seen-all').show();
        }

        function showNothingMoreToShowMessage() {
            $('#user-message-container').show();
            $('#user-seen-all').hide();
            $('#nothing-more-to-show').show();
        }

        function showDescription() {
            $(currentPhoto).find('.show-description').fadeOut(function () {
                $(this).parent().find('.description').fadeIn();
            });
        }

        function nextPhoto() {
            hintUsed = 0;
            disableSave = true;
            azimuthListenerActive = false;
            window.map.setZoom(16);
            mapMousemoveListenerActive = false;
            google.maps.event.clearListeners(window.map, 'mousemove');
            if (line !== undefined) {
                line.setVisible(false);
            }

            if (photos.length > currentPhotoIdx) {
                disableNext = true;

                $('.skip-photo').animate({ 'opacity': 0.4 });
                $(currentPhoto).find('img').animate({ 'opacity': 0.4 });
                $(currentPhoto).find('.show-description').hide();

                photosDiv = $('#photos');
                photosDiv.append('<div class="photo photo' + currentPhotoIdx + '"></div>');

                currentPhoto = photosDiv.find('.photo' + currentPhotoIdx);

                $(currentPhoto).append(
                    '<div class="container"><a class="fullscreen" rel="' + photos[currentPhotoIdx].id + '"><img ' + (photos[currentPhotoIdx].flip ? 'class="flip-photo "' : '') + 'src="' + mediaUrl + photos[currentPhotoIdx].big.url + '" /></a><a onclick="window.flipPhoto();" class="btn flip" href="#" class="btn medium"></a><div class="fb-like"><fb:like href="' + permalinkURL + photos[currentPhotoIdx].id + '/" layout="button_count" send="false" show_faces="false" action="recommend"></fb:like></div>' + (language_code == 'et' ? '<a href="#" class="id' + photos[currentPhotoIdx].id + ' btn small show-description">' + gettext('Show description') + '</a>' : '') + '<div class="description">' + photos[currentPhotoIdx].description + '</div></div>'
                ).find('img').load(function () {
                    currentPhoto.css({ 'visibility': 'visible' });
                    $(this).fadeIn('slow', function () {
                        gameWidth += $(currentPhoto).width();
                        $('#photos').width(gameWidth);
                        scrollPhotos();
                    });
                });
                if (typeof FB !== 'undefined') {
                    FB.XFBML.parse();
                }
                $('#full-photos').append('<div class="full-box" style="/*chrome fullscreen fix*/"><div class="full-pic" id="game-full' + photos[currentPhotoIdx].id + '"><img ' + (photos[currentPhotoIdx].flip ? 'class="flip-photo "' : '') + 'src="' + mediaUrl + photos[currentPhotoIdx].large.url + '" border="0" /></div>');
                prepareFullscreen();
                currentPhotoIdx += 1;
            } else {
                loadPhotos(1);
            }
        }

        function scrollPhotos() {
            gameOffset = ($(document).width() / 2) + ($(currentPhoto).width() / 2) - gameWidth;
            $('#photos').animate({ left: gameOffset }, 1000, function () {
                disableNext = false;
                $('.skip-photo').animate({ 'opacity': 1 });
            });
        }

        function showScoreboard() {
            var topDiv = $('#top');
            topDiv.find('.score_container .scoreboard li').not('.you').add('h2').slideDown();
            topDiv.find('.score_container #facebook-connect').slideDown();
            topDiv.find('.score_container #google-plus-connect').slideDown();
        }

        function hideScoreboard() {
            var topDiv = $('#top');
            topDiv.find('.score_container .scoreboard li').not('.you').add('h2').slideUp();
            topDiv.find('.score_container #facebook-connect').slideUp();
            topDiv.find('.score_container #google-plus-connect').slideUp();
        }

        function loadPhotos(next) {
            // IE needs a different URL, sending seconds
            var date = new Date(),
                qs = URI.parseQuery(window.location.search);
            if (marker) {
                marker.setMap(window.map);
                $(".center-marker").show();
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

            $.getJSON(streamUrl, $.extend({
                'b': date.getTime()
            }, qs), function (data) {
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
    });
}());