(function () {
    'use strict';
    /*jslint nomen: true */
    /*global FB */
    /*global _gaq */
    /*global cityId */
    /*global google */
    /*global userAlreadySeenPhotoIds */
    /*global $ */
    /*global History */
    /*global BigScreen */
    /*global leaderboardFullURL */
    /*global MarkerClusterer */
    /*global gettext */
    /*global isMobile */

    var photoId,
        currentMapBounds,
        ne,
        sw,
        p,
        photoPanel,
        icon,
        marker,
        radianAngle,
        degreeAngle,
        azimuthLineEndPoint,
        saveDirection = false,
        azimuthListenerActive = true,
        centerMarker,
        mapClickListenerActive = false,
        mapIdleListenerActive = false,
        mapDragstartListenerActive = false,
        mapMousemoveListenerActive = false,
        mapClickListenerFunction,
        mapDragstartListenerFunction,
        mapIdleListenerFunction,
        mapMousemoveListenerFunction,
        firstDragDone = false,
        disableSave = true,
        guessLocationStarted = false,
        currentPanelWidth,
        lastPanelWidth,
        recurringCheckPanelSize,
        i = 0,
        j = 0,
        maxIndex = 2,
        lastHighlightedMarker,
        lastSelectedPaneElement,
        markerIdsWithinBounds,
        lineLength = 0.01,
        lastSelectedMarkerId,
        currentlySelectedMarkerId,
        targetPaneElement,
        markerTemp,
        markers = [],
        mc,
        currentMapDataRequest,
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
        toggleVisiblePaneElements,
        setCorrectMarkerIcon,
        blackMarkerIcon20 = '/static/images/ajapaik_marker_20px.png',
        blackMarkerIcon35 = '/static/images/ajapaik_marker_35px.png',
        blueMarkerIcon20 = '/static/images/ajapaik_marker_20px_blue.png',
        blueMarkerIcon35 = '/static/images/ajapaik_marker_35px_blue.png';


    window.loadPhoto = function (id) {
        // TODO: No double request, this could get logged in /foto/ anyway
        //$.post('/log_user_map_action/', {user_action: 'opened_drawer', photo_id: id}, function () {
        //    $.noop();
        //});
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
        $('#ajapaik-photo-modal').html(content).modal();
    };

    mapClickListenerFunction = function (e) {
        radianAngle = window.getAzimuthBetweenMouseAndMarker(e, marker);
        azimuthLineEndPoint = [e.latLng.lat(), e.latLng.lng()];
        degreeAngle = Math.degrees(radianAngle);
        if (azimuthListenerActive) {
            mapMousemoveListenerActive = false;
            google.maps.event.clearListeners(window.map, 'mousemove');
            saveDirection = true;
            $('.ajapaik-grid-save-location-button').text(gettext('Save location and direction'));
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
        $('.ajapaik-grid-save-location-button').text(gettext('Save location only'));
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

    mapDragstartListenerFunction = function () {
//            if (mobileMapMinimized) {
//                toggleTouchPhotoView();
//            }
        window.dottedAzimuthLine.setVisible(false);
//            centerMarker
//                .css('background-image', 'url("/static/images/ajapaik_marker_35px_cross.png")')
//                .css('margin-left', '-17px')
//                .css('margin-top', '-55px')
//                .css('height', '60px');
        $('.ajapaik-grid-save-location-button').text(gettext('Save location only'));
        azimuthListenerActive = false;
        window.dottedAzimuthLine.setVisible(false);
        mapMousemoveListenerActive = false;
        google.maps.event.clearListeners(window.map, 'mousemove');
    };

    mapIdleListenerFunction = function () {
        if (firstDragDone) {
            marker.position = window.map.center;
            azimuthListenerActive = true;
//                centerMarker
//                    .css('background-image', 'url("http://maps.gstatic.com/intl/en_ALL/mapfiles/drag_cross_67_16.png")')
//                    .css('margin-left', '-8px')
//                    .css('margin-top', '-9px');
            if (!mapMousemoveListenerActive) {
                google.maps.event.addListener(window.map, 'mousemove', mapMousemoveListenerFunction);
                mapMousemoveListenerActive = true;
            }
        }
    };


    window.startGuessLocation = function () {
        if (!guessLocationStarted) {
            marker = new google.maps.Marker({
                map: window.map,
                draggable: false,
                position: window.map.getCenter(),
                visible: false
            });
            marker.bindTo('position', window.map, 'center');
            $('<div/>').addClass('center-marker').appendTo(window.map.getDiv()).click(function () {
                var that = $(this);
                if (!that.data('win')) {
                    that.data('win').bindTo('position', window.map, 'center');
                }
                that.data('win').open(window.map);
            });
            centerMarker = $('.center-marker');
            //$('.ajapaik-mapview-guess-location-button').hide();
            $('.ajapaik-mapview-save-location-button').show();
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
            google.maps.event.addListener(window.map, 'drag', function () {
                firstDragDone = true;
            });
            google.maps.event.addListener(marker, 'position_changed', function () {
                disableSave = false;
            });
            guessLocationStarted = true;
        }
    };

    window.closePhotoDrawer = function () {
        $('#ajapaik-photo-modal').modal('toggle');
        //photoDrawerElement.animate({ top: '-1000px' });
        //var historyReplacementString = '/kaart/?city=' + cityId + '&lat=' + window.map.getCenter().lat() + '&lng=' + window.map.getCenter().lng();
        //if (currentlySelectedMarkerId) {
        //    historyReplacementString += '&selectedPhoto=' + currentlySelectedMarkerId;
        //}
        //historyReplacementString += '&zoom=' + window.map.zoom;
        //History.replaceState(null, null, historyReplacementString);
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

//    var buildPaneElement = function (marker) {
//        var a = document.createElement('a');
//        $(a).addClass('ajapaik-mapview-pane-photo-container').prop('id', 'element' + marker.id)
//            .prop('data-id', 'element' + marker.id).click(function () {
//                window.highlightSelected(marker.id, false);
//            });
//    };

    toggleVisiblePaneElements = function () {
        if (window.map) {
            if (cityId) {
                var historyReplacementString = '/kaart/?city=' + cityId + '&lat=' + window.map.getCenter().lat() + '&lng=' + window.map.getCenter().lng();
                if (currentlySelectedMarkerId) {
                    historyReplacementString += '&selectedPhoto=' + currentlySelectedMarkerId;
                }
                historyReplacementString += '&zoom=' + window.map.zoom;
                History.replaceState(null, null, historyReplacementString);
            }
            currentMapBounds = window.map.getBounds();
            ne = currentMapBounds.getNorthEast();
            sw = currentMapBounds.getSouthWest();
            if (currentMapDataRequest) {
                currentMapDataRequest.abort();
            }
            currentMapDataRequest = $.post('/map_data/', { sw_lat: sw.lat(), sw_lon: sw.lng(), ne_lat: ne.lat(), ne_lon: ne.lng(), zoom: window.map.zoom}, function (response) {
                markers = [];
                for (j = 0; j < response.length; j += 1) {
                    p = response[j];
                    if (p[4]) {
                        icon = blueMarkerIcon20;
                    } else {
                        icon = blackMarkerIcon20;
                    }
                    var marker = new google.maps.Marker({
                        id: p[0],
                        icon: icon,
                        rephotoCount: p[4],
                        position: new google.maps.LatLng(p[3], p[2]),
                        zIndex: 1,
                        azimuth: p[7]
                    });
                    (function (id) {
                        google.maps.event.addListener(marker, 'click', function () {
                            window.highlightSelected(id, true);
                        });
                    })(p[0]);
                    markers.push(marker);
                }
                mc = new MarkerClusterer(window.map, markers, {maxZoom: 15});
                // TODO: Make neat, no extra request
                if (window.map.zoom > 15) {
                    markerIdsWithinBounds = [];
                    for (i = 0; i < markers.length; i += 1) {
                        markerIdsWithinBounds.push(markers[i].id);
                    }
                    $.post('/pane_contents/', { marker_ids: markerIdsWithinBounds}, function (response) {
                        if (photoPanel) {
                            photoPanel.content.html(response);
                            photoPanel.find('.panel-body').justifiedGallery(justifiedGallerySettings);
                        } else {
                            photoPanel = $('#ajapaik-mapview-map-container').jsPanel({
                                content: response,
                                controls: {buttons: false},
                                title: false,
                                position: {top: 35, left: 35},
                                size: { height: function () {
                                    return $(window).height() / 1.5;
                                }},
                                draggable: {
                                    handle: '.jsPanel-header',
                                    containment: '#ajapaik-mapview-map-container'
                                },
                                overflow: { horizontal: 'hidden', vertical: 'auto' },
                                id: 'ajapaik-mapview-photo-panel'
                            });
                            photoPanel.find('.panel-body').justifiedGallery(justifiedGallerySettings);
                        }
                        if (!recurringCheckPanelSize) {
                            recurringCheckPanelSize = setInterval(function () {
                                currentPanelWidth = $('#ajapaik-mapview-photo-panel').width();
                                if (photoPanel && currentPanelWidth !== lastPanelWidth) {
                                    photoPanel.find('.panel-body').justifiedGallery();
                                }
                                lastPanelWidth = currentPanelWidth;
                            }, 500);
                        }
                    });
                } else {
                    if (photoPanel) {
                        photoPanel.close();
                        photoPanel = undefined;
                    }
                }
            });
        }
    };

    window.highlightSelected = function (markerId, fromMarker) {
        currentlySelectedMarkerId = markerId;
        if (cityId) {
            var historyReplacementString = '/kaart/?city=' + cityId + '&lat=' + window.map.getCenter().lat() + '&lng=' + window.map.getCenter().lng();
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
    };

    $(document).ready(function () {
        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

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

        //photoDrawerElement.delegate('ul.thumbs li.photo a', 'click', function (e) {
        //    e.preventDefault();
        //    var rephotoContentElement = $('#rephoto_content'),
        //        fullLargeElement = $('#full-large2'),
        //        that = $(this);
        //    $('ul.thumbs li.photo').removeClass('current');
        //    that.parent().addClass('current');
        //    rephotoContentElement.find('a').attr('href', rephotoImgHref[that.attr('rel')]);
        //    rephotoContentElement.find('a').attr('rel', that.attr('rel'));
        //    rephotoContentElement.find('img').attr('src', rephotoImgSrc[that.attr('rel')]);
        //    fullLargeElement.find('img').attr('src', rephotoImgSrcFs[that.attr('rel')]);
        //    $('#meta_content').html(rephotoMeta[that.attr('rel')]);
        //    $('#add-comment').html(rephotoComment[that.attr('rel')]);
        //    if (typeof FB !== 'undefined') {
        //        FB.XFBML.parse();
        //    }
        //    History.replaceState(null, window.document.title, that.attr('href'));
        //    _gaq.push(['_trackPageview', that.attr('href')]);
        //});

        //photoDrawerElement.delegate('a.add-rephoto', 'click', function (e) {
        //    e.preventDefault();
        //    $('#notice').modal();
        //    _gaq.push(['_trackEvent', 'Map', 'Add rephoto']);
        //});

        //$('.single .original').hoverIntent(function () {
        //    $('.original .tools').addClass('hovered');
        //}, function () {
        //    $('.original .tools').removeClass('hovered');
        //});
        //$('.single .rephoto .container').hoverIntent(function () {
        //    $('.rephoto .container .meta').addClass('hovered');
        //}, function () {
        //    $('.rephoto .container .meta ').removeClass('hovered');
        //});

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

        $('#full_leaderboard').bind('click', function (e) {
            e.preventDefault();
            $.ajax({
                url: leaderboardFullURL,
                success: function (response) {
                    var modalWindow = $('#ajapaik-full-leaderboard-modal');
                    modalWindow.find('.scoreboard').html(response);
                    modalWindow.modal().on('shown.bs.modal', function () {
                        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                    });
                }
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