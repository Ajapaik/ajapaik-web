(function () {
    'use strict';
    /*jslint nomen: true */
    /*global FB */
    /*global geotaggedPhotos */
    /*global _gaq */
    /*global markers */
    /*global cityId */
    /*global google */
    /*global userAlreadySeenPhotoIds */
    /*global $ */
    /*global History */
    /*global BigScreen */
    /*global leaderboardFullURL */
    /*global rephotoImgHref */
    /*global rephotoImgSrc */
    /*global rephotoImgSrcFs */
    /*global rephotoMeta */
    /*global rephotoComment */

    var photoId,
        photoDrawerElement = $('#photo-drawer'),
        photoPaneContainer = $('#photo-pane-container'),
        photoPane = $('#photo-pane'),
        detachedPhotos = {},
        i = 0,
        maxIndex = 2,
        lastHighlightedMarker,
        lastSelectedPaneElement,
        dottedLineSymbol = {
            path: google.maps.SymbolPath.CIRCLE,
            strokeOpacity: 1,
            strokeWeight: 1.5,
            strokeColor: 'red',
            scale: 0.75
        },
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
            clickable: false
        }),
        lineLength = 0.01,
        lastSelectedMarkerId,
        currentlySelectedMarkerId,
        targetPaneElement,
        markerTemp,
        justifiedGallerySettings = {
            waitThumbnailsLoad: false,
            rowHeight: 120,
            margins: 3,
            sizeRangeSuffixes: {
                'lt100': '',
                'lt240': '',
                'lt320': '',
                'lt500': '',
                'lt640': '',
                'lt1024': ''
            }
        },
        lastEvent,
        mapRefreshInterval = 500,
        openPhotoDrawer,
        closePhotoDrawer,
        toggleVisiblePaneElements,
        calculateLineEndPoint,
        fireIfLastEvent,
        scheduleDelayedCallback,
        setCorrectMarkerIcon,
        blueSvgIconUrl = '/static/images/ajapaik-dot-blue.svg',
        blackSvgIconUrl = '/static/images/ajapaik-dot-black.svg',
        blackMarkerIcon20 = '/static/images/ajapaik_marker_20px.png',
        blackMarkerIcon35 = '/static/images/ajapaik_marker_35px.png',
        blueMarkerIcon20 = '/static/images/ajapaik_marker_20px_blue.png',
        blueMarkerIcon35 = '/static/images/ajapaik_marker_35px_blue.png';

    Math.radians = function (degrees) {
        return degrees * Math.PI / 180;
    };

    window.loadPhoto = function (id) {
        $.post('/log_user_map_action/', {user_action: 'opened_drawer', photo_id: id}, function () {
            $.noop();
        });
        photoId = id;
        $.ajax({
            cache: false,
            url: '/foto/' + id + '/',
            success: function (result) {
                openPhotoDrawer(result);
                if (FB !== undefined) {
                    FB.XFBML.parse();
                }
                $('a.iframe').fancybox({
                    'width': '75%',
                    'height': '75%',
                    'autoScale': false,
                    'hideOnContentClick': false
                });
            }
        });
    };

    openPhotoDrawer = function (content) {
        photoDrawerElement.html(content);
        photoDrawerElement.animate({ top: '7%' });
    };

    closePhotoDrawer = function () {
        photoDrawerElement.animate({ top: '-1000px' });
        var historyReplacementString = '/kaart/?city__pk=' + cityId + '&lat=' + window.map.getCenter().lat() + '&lng=' + window.map.getCenter().lng();
        if (currentlySelectedMarkerId) {
            historyReplacementString += '&selectedPhoto=' + currentlySelectedMarkerId;
        }
        historyReplacementString += '&zoom=' + window.map.zoom;
        History.replaceState(null, null, historyReplacementString);
        $('.filter-box').show();
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

    window.showScoreboard = function () {
        $('.top .score_container .scoreboard li').not('.you').add('h2').slideDown();
        $('.top .score_container #facebook-connect').slideDown();
        $('.top .score_container #google-plus-connect').slideDown();
    };

    window.hideScoreboard = function () {
        $('.top .score_container .scoreboard li').not('.you').add('h2').slideUp();
        $('.top .score_container #facebook-connect').slideUp();
        $('.top .score_container #google-plus-connect').slideUp();
    };

    toggleVisiblePaneElements = function () {
        if (window.map) {
            if (cityId) {
                var historyReplacementString = '/kaart/?city__pk=' + cityId + '&lat=' + window.map.getCenter().lat() + '&lng=' + window.map.getCenter().lng();
                if (currentlySelectedMarkerId) {
                    historyReplacementString += '&selectedPhoto=' + currentlySelectedMarkerId;
                }
                historyReplacementString += '&zoom=' + window.map.zoom;
                History.replaceState(null, null, historyReplacementString);
            }
            for (i = 0; i < markers.length; i += 1) {
                if (window.map.getBounds().contains(markers[i].getPosition())) {
//                    if (detachedPhotos[markers[i].id]) {
//                        photoPane.append(detachedPhotos[markers[i].id]);
//                        delete detachedPhotos[markers[i].id];
//                    }
                    $("#element" + markers[i].id).css("visiblity", "visible");
                } else {
//                    if (!detachedPhotos[markers[i].id]) {
//                        detachedPhotos[markers[i].id] = $('#element' + markers[i].id).detach();
//                    }
                    console.log("#element" + i);
                    $("#element" + markers[i].id).css("visiblity", "hidden");
                }
            }
            photoPane.justifiedGallery();
            photoPaneContainer.trigger('scroll');
        }
    };

    calculateLineEndPoint = function (azimuth, startPoint) {
        azimuth = Math.radians(azimuth);
        var newX = Math.cos(azimuth) * lineLength + startPoint.lat(),
            newY = Math.sin(azimuth) * lineLength + startPoint.lng();
        return new google.maps.LatLng(newX, newY);
    };

    window.highlightSelected = function (markerId, fromMarker) {
        currentlySelectedMarkerId = markerId;
        if (cityId) {
            var historyReplacementString = '/kaart/?city__pk=' + cityId + '&lat=' + window.map.getCenter().lat() + '&lng=' + window.map.getCenter().lng();
            if (currentlySelectedMarkerId) {
                historyReplacementString += '&selectedPhoto=' + currentlySelectedMarkerId;
            }
            historyReplacementString += '&zoom=' + window.map.zoom;
            History.replaceState(null, null, historyReplacementString);
        }
        targetPaneElement = $('#element' + markerId);
        lastSelectedMarkerId = markerId;
        userAlreadySeenPhotoIds[markerId] = 1;
        if (fromMarker && targetPaneElement) {
            photoPaneContainer.scrollTop(targetPaneElement.position().top);
            _gaq.push(['_trackEvent', 'Map', 'Marker click']);
        }
        if (!fromMarker) {
            _gaq.push(['_trackEvent', 'Map', 'Pane photo click']);
        }
        if (currentlySelectedMarkerId == lastSelectedMarkerId) {
            return true;
        }
        if (lastSelectedPaneElement) {
            lastSelectedPaneElement.find('.ajapaik-azimuth').hide();
            lastSelectedPaneElement.find('.ajapaik-eye-open').hide();
            lastSelectedPaneElement.find('.ajapaik-rephoto-count').hide();
        }
        $.post('/log_user_map_action/', {user_action: 'saw_marker', photo_id: markerId}, function () {});
        lastSelectedMarkerId = markerId;
        lastSelectedPaneElement = targetPaneElement;
        markerTemp = undefined;
        for (i = 0; i < markers.length; i += 1) {
            if (markers[i].id == markerId) {
                targetPaneElement.find('img').attr('src', markers[i].thumb);
                targetPaneElement.find('.ajapaik-azimuth').show();
                targetPaneElement.find('.ajapaik-eye-open').show();
                targetPaneElement.find('.ajapaik-rephoto-count').show();
                if (!targetPaneElement.find('.ajapaik-eye-open').hasClass('ajapaik-eye-open-light-bg')) {
                    targetPaneElement.find('.ajapaik-eye-open').addClass('ajapaik-eye-open-light-bg');
                }
                markers[i].setZIndex(maxIndex);
                maxIndex += 1;
                markerTemp = markers[i];
                if (markers[i].azimuth) {
                    line.setPath([markers[i].position, calculateLineEndPoint(markers[i].azimuth, markers[i].position)]);
                    line.setMap(window.map);
                    line.setVisible(true);
                } else {
                    line.setVisible(false);
                }
                break;
            }
        }
        if (markerTemp) {
            lastHighlightedMarker = markerTemp;
            markerTemp = undefined;
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

    fireIfLastEvent = function () {
        if (lastEvent.getTime() + mapRefreshInterval <= new Date().getTime()) {
            toggleVisiblePaneElements();
        }
    };

    scheduleDelayedCallback = function () {
        lastEvent = new Date();
        setTimeout(fireIfLastEvent, mapRefreshInterval);
    };

    //TODO: There has to be a better way
    window.paneImageHoverIn = function (e) {
        var myParent = $(e).parent();
        myParent.find('.ajapaik-eye-open').show();
        myParent.find('.ajapaik-azimuth').show();
        myParent.find('.ajapaik-rephoto-count').show();
    };

    window.paneImageHoverOut = function (e) {
        if (e.dataset.id != currentlySelectedMarkerId) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-eye-open').hide();
            myParent.find('.ajapaik-azimuth').hide();
            myParent.find('.ajapaik-rephoto-count').hide();
        }
    };

    window.paneEyeHoverIn = function (e) {
        var myParent = $(e).parent();
        myParent.find('.ajapaik-eye-open').show();
        myParent.find('.ajapaik-azimuth').show();
        myParent.find('.ajapaik-rephoto-count').show();
        return false;
    };

    window.paneEyeHoverOut = function (e) {
        if (e.dataset.id != currentlySelectedMarkerId) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-eye-open').hide();
            myParent.find('.ajapaik-azimuth').hide();
            myParent.find('.ajapaik-rephoto-count').hide();
        }
        return false;
    };

    window.paneAzimuthHoverIn = function (e) {
        var myParent = $(e).parent();
        myParent.find('.ajapaik-eye-open').show();
        myParent.find('.ajapaik-azimuth').show();
        myParent.find('.ajapaik-rephoto-count').show();
        return false;
    };

    window.paneAzimuthHoverOut = function (e) {
        if (e.dataset.id != currentlySelectedMarkerId) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-eye-open').hide();
            myParent.find('.ajapaik-azimuth').hide();
            myParent.find('.ajapaik-rephoto-count').hide();
        }
        return false;
    };

    window.paneRephotoCountHoverIn = function (e) {
        var myParent = $(e).parent();
        myParent.find('.ajapaik-eye-open').show();
        myParent.find('.ajapaik-azimuth').show();
        myParent.find('.ajapaik-rephoto-count').show();
        return false;
    };

    window.paneRephotoCountHoverOut = function (e) {
        if (e.dataset.id != currentlySelectedMarkerId) {
            var myParent = $(e).parent();
            myParent.find('.ajapaik-eye-open').hide();
            myParent.find('.ajapaik-azimuth').hide();
            myParent.find('.ajapaik-rephoto-count').hide();
        }
        return false;
    };

    setCorrectMarkerIcon = function (marker) {
        if (window.map.zoom < 16) {
            if (marker.icon.indexOf('ajapaik-dot') > -1) {
                return;
            }
            if (marker.rephotoCount) {
                marker.setIcon(blueSvgIconUrl);
            } else {
                marker.setIcon(blackSvgIconUrl);
            }
        } else {
            if (marker.icon.indexOf('ajapaik_marker') > -1) {
                return;
            }
            if (marker.rephotoCount) {
                if (marker.id == currentlySelectedMarkerId) {
                    marker.setIcon(blueMarkerIcon35);
                } else {
                    marker.setIcon(blueMarkerIcon20);
                }
            } else {
                if (marker.id == currentlySelectedMarkerId) {
                    marker.setIcon(blackMarkerIcon35);
                } else {
                    marker.setIcon(blackMarkerIcon20);
                }
            }
        }
    };

    $(document).ready(function () {
        $('.top .score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

        $('#open-photo-drawer').click(function (e) {
            e.preventDefault();
            openPhotoDrawer();
        });

        if (window.getQueryParameterByName('lat') && window.getQueryParameterByName('lng') && window.getQueryParameterByName('zoom') && !window.fromSelect && !window.barePhotoview) {
            window.map.setCenter(new google.maps.LatLng(window.getQueryParameterByName('lat'), window.getQueryParameterByName('lng')));
            window.map.setZoom(parseInt(window.getQueryParameterByName('zoom'), 10));
        }

        if (window.getQueryParameterByName('selectedPhoto') && !window.fromSelect && !window.barePhotoview) {
            setTimeout(function () {
                window.highlightSelected(window.getQueryParameterByName('selectedPhoto'), true);
            }, 1000);
        }

        if (typeof markers !== 'undefined') {
            photoPane.justifiedGallery(justifiedGallerySettings);
        }

        setTimeout(function () {
            photoPaneContainer.trigger('scroll');
        }, 1000);

        if (window.map !== undefined) {
            google.maps.event.addListener(window.map, 'bounds_changed', scheduleDelayedCallback);
            //google.maps.event.addListener(window.map, 'zoom_changed', setCorrectMarkerIcons);
        }

        $('#google-plus-login-button').click(function () {
            _gaq.push(['_trackEvent', 'Map', 'Google+ login']);
        });

        $('#logout-button').click(function () {
            _gaq.push(['_trackEvent', 'Map', 'Logout']);
        });

        photoDrawerElement.delegate('#close-photo-drawer', 'click', function (e) {
            e.preventDefault();
            closePhotoDrawer();
        });

        photoDrawerElement.delegate('#random-photo', 'click', function (e) {
            e.preventDefault();
            window.loadPhoto(geotaggedPhotos[Math.floor(Math.random() * geotaggedPhotos.length)][0]);
        });

        photoDrawerElement.delegate('ul.thumbs li.photo a', 'click', function (e) {
            e.preventDefault();
            var rephotoContentElement = $('#rephoto_content'),
                fullLargeElement = $('#full-large2'),
                that = $(this);
            $('ul.thumbs li.photo').removeClass('current');
            that.parent().addClass('current');
            rephotoContentElement.find('a').attr('href', rephotoImgHref[that.attr('rel')]);
            rephotoContentElement.find('a').attr('rel', that.attr('rel'));
            rephotoContentElement.find('img').attr('src', rephotoImgSrc[that.attr('rel')]);
            fullLargeElement.find('img').attr('src', rephotoImgSrcFs[that.attr('rel')]);
            $('#meta_content').html(rephotoMeta[that.attr('rel')]);
            $('#add-comment').html(rephotoComment[that.attr('rel')]);
            if (typeof FB !== 'undefined') {
                FB.XFBML.parse();
            }
            History.replaceState(null, window.document.title, that.attr('href'));
            _gaq.push(['_trackPageview', that.attr('href')]);
        });

        photoDrawerElement.delegate('a.add-rephoto', 'click', function (e) {
            e.preventDefault();
            $('#notice').modal();
            _gaq.push(['_trackEvent', 'Map', 'Add rephoto']);
        });

        $('.single .original').hoverIntent(function () {
            $('.original .tools').addClass('hovered');
        }, function () {
            $('.original .tools').removeClass('hovered');
        });
        $('.single .rephoto .container').hoverIntent(function () {
            $('.rephoto .container .meta').addClass('hovered');
        }, function () {
            $('.rephoto .container .meta ').removeClass('hovered');
        });

        if (window.map !== undefined) {
            window.map.scrollwheel = true;
        }

        $('a.iframe').fancybox({

        });

        $('.full-box div').live('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.exit();
            }
        });

        $('#full-thumb1').live('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.request($('#full-large1')[0]);
                _gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'historic-' + this.rel]);
            }
        });

        $('#full-thumb2').live('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.request($('#full-large2')[0]);
                _gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'rephoto-' + this.rel]);
            }
        });

        $('#full_leaderboard').live('click', function (e) {
            e.preventDefault();
            $('#leaderboard_browser').find('.scoreboard').load(leaderboardFullURL, function () {
                $('#leaderboard_browser').modal({overlayClose: true});
            });
            _gaq.push(['_trackEvent', 'Map', 'Full leaderboard']);
        });
    });
}());