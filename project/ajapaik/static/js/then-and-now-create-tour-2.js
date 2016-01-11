(function () {
    'use strict';
    /* global google */
    /* global mapMarkersURL */
    /* global selectionToggleURL */
    /* global gettext */
    /* global docCookies */
    /* global MarkerClusterer */
    /* global icon1 */
    /* global icon2 */
    $(document).ready(function () {
        $('#tan-create-tour-2-selection-clear').click(function () {
            $.ajax({
                method: 'POST',
                url: selectionToggleURL,
                data: {
                    clear: true,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success: function (response) {
                    $('#tan-create-tour-2-selection-size').html(Object.keys(response).length);
                    getMapMarkers();
                }
            });
        });
        var map = new google.maps.Map(document.getElementById('tan-create-tour-map'), {
                center: new google.maps.LatLng(59, 26),
                mapTypeControlOptions: {
                    position: google.maps.ControlPosition.BOTTOM_RIGHT
                },
                zoom: 7,
                minZoom: 7
            }),
            infoWindow = new google.maps.InfoWindow(),
            infoWindowClosed = true,
            mc,
            markerClustererSettings = {
                minimumClusterSize: 2,
                maxZoom: 17,
                gridSize: 5
            },
            getMapMarkersTimeout,
            getMapMarkers = function () {
                var mapSW = map.getBounds().getSouthWest(),
                    mapNE = map.getBounds().getNorthEast();
                $.ajax({
                    url: mapMarkersURL,
                    data: {
                        swLat: mapSW.lat(),
                        swLon: mapSW.lng(),
                        neLat: mapNE.lat(),
                        neLon: mapNE.lng()
                    },
                    success: function (response) {
                        if (mc) {
                            mc.clearMarkers();
                        }
                        if (response.count > 500) {
                            $('#tan-create-tour-2-total-marker-count').find('span').html(response.count + ', ' + gettext('zoom in more to view markers.'));
                        } else {
                            $('#tan-create-tour-2-total-marker-count').find('span').html(response.count);
                            var markers = [];
                            $.each(response.photos, function (k, v) {
                                var icon;
                                if (v.inSelection) {
                                    icon = icon1;
                                } else {
                                    icon = icon2;
                                }
                                var marker = new google.maps.Marker({
                                    position: new google.maps.LatLng(v.lat, v.lon),
                                    map: map,
                                    icon: icon,
                                    id: v.id
                                });
                                markers.push(marker);
                                google.maps.event.addListener(marker, 'mouseover', (function (marker, content, infoWindow) {
                                    return function () {
                                        infoWindow.setContent(content);
                                        infoWindow.open(map, marker);
                                        infoWindowClosed = false;
                                    };
                                })(marker, '<img class="img-responsive" src="' + v.imageURL + '">' + v.description, infoWindow));
                                google.maps.event.addListener(marker, 'mouseout', (function (marker, infoWindow) {
                                    return function () {
                                        infoWindow.close();
                                        infoWindowClosed = true;
                                    };
                                })(marker, infoWindow));
                                google.maps.event.addListener(marker, 'click', (function (marker) {
                                    return function () {
                                        $.ajax({
                                            method: 'POST',
                                            url: selectionToggleURL,
                                            data: {
                                                'photo': marker.id,
                                                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                                            },
                                            success: function (response) {
                                                $('#tan-create-tour-2-selection-size').html(Object.keys(response).length);
                                                if (marker.id in response) {
                                                    marker.setIcon(icon1);
                                                } else {
                                                    marker.setIcon(icon2);
                                                }
                                            }
                                        });
                                    };
                                })(marker));
                            });
                            mc = new MarkerClusterer(map, markers, markerClustererSettings);
                        }
                    }
                });
            },
            mapCenter,
            hiddenLatInput = $('#tan-create-tour-2-lat'),
            hiddenLngInput = $('#tan-create-tour-2-lng');
        google.maps.event.addListener(infoWindow, 'closeclick', function () {
            infoWindowClosed = true;
        });
        google.maps.event.addListener(map, 'dragstart', function () {
            infoWindow.close();
            infoWindowClosed = true;
        });
        map.addListener('center_changed', function() {
            mapCenter = map.getCenter();
            hiddenLatInput.val(mapCenter.lat());
            hiddenLngInput.val(mapCenter.lng());
            if (infoWindowClosed) {
                if (getMapMarkersTimeout) {
                    clearTimeout(getMapMarkersTimeout);
                }
                getMapMarkersTimeout = setTimeout(function () {
                    getMapMarkers();
                }, 500);
            }
        });
    });
}());