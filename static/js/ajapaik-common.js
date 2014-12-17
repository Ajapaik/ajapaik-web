(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global google */
    /*global $ */
    /*global docCookies */
    /*global URI */
    /*global gettext */
    var saveLocationCallback;
    window.getAzimuthBetweenMouseAndMarker = function (e, marker) {
        var x = e.latLng.lat() - marker.position.lat(),
            y = e.latLng.lng() - marker.position.lng();
        return Math.atan2(y, x);
    };
    Math.degrees = function (rad) {
        var ret = rad * (180 / Math.PI);
        if (ret < 0) {
            ret += 360;
        }
        return ret;
    };
    Math.radians = function (degrees) {
        return degrees * Math.PI / 180;
    };
    Math.calculateMapLineEndPoint = function (azimuth, startPoint, lineLength) {
        azimuth = Math.radians(azimuth);
        var newX = Math.cos(azimuth) * lineLength + startPoint.lat(),
            newY = Math.sin(azimuth) * lineLength + startPoint.lng();
        return new google.maps.LatLng(newX, newY);
    };
    window.dottedAzimuthLineSymbol = {
        path: google.maps.SymbolPath.CIRCLE,
        strokeOpacity: 1,
        strokeWeight: 1.5,
        strokeColor: 'red',
        scale: 0.75
    };
    window.dottedAzimuthLine = new google.maps.Polyline({
        geodesic: false,
        strokeOpacity: 0,
        icons: [
            {
                icon: window.dottedAzimuthLineSymbol,
                offset: '0',
                repeat: '7px'
            }
        ],
        visible: false,
        clickable: false
    });
    $.ajaxSetup({
        headers: { 'X-CSRFToken': docCookies.getItem('csrftoken') }
    });
    window.getQueryParameterByName = function (name) {
        var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
        return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
    };
    window.prepareFullscreen = function (width, height) {
        if (!width || !height) {
            width = $(this).width();
            height = $(this).height();
        }
        $('.full-box img').load(function () {
            var that = $(this),
                aspectRatio = width / height,
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
    // Modal centering code from http://codepen.io/dimbslmh/pen/mKfCc
    window.adjustModalMaxHeightAndPosition = function () {
        $('.modal').each(function () {
            if ($(this).hasClass('in') === false) {
                $(this).show();
            }
            var contentHeight = $(window).height() - 60,
                headerHeight = $(this).find('.modal-header').outerHeight() || 2,
                footerHeight = $(this).find('.modal-footer').outerHeight() || 2;

            $(this).find('.modal-content').css({
                'max-height': function () {
                    return contentHeight;
                }
            });

            $(this).find('.modal-body').css({
                'max-height': function () {
                    return contentHeight - (headerHeight + footerHeight);
                }
            });

            $(this).find('.modal-dialog').addClass('modal-dialog-center').css({
                'margin-top': function () {
                    return -($(this).outerHeight() / 2);
                },
                'margin-left': function () {
                    return -($(this).outerWidth() / 2);
                }
            });
            if ($(this).hasClass('in') === false) {
                $(this).hide();
            }
        });
    };
    if ($(window).height() >= 320) {
        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
    }
    window.showScoreboard = function () {
        var scoreContainer = $('#ajapaik-header').find('.score_container');
        scoreContainer.find('.scoreboard li').not('.you').add('h2').slideDown();
        scoreContainer.find('#facebook-connect').slideDown();
        scoreContainer.find('#google-plus-connect').slideDown();
    };
    window.hideScoreboard = function () {
        var scoreContainer = $('#ajapaik-header').find('.score_container');
        scoreContainer.find('.scoreboard li').not('.you').add('h2').slideUp();
        scoreContainer.find('#facebook-connect').slideUp();
        scoreContainer.find('#google-plus-connect').slideUp();
    };
    window.updateLeaderboard = function () {
        $('.score_container').find('.scoreboard').load(window.leaderboardUpdateURL);
    };
    saveLocationCallback = function (resp) {
        var message = '',
            hideFeedback = false,
            heatmapPoints,
            currentScore,
            tagsWithAzimuth,
            newEstimatedLocation;
        if (resp.is_correct == true) {
            message = gettext('Looks right!');
            hideFeedback = false;
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
            hideFeedback = true;
            _gaq.push(['_trackEvent', 'Game', 'Wrong coordinates']);
        } else {
            message = gettext('Your guess was first.');
        }
        if (resp.heatmap_points) {
            heatmapPoints = resp.heatmap_points;
        }
        if (resp.azimuth_tags) {
            tagsWithAzimuth = resp.azimuth_tags;
        }
        if (resp.current_score) {
            currentScore = resp.current_score;
        }
        if (resp.new_estimated_location) {
            newEstimatedLocation = resp.new_estimated_location;
        }
        window.handleGuessResponse({feedbackMessage: message, hideFeedback: hideFeedback,
            heatmapPoints: heatmapPoints, currentScore: currentScore, tagsWithAzimuth: tagsWithAzimuth,
            newEstimatedLocation: newEstimatedLocation});
    };
    window.saveLocation = function (marker, photoId, photoFlipStatus, hintUsed, userFlippedPhoto, degreeAngle, azimuthLineEndPoint) {
        var lat = marker.getPosition().lat(),
            lon = marker.getPosition().lng(),
            data = {
                photo_id: photoId,
                hint_used: hintUsed,
                zoom_level: window.map.zoom
            };
        if (degreeAngle) {
            data.azimuth = degreeAngle;
        }
        if (azimuthLineEndPoint) {
            data.azimuth_line_end_point = azimuthLineEndPoint;
        }
        if (lat && lon) {
            data.lat = lat;
            data.lon = lon;
        }
        if (userFlippedPhoto) {
            data.flip = photoFlipStatus;
        }
        $.ajax({
            url: window.saveLocationURL,
            data: data,
            method: 'POST',
            success: function (resp) {
                saveLocationCallback(resp);
            }
        });
    };
    $('.filter-box select').change(function () {
        var uri = new URI(location.href),
            newQ = {city: $(this).val()},
            isFilterEmpty = false;
        uri.removeQuery(Object.keys(newQ));
        $.each(newQ, function (i, ii) {
            ii = String(ii);
            isFilterEmpty = ii === '';
        });

        if (!isFilterEmpty) {
            uri = uri.addQuery(newQ);
        }

        uri = uri.addQuery({fromSelect: 1});

        location.href = uri.toString();
    });
    // Firefox and Opera cannot handle modal taking over focus
    $.fn.modal.Constructor.prototype.enforceFocus = function () {
        $.noop();
    };
    // Our own custom zooming functions to fix the otherwise laggy zooming for mobile
    window.wheelEventFF = function (e) {
        window.now = new Date().getTime();
        if (!window.lastTriggeredWheeling) {
            window.lastTriggeredWheeling = window.now - 250;
        }
        if (window.now - 250 > window.lastTriggeredWheeling) {
            window.lastTriggeredWheeling = window.now;
            if (e.detail > 0) {
                window.map.setZoom(window.map.zoom + 1);
            } else {
                if (window.map.zoom > 14) {
                    window.map.setZoom(window.map.zoom - 1);
                }
            }
        }
    };
    window.wheelEventNonFF = function (e) {
        window.now = new Date().getTime();
        if (!window.lastTriggeredWheeling) {
            window.lastTriggeredWheeling = window.now - 100;
        }
        if (window.now - 100 > window.lastTriggeredWheeling) {
            window.lastTriggeredWheeling = window.now;
            if (e.wheelDelta > 0) {
                window.map.setZoom(window.map.zoom + 1);
            } else {
                if (window.map.zoom > 14) {
                    window.map.setZoom(window.map.zoom - 1);
                }
            }
        }
    };
}());