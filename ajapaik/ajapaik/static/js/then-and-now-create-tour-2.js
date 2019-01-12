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
    /* global icon3 */
    /* global isMobile */
    /* global tourType */
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
                zoom: 15,
                minZoom: 7,
                mapTypeControl: false,
                streetViewControl: false
            }),
            userMarker = new google.maps.Marker({
                clickable: false,
                icon: icon3,
                shadow: null,
                zIndex: 999,
                map: map
            }),
            searchInput = document.getElementById('tan-pac-input'),
            searchBox = new google.maps.places.SearchBox(searchInput),
            myLocationButton = document.getElementById('tan-my-location-button'),
            lastClickedMarkerIdForMobile,
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
                        if (response.count > 250) {
                            $('#tan-create-tour-2-total-marker-count').html(response.count);
                            $('#tan-create-tour-2-zoom-in-notice').html(', ' + gettext('zoom in more to view markers.')).show();
                        } else {
                            $('#tan-create-tour-2-total-marker-count').html(response.count);
                            $('#tan-create-tour-2-zoom-in-notice').hide();
                            var markers = [];
                            if (response.photos) {
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
                                    if (!isMobile) {
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
                                        // Fixed photo set
                                        if (tourType === '0') {
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
                                        }
                                    } else {
                                        google.maps.event.addListener(marker, 'click', (function (marker) {
                                            return function () {
                                                if (tourType === '0' && lastClickedMarkerIdForMobile === marker.id) {
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
                                                } else {
                                                    infoWindow.setContent('<img class="img-responsive" src="' + v.imageURL + '">' + v.description);
                                                    infoWindow.open(map, marker);
                                                    infoWindowClosed = false;
                                                }
                                                lastClickedMarkerIdForMobile = marker.id;
                                            };
                                        })(marker));
                                    }
                                });
                            }
                            mc = new MarkerClusterer(map, markers, markerClustererSettings);
                        }
                    }
                });
            },
            mapCenter,
            hiddenLatInput = $('#tan-create-tour-2-lat'),
            hiddenLngInput = $('#tan-create-tour-2-lng'),
            geolocationCallback = function (location) {
                var lat = location.coords.latitude,
                    lng = location.coords.longitude,
                    gLatLng = new google.maps.LatLng(lat, lng);
                map.setCenter(gLatLng);
                userMarker.setPosition(gLatLng);
            },
            geolocationError = function () {
                console.log(gettext('Unable to get location data'));
            },
            getGeolocation = function getLocation(callback) {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(callback, geolocationError);
                }
            };
        // Try to center on user
        getGeolocation(geolocationCallback);
        $(searchInput).empty();
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(searchInput);
        map.controls[google.maps.ControlPosition.TOP_RIGHT].push(myLocationButton);
        $('#tan-my-location-button').click(function () {
            getGeolocation(geolocationCallback);
        });
        google.maps.event.addListener(searchBox, 'places_changed', function () {
            var places = searchBox.getPlaces();
            if (places.length === 0) {
                return;
            }
            map.setCenter(places[0].geometry.location);
        });
        google.maps.event.addListener(infoWindow, 'closeclick', function () {
            infoWindowClosed = true;
        });
        google.maps.event.addListener(map, 'dragstart', function () {
            infoWindow.close();
            infoWindowClosed = true;
        });
        map.addListener('center_changed', function () {
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
        map.addListener('zoom_changed', function () {
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