(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global google */
    /*global $ */
    /*global docCookies */
    /*global URI */
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
    window.prepareFullscreen = function () {
        $('.full-box img').load(function () {
            var that = $(this),
                aspectRatio = that.width() / that.height(),
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
    $('.filter-box select').change(function () {
        var uri = new URI(location.href),
            newQ = URI.parseQuery($(this).val()),
            isFilterEmpty = false;
        uri.removeQuery(Object.keys(newQ));
        $.each(newQ, function (i, ii) {
            ii = String(ii);
            isFilterEmpty = ii === '';
        });

        if (!isFilterEmpty) {
            uri = uri.addQuery(newQ);
        }
        location.href = uri.toString();
    });
}());