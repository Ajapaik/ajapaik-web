(function ($) {
    'use strict';

    var photoId,
        currentMapBounds,
        ne,
        sw,
        p,
        photoPanel,
        icon,
        lastRequestedPaneMarkersIds,
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
        currentPaneDataRequest,
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
        blueMarkerIcon35 = '/static/images/ajapaik_marker_35px_blue.png',
        realMapElement,
        ffWheelListener,
        nonFFWheelListener;

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
                if (window.FB !== undefined) {
                    window.FB.XFBML.parse();
                }
            }
        });
    };

    openPhotoDrawer = function (content) {
        $('#ajapaik-photo-modal').html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
            $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
            window.prepareFullscreen();
        });
    };

    window.startGuessLocation = function () {
        if (!guessLocationStarted) {
            window.marker = new window.google.maps.Marker({
                map: window.map,
                draggable: false,
                position: window.map.getCenter(),
                visible: false
            });
            window.map.set('scrollwheel', false);
            nonFFWheelListener = realMapElement.addEventListener('mousewheel', window.wheelEventNonFF, true);
            ffWheelListener = realMapElement.addEventListener('DOMMouseScroll', window.wheelEventFF, true);
            window.marker.bindTo('position', window.map, 'center');
            $('<div/>').addClass('center-marker').appendTo(window.map.getDiv()).click(function () {
                var that = $(this);
                if (!that.data('win')) {
                    that.data('win').bindTo('position', window.map, 'center');
                }
                that.data('win').open(window.map);
            });
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
            window.google.maps.event.addListener(window.map, 'drag', function () {
                window.firstDragDone = true;
            });
            window.google.maps.event.addListener(window.marker, 'position_changed', function () {
                disableSave = false;
            });
            $('#ajapaik-photo-modal').modal('toggle');
            photoPanel.close();
            $('#ajapaik-mapview-map-info-panel').show();
            $('#ajapaik-map-button-container').show();
            mc.clearMarkers();
            $.ajax({
                url: '/heatmap_data/',
                data: {photo_id: photoId},
                cache: false,
                success: function (response) {
                    console.log(response);
                }
            });
            guessLocationStarted = true;
        }
    };

    window.stopGuessLocation = function () {
        window.marker.setMap(null);
        window.map.set('scrollwheel', true);
        window.google.maps.event.removeListener(nonFFWheelListener);
        window.google.maps.event.removeListener(ffWheelListener);
        window.centerMarker.hide();
        window.google.maps.event.clearListeners(window.map, 'mousemove');
        window.google.maps.event.clearListeners(window.map, 'click');
        window.google.maps.event.clearListeners(window.map, 'dragstart');
        window.google.maps.event.clearListeners(window.map, 'idle');
        window.google.maps.event.clearListeners(window.map, 'drag');
        window.google.maps.event.clearListeners(window.map, 'position_changed');
        $('#ajapaik-photo-modal').modal('toggle');
        $('#ajapaik-mapview-map-info-panel').hide();
        $('#ajapaik-map-button-container').hide();
        window.setCursorAuto();
        window.dottedAzimuthLine.setMap(null);
        guessLocationStarted = false;
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
        if (window.map && !guessLocationStarted) {
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
                    if (!lastRequestedPaneMarkersIds || lastRequestedPaneMarkersIds.sort().join(',') !== markerIdsWithinBounds.sort().join(',')) {
                        if (currentPaneDataRequest) {
                            currentPaneDataRequest.abort();
                        }
                        currentPaneDataRequest = $.post('/pane_contents/', { marker_ids: markerIdsWithinBounds}, function (response) {
                            if (photoPanel) {
                                photoPanel.content.html(response);
                                photoPanel.find('.panel-body').justifiedGallery(justifiedGallerySettings);
                            } else {
                                photoPanel = $('#ajapaik-map-container').jsPanel({
                                    content: response,
                                    controls: {buttons: false},
                                    title: false,
                                    position: {top: 35, left: 35},
                                    size: { height: function () {
                                        return $(window).height() / 1.5;
                                    }},
                                    draggable: {
                                        handle: '.jsPanel-header',
                                        containment: '#ajapaik-map-container'
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
                            currentPaneDataRequest = undefined;
                            lastRequestedPaneMarkersIds = markerIdsWithinBounds;
                        });
                    }
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
        realMapElement = $('#ajapaik-map-canvas')[0];
        if (window.getQueryParameterByName('fromSelect') && window.cityId) {
            window.fromSelect = true;
            window.History.replaceState(null, null, '/kaart/?city=' + window.cityId);
        } else {
            window.fromSelect = false;
        }

        if (window.cityLatLng) {
            window.getMap(window.cityLatLng, 13, false);
        } else {
            window.getMap(null, 13, false);
        }

        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);

        window.saveLocationButton = $('.ajapaik-save-location-button');

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
            window.google.maps.event.addListener(window.map, 'idle', toggleVisiblePaneElements);
        }

        $('#google-plus-login-button').click(function () {
            _gaq.push(['_trackEvent', 'Map', 'Google+ login']);
        });

        $('#logout-button').click(function () {
            _gaq.push(['_trackEvent', 'Map', 'Logout']);
        });

        $('.ajapaik-mapview-skip-photo-button').click(function () {
            window.stopGuessLocation();
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

        $(document).on('mouseover', '#ajapaik-photo-modal', function () {
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').show();
            }
        });

        $(document).on('mouseout', '#ajapaik-photo-modal', function () {
            if (!isMobile) {
                $('.ajapaik-flip-photo-overlay-button').hide();
            }
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
}(jQuery));