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
        photoPanel,
        currentPanelWidth,
        lastPanelWidth,
        recurringCheckPanelSize,
        i = 0,
        maxIndex = 2,
        lastHighlightedMarker,
        lastSelectedPaneElement,
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
        openPhotoDrawer,
        closePhotoDrawer,
        toggleVisiblePaneElements,
        setCorrectMarkerIcon,
        blueSvgIconUrl = '/static/images/ajapaik-dot-blue.svg',
        blackSvgIconUrl = '/static/images/ajapaik-dot-black.svg',
        blackMarkerIcon20 = '/static/images/ajapaik_marker_20px.png',
        blackMarkerIcon35 = '/static/images/ajapaik_marker_35px.png',
        blueMarkerIcon20 = '/static/images/ajapaik_marker_20px_blue.png',
        blueMarkerIcon35 = '/static/images/ajapaik_marker_35px_blue.png';


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
            }
        });
    };

    openPhotoDrawer = function (content) {
        photoDrawerElement.html(content);
        photoDrawerElement.animate({ top: '0' });
    };

    window.closePhotoDrawer = function () {
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
            var currentBounds = window.map.getBounds(),
                markerIdsWithinBounds = [];
            for (i = 0; i < markers.length; i += 1) {
                if (currentBounds.contains(markers[i].getPosition())) {
                    markerIdsWithinBounds.push(markers[i].id);
                }
                setCorrectMarkerIcon(markers[i]);
            }
            if (window.map.zoom > 15) {
                $.post('/pane_contents/', { marker_ids: markerIdsWithinBounds}, function (response) {
                    if (photoPanel) {
                        photoPanel.content.html(response);
                        photoPanel.find('.panel-body').justifiedGallery(justifiedGallerySettings);
                    } else {
                        photoPanel = $('#ajapaik-mapview-map-container').jsPanel({
                            content: response,
                            controls: {buttons: false},
                            title: false,
                            header: false,
                            draggable: {handle: '.jsPanel-content'},
                            overflow: { horizontal: 'hidden', vertical: 'auto' },
                            id: 'ajapaik-mapview-photo-panel'
                        });
                        photoPanel.find('.panel-body').justifiedGallery(justifiedGallerySettings);
                    }
                    if (!recurringCheckPanelSize) {
                        recurringCheckPanelSize = setInterval(function () {
                            currentPanelWidth = $('#ajapaik-mapview-photo-panel').width();
                            if (currentPanelWidth !== lastPanelWidth) {
                                photoPanel.find('.panel-body').justifiedGallery();
                            }
                            lastPanelWidth = currentPanelWidth;
                        }, 500);
                    }
                });
            }
//            for (i = 0; i < markers.length; i += 1) {
//                if (window.map.getBounds().contains(markers[i].getPosition())) {
//                    if (detachedPhotos[markers[i].id]) {
//                        photoPane.append(detachedPhotos[markers[i].id]);
//                        delete detachedPhotos[markers[i].id];
//                    }
//                } else {
//                    if (!detachedPhotos[markers[i].id]) {
//                        detachedPhotos[markers[i].id] = $('#element' + markers[i].id).detach();
//                    }
//                }
//                setCorrectMarkerIcon(markers[i]);
//            }
//            photoPane.justifiedGallery();
//            photoPaneContainer.trigger('scroll');
        }
    };

    /*    $(document).on('jspanelstatechange', '#ajapaik-mapview-photo-panel', function () {
     console.log('asd');
     photoPanel.justifiedGallery(justifiedGallerySettings);
     });*/

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
        userAlreadySeenPhotoIds[markerId] = 1;
        if (fromMarker && targetPaneElement) {
            var targetPos = targetPaneElement.position(),
                targetTop;
            if (targetPos) {
                targetTop = targetPos.top;
                console.log(targetTop);
                $('#ajapaik-mapview-photo-panel').find('.jsPanel-content').scrollTop(targetTop);
            }
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
        if (lastSelectedMarkerId) {
            setCorrectMarkerIcon(lastHighlightedMarker);
        }
        $.post('/log_user_map_action/', {user_action: 'saw_marker', photo_id: markerId}, function () {
        });
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
                    window.dottedAzimuthLine.setPath([markers[i].position, Math.calculateMapLineEndPoint(markers[i].azimuth, markers[i].position, lineLength)]);
                    window.dottedAzimuthLine.setMap(window.map);
                    window.dottedAzimuthLine.setVisible(true);
                } else {
                    window.dottedAzimuthLine.setVisible(false);
                }
                setCorrectMarkerIcon(markers[i]);
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

    setCorrectMarkerIcon = function (marker) {
        if (window.map.zoom < 16 && marker.id !== currentlySelectedMarkerId) {
            if (marker.rephotoCount) {
                marker.setIcon(blueSvgIconUrl);
            } else {
                marker.setIcon(blackSvgIconUrl);
            }
        } else {
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
        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

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

        if (window.map !== undefined) {
            google.maps.event.addListener(window.map, 'idle', toggleVisiblePaneElements);
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

        $('.full-box div').on('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.exit();
            }
        });

        $('#full-thumb1').on('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.request($('#full-large1')[0]);
                _gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'historic-' + this.rel]);
            }
        });

        $('#full-thumb2').on('click', function (e) {
            if (BigScreen.enabled) {
                e.preventDefault();
                BigScreen.request($('#full-large2')[0]);
                _gaq.push(['_trackEvent', 'Photo', 'Full-screen', 'rephoto-' + this.rel]);
            }
        });

        $('#full_leaderboard').on('click', function (e) {
            e.preventDefault();
            $('#leaderboard_browser').find('.scoreboard').load(leaderboardFullURL, function () {
                $('#leaderboard_browser').modal({overlayClose: true});
            });
            _gaq.push(['_trackEvent', 'Map', 'Full leaderboard']);
        });

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
    });
}());