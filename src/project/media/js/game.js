(function () {
    "use strict";
    /*jslint nomen: true*/
    /*global google */
    /*global leaderboardUpdateURL */
    /*global start_location */
    /*global city_id */
    /*global map */
    /*global saveLocationURL */
    /*global _gaq */
    /*global gettext */
    /*global leaderboardFullURL */
    /*global language_code */
    /*global FB */
    /*global isMobile */

    var photos = [],
        gameOffset = 0,
        gameWidth = 0,
        currentPhotoIdx = 0,
        currentPhoto,
        hintUsed = 0,
        mediaUrl = '',
        streamUrl = '/stream/',
        disableNext = false,
        disableSave = true,
        disableContinue = true,
        locationToolsOpen = false,
        mobileMapMinimized = false,
        infowindow = undefined,
        photosDiv = undefined,
        noticeDiv = undefined,
        topDiv = undefined,
        lat = undefined,
        lon = undefined,
        relativeVector = {},
        radianAngle = undefined,
        degreeAngle = undefined,
        azimuthListenerActive = true,
        firstDragDone = false,
        saveDirection = false;

    function update_leaderboard () {
        $('#top').find('.score_container .scoreboard').load(leaderboardUpdateURL);
    }

    $(document).ready(function () {
        update_leaderboard();

        loadPhotos();

        var location = new google.maps.LatLng(start_location[1], start_location[0]);

        function reCalculateAzimuthOfMouseAndMarker (e) {
            relativeVector.x = e.latLng.lat() - marker.position.lat();
            relativeVector.y = e.latLng.lng() - marker.position.lng();
            radianAngle = Math.atan2(relativeVector.y, relativeVector.x);
            degreeAngle = radianAngle * (180 / Math.PI);
            if (degreeAngle < 0) {
              degreeAngle += 360;
            }
        }

        // Will load the base map layer and return it
        if (city_id) {
            map = get_map(start_location, 15, true);
        } else {
            map = get_map(undefined, undefined, true);
        }

        // To support touchscreens, we have an invisible marker underneath a fake one
        var marker = new google.maps.Marker({
            map: map,
            draggable: false,
            position: location,
            visible: false
        });

        var dottedLineSymbol = {
            path: google.maps.SymbolPath.CIRCLE,
            strokeOpacity: 1,
            strokeWeight: 1.5,
            strokeColor: 'red',
            scale: 0.75
        };

        var line = new google.maps.Polyline({
            geodesic: true,
            strokeOpacity: 0,
            icons: [{
                icon: dottedLineSymbol,
                offset: '0',
                repeat: '7px'
            }],
            visible: false,
            map: map,
            clickable: false
        });

        marker.bindTo('position', map, 'center');

        google.maps.event.addListener(map, 'click', function (e) {
            if (infowindow !== undefined) {
                infowindow.close();
                infowindow = undefined;
            }
            reCalculateAzimuthOfMouseAndMarker(e);
            if (azimuthListenerActive) {
                google.maps.event.clearListeners(map, 'mousemove');
                saveDirection = true;
                $("#save-location").text(gettext('Save location and direction')).removeClass("medium").addClass("green");
                line.icons[0].repeat = '2px';
                line.setPath([marker.position, e.latLng]);
                line.setVisible(true);
            } else {
                addMouseMoveListener();
                google.maps.event.trigger(map, "mousemove", e);
            }
            azimuthListenerActive = !azimuthListenerActive;
        });

        function addMouseMoveListener () {
            google.maps.event.addListener(map, 'mousemove', function (e) {
                // The mouse is moving, therefore we haven't locked on a direction
                $("#save-location").text(gettext('Save location only')).removeClass("medium").addClass("green");
                saveDirection = false;
                reCalculateAzimuthOfMouseAndMarker(e);
                if (!isMobile) {
                    line.setPath([marker.position, e.latLng]);
                    line['icons'] = [{icon: dottedLineSymbol, offset: '0', repeat: '7px'}];
                    line.setVisible(true);
                } else {
                    line.setVisible(false);
                }
            });
        }

        google.maps.event.addListener(map, 'idle', function () {
            if (firstDragDone) {
                marker.position = map.center;
                azimuthListenerActive = true;
                addMouseMoveListener();
            }
        });

        google.maps.event.addListener(map, 'dragstart', function () {
            line.setVisible(false);
            if (infowindow !== undefined) {
                infowindow.close();
                infowindow = undefined;
            }
            $("#save-location").text(gettext('Save location only')).removeClass("medium").addClass("green");
            azimuthListenerActive = false;
            line.setVisible(false);
            google.maps.event.clearListeners(map, 'mousemove');
        });

        google.maps.event.addListener(map, 'drag', function () {
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
                marker.setMap(map);
                marker.setPosition(map.getCenter());
            } else {
                // Otherwise open tools
                $('#open-location-tools').click();
            }
        });

        $.jQee('enter', function () {
            // Save location only if Tools open and no result window
            if (locationToolsOpen && disableContinue) {
                $('#save-location').click();
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
            openLocationTools();
        });

        $('#close-location-tools').click(function (e) {
            e.preventDefault();
            closeLocationTools();
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
                alert(gettext('Point the marker to where the picture was taken from.'));
            } else {
                saveLocation();
                _gaq.push(['_trackEvent', 'Game', 'Save location']);
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
            if (locationToolsOpen == true && !isMobile) {
                showPhotos();
            }
        }, function () {
            if (locationToolsOpen == true && !isMobile) {
                hidePhotos();
            }
        });

        photosDiv.find('img').live('click', function () {
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
        });

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

            if (photos)

            var data = {
                photo_id: photos[currentPhotoIdx - 1].id,
                hint_used: hintUsed,
                zoom_level: map.zoom
            };

            if (saveDirection) {
                data['azimuth'] = degreeAngle;
            }

            if (lat && lon) {
                data['lat'] = lat;
                data['lon'] = lon;
            }

            $.post(saveLocationURL, data, function (resp) {
                update_leaderboard();
                var message = '';
                if (resp['is_correct'] == true) {
                    message = gettext('Looks right!');
                    if (resp['azimuth_false']) {
                        message = gettext('The location seems right, but not the azimuth.');
                    }
                    if (resp['azimuth_uncertain']) {
                        message = gettext('The location seems right, but the azimuth is yet uncertain.');
                    }
                }
                else if (resp['location_is_unclear']) {
                    message = gettext('Correct location is not certain yet.');
                }
                else if (resp['is_correct'] == false) {
                    message = gettext('We doubt about it.');
                }
                else {
                    message = gettext('Your guess was first.');
                }
                noticeDiv = $("#notice");
                noticeDiv.find(".message").text(message);
                noticeDiv.modal({escClose: false});
                disableContinue = false;
            }, 'json');
        }

        function openLocationTools() {
            disableNext = true;
            if (infowindow !== undefined) {
                // Show info window when the map is opened the first time
                infowindow.open(map, marker);
            }

            $('#tools').animate({ left: '15%' }, function () {
                locationToolsOpen = true;
                var photosLeft = gameOffset - ($(document).width() / 2) + ($(currentPhoto).width() / 2);
                $('#photos').animate({ left: photosLeft + 'px' });
                $('#open-location-tools').fadeOut();
            });
        }

        function continueGame() {
            $.modal.close();
            closeLocationTools(1);
            disableContinue = true;
        }

        function closeLocationTools(next) {
            locationToolsOpen = false;
            $('#photos').animate({ left: gameOffset });
            $('#tools').animate({ left: '100%' }, function () {
                var panorama = map.getStreetView();
                panorama.setVisible(false);
                disableNext = false;
                $('#open-location-tools').fadeIn();
                if (next == 1) {
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

        function showScoreboard() {
            topDiv = $('#top');
            topDiv.find('.score_container .scoreboard li').not('.you').add('h2').slideDown();
            topDiv.find('.score_container #facebook-connect').slideDown();
            topDiv.find('.score_container #google-plus-connect').slideDown();
        }

        function hideScoreboard() {
            topDiv = $('#top');
            topDiv.find('.score_container .scoreboard li').not('.you').add('h2').slideUp();
            topDiv.find('.score_container #facebook-connect').slideUp();
            topDiv.find('.score_container #google-plus-connect').slideUp();
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
            map.setZoom(16);
            google.maps.event.clearListeners(map, 'mousemove');
            if (line !== undefined) {
                line.setVisible(false);
            }

            if (photos.length > currentPhotoIdx) {
                disableNext = true;

                $('.skip-photo').animate({ 'opacity': .4 });
                $(currentPhoto).find('img').animate({ 'opacity': .4 });
                $(currentPhoto).find('.show-description').hide();

                photosDiv = $('#photos');
                photosDiv.append('<div class="photo photo' + currentPhotoIdx + '"></div>');

                currentPhoto = photosDiv.find('.photo' + currentPhotoIdx);

                $(currentPhoto).append(
                        '<div class="container"><a class="fullscreen" rel="' + photos[currentPhotoIdx].id + '"><img src="' + mediaUrl + photos[currentPhotoIdx].big.url + '" /></a><div class="fb-like"><fb:like href="' + permalinkURL + photos[currentPhotoIdx].id + '/" layout="button_count" send="false" show_faces="false" action="recommend"></fb:like></div>' + (language_code == 'et' ? '<a href="#" class="id' + photos[currentPhotoIdx].id + ' btn small show-description">' + gettext('Show description') + '</a>' : '') + '<div class="description">' + photos[currentPhotoIdx].description + '</div></div>'
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
                $('#full-photos').append('<div class="full-box" style="/*chrome fullscreen fix*/"><div class="full-pic" id="game-full' + photos[currentPhotoIdx].id + '"><img src="' + mediaUrl + photos[currentPhotoIdx].large.url + '" border="0" /></div>');
                prepareFullscreen();
                currentPhotoIdx++;
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

        function loadPhotos(next) {
            var date = new Date(); // IE needs a different URL, sending seconds
            var qs = URI.parseQuery(window.location.search);

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
    })
}());
