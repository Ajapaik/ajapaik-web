(function () {
    "use strict";
    /*jslint nomen: true */
    /*global FB */
    /*global geotaggedPhotos */
    /*global _gaq */
    /*global markers */
    /*global cityId */
    /*global google */
    /*global userAlreadySeenPhotoIds */

    var photoId,
        photoDrawerElement = $('#photo-drawer'),
        photoPaneContainer = $("#photo-pane-container"),
        photoPane = $("#photo-pane"),
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
            maxRowHeight: 150,
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
        lazyloadSettings = {
            container: photoPaneContainer,
            effect: "fadeIn",
            threshold: 50
        },
        lastEvent,
        mapRefreshInterval = 500;

    Math.radians = function(degrees) {
        return degrees * Math.PI / 180;
    };

    window.loadPhoto = function(id) {
        $.post("/log_user_map_action/", {user_action: "opened_drawer", photo_id: id}, function () {});
        photoId = id;
        $.ajax({
            cache: false,
            url: '/foto/' + id + '/',
            success: function (result) {
                openPhotoDrawer(result);
                if (typeof FB != 'undefined') {
                    FB.XFBML.parse();
                }
                $("a.iframe").fancybox({
                    'width': '75%',
                    'height': '75%',
                    'autoScale': false,
                    'hideOnContentClick': false
                });
            }
        });
    };

    function openPhotoDrawer(content) {
        photoDrawerElement.html(content);
        photoDrawerElement.animate({ top: '7%' });
    }

    function closePhotoDrawer() {
        photoDrawerElement.animate({ top: '-1000px' });
        var historyReplacementString = "/kaart/?city__pk=" + cityId + "&lat=" + window.map.getCenter().lat() + "&lng=" + window.map.getCenter().lng();
        if (currentlySelectedMarkerId) {
            historyReplacementString += "&selectedPhoto=" + currentlySelectedMarkerId;
        }
        historyReplacementString += "&zoom=" + window.map.zoom;
        History.replaceState(null, null, historyReplacementString);
        $('.filter-box').show();
    }

    window.uploadCompleted = function(response) {
        $.modal.close();
        if (typeof photoId == 'undefined') {
            if (response && typeof response.new_id !== 'undefined' && response.new_id) {
                window.location.href = '/foto/' + response.new_id + '/';
            } else {
                window.location.reload();
            }
        } else {
            closePhotoDrawer();
            if (response && typeof response.new_id != 'undefined' && response.new_id) {
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

    function toggleVisiblePaneElements() {
        if (window.map) {
            if (cityId) {
                var historyReplacementString = "/kaart/?city__pk=" + cityId + "&lat=" + window.map.getCenter().lat() + "&lng=" + window.map.getCenter().lng();
                if (currentlySelectedMarkerId) {
                    historyReplacementString += "&selectedPhoto=" + currentlySelectedMarkerId;
                }
                historyReplacementString += "&zoom=" + window.map.zoom;
                History.replaceState(null, null, historyReplacementString);
            }
            for (i = 0; i < markers.length; i += 1) {
                if (window.map.getBounds().contains(markers[i].getPosition())) {
                    if (detachedPhotos[markers[i].id]) {
                        photoPane.append(detachedPhotos[markers[i].id]);
                        delete detachedPhotos[markers[i].id];
                    }
                } else {
                    if (!detachedPhotos[markers[i].id]) {
                        detachedPhotos[markers[i].id] = $("#element" + markers[i].id).detach();
                    }
                }
            }
            photoPane.justifiedGallery();
            photoPaneContainer.trigger("scroll");
        }
    }

    function calculateLineEndPoint(azimuth, startPoint) {
        azimuth = Math.radians(azimuth);
        var newX = Math.cos(azimuth) * lineLength + startPoint.lat();
        var newY = Math.sin(azimuth) * lineLength + startPoint.lng();
        return new google.maps.LatLng(newX, newY);
    }

    function setIcon(marker, color, size) {

        if (color) {
            marker.setIcon("/media/gfx/ajapaik_marker_" + size + "px_" + color + ".png")
        } else {
            marker.setIcon("/media/gfx/ajapaik_marker_" + size + "px.png")
        }
    }

    window.highlightSelected = function (markerId, fromMarker) {
        currentlySelectedMarkerId = markerId;
        if (cityId) {
            var historyReplacementString = "/kaart/?city__pk=" + cityId + "&lat=" + window.map.getCenter().lat() + "&lng=" + window.map.getCenter().lng();
            if (currentlySelectedMarkerId) {
                historyReplacementString += "&selectedPhoto=" + currentlySelectedMarkerId;
            }
            historyReplacementString += "&zoom=" + window.map.zoom;
            History.replaceState(null, null, historyReplacementString);
        }
        targetPaneElement = $("#element" + markerId);
        userAlreadySeenPhotoIds[markerId] = 1;
        if (fromMarker && targetPaneElement) {
            photoPaneContainer.scrollTop(targetPaneElement.position().top);
            _gaq.push(["_trackEvent", "Map", "Marker click"]);
        }
        if (!fromMarker) {
            _gaq.push(["_trackEvent", "Map", "Pane photo click"]);
        }
        if (currentlySelectedMarkerId == lastSelectedMarkerId) {
            return true;
        }
        if (lastSelectedPaneElement) {
            lastSelectedPaneElement.find(".ajapaik-azimuth").hide();
            lastSelectedPaneElement.find(".ajapaik-eye-open").hide();
            lastSelectedPaneElement.find(".ajapaik-rephoto-count").hide();
        }
        $.post("/log_user_map_action/", {user_action: "saw_marker", photo_id: markerId}, function () {});
        lastSelectedMarkerId = markerId;
        lastSelectedPaneElement = targetPaneElement;
        markerTemp = undefined;
        for (i = 0; i < markers.length; i += 1) {
            if (lastHighlightedMarker) {
                if (lastHighlightedMarker.rephotoCount) {
                    setIcon(lastHighlightedMarker, "blue", 20);
                } else {
                    setIcon(lastHighlightedMarker, null, 20);
                }
            }
            if (markers[i].id == markerId) {
                targetPaneElement.find("img").attr("src", markers[i].thumb);
                targetPaneElement.find(".ajapaik-azimuth").show();
                targetPaneElement.find(".ajapaik-eye-open").show();
                targetPaneElement.find(".ajapaik-rephoto-count").show();
                if (!targetPaneElement.find(".ajapaik-eye-open").hasClass("ajapaik-eye-open-light-bg")) {
                    targetPaneElement.find(".ajapaik-eye-open").addClass("ajapaik-eye-open-light-bg");
                }
                if (markers[i].rephotoCount) {
                    setIcon(markers[i], "blue", 35);
                } else {
                    setIcon(markers[i], null, 35);
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
        var photoElement = $("a[rel=" + photoId + "]").find("img"),
            photoFullscreenElement = $("#full-large1").find("img");
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

    function fireIfLastEvent() {
        if (lastEvent.getTime() + mapRefreshInterval <= new Date().getTime()) {
            toggleVisiblePaneElements();
        }
    }

    function scheduleDelayedCallback() {
        lastEvent = new Date();
        setTimeout(fireIfLastEvent, mapRefreshInterval);
    }

    //TODO: There has to be a better way
    function paneImageHoverIn() {
        $(this).parent().find(".ajapaik-eye-open").show();
        $(this).parent().find(".ajapaik-azimuth").show();
        $(this).parent().find(".ajapaik-rephoto-count").show();
    }

    function paneImageHoverOut() {
        if (this.dataset.id != currentlySelectedMarkerId) {
            $(this).parent().find(".ajapaik-eye-open").hide();
            $(this).parent().find(".ajapaik-azimuth").hide();
            $(this).parent().find(".ajapaik-rephoto-count").hide();
        }
    }

    function paneEyeHoverIn() {
        $(this).parent().find(".ajapaik-eye-open").show();
        $(this).parent().find(".ajapaik-azimuth").show();
        $(this).parent().find(".ajapaik-rephoto-count").show();
        return false;
    }

    function paneEyeHoverOut() {
        if (this.dataset.id != currentlySelectedMarkerId) {
            $(this).parent().find(".ajapaik-eye-open").hide();
            $(this).parent().find(".ajapaik-azimuth").hide();
            $(this).parent().find(".ajapaik-rephoto-count").hide();
        }
        return false;
    }

    function paneAzimuthHoverIn() {
        $(this).parent().find(".ajapaik-eye-open").show();
        $(this).parent().find(".ajapaik-azimuth").show();
        $(this).parent().find(".ajapaik-rephoto-count").show();
        return false;
    }

    function paneAzimuthHoverOut() {
        if (this.dataset.id != currentlySelectedMarkerId) {
            $(this).parent().find(".ajapaik-eye-open").hide();
            $(this).parent().find(".ajapaik-azimuth").hide();
            $(this).parent().find(".ajapaik-rephoto-count").hide();
        }
        return false;
    }

    function paneRephotoCountHoverIn() {
        $(this).parent().find(".ajapaik-eye-open").show();
        $(this).parent().find(".ajapaik-azimuth").show();
        $(this).parent().find(".ajapaik-rephoto-count").show();
        return false;
    }

    function paneRephotoCountHoverOut() {
        if (this.dataset.id != currentlySelectedMarkerId) {
            $(this).parent().find(".ajapaik-eye-open").hide();
            $(this).parent().find(".ajapaik-azimuth").hide();
            $(this).parent().find(".ajapaik-rephoto-count").hide();
        }
        return false;
    }

    $(document).ready(function () {
        $('.top .score_container').hoverIntent(showScoreboard, hideScoreboard);

        $('#open-photo-drawer').click(function (e) {
            e.preventDefault();
            openPhotoDrawer();
        });

        var QueryString = function () {
            var queryString = {};
            var query = window.location.search.substring(1);
            var vars = query.split("&");
            for (var i = 0; i < vars.length; i++) {
                var pair = vars[i].split("=");
                if (typeof queryString[pair[0]] === "undefined") {
                    queryString[pair[0]] = pair[1];
                } else if (typeof queryString[pair[0]] === "string") {
                    queryString[pair[0]] = [ queryString[pair[0]], pair[1] ];
                } else {
                    queryString[pair[0]].push(pair[1]);
                }
            }
            return queryString;
        }();

        if (QueryString.lat && QueryString.lng && QueryString.zoom) {
            window.map.setCenter(new google.maps.LatLng(QueryString.lat, QueryString.lng));
            window.map.setZoom(parseInt(QueryString.zoom));
        }

        if (QueryString.selectedPhoto) {
            setTimeout(function () {
                window.highlightSelected(QueryString.selectedPhoto, true);
            }, 1000);
        }

        if (typeof(markers) !== "undefined") {
            for (i = 0; i < markers.length; i += 1) {
                var newAElement = document.createElement("a");
                $(newAElement).click(function (e) {
                    e.preventDefault();
                    window.highlightSelected(e.target.dataset.id, false);
                }).attr("id", "element" + markers[i].id).attr("data-id", markers[i].id);
                var newImgElement = document.createElement("img");
                $(newImgElement).attr("src", "").attr("data-src", markers[i].thumb).attr("title", markers[i].description)
                    .attr("data-id", markers[i].id).addClass("lazyload").hover(paneImageHoverIn, paneImageHoverOut)
                    .attr("height", markers[i].thumbHeight).attr("width", markers[i].thumbWidth);
                $(newAElement).attr("src", markers[i].thumb);
                var newEyeElement = document.createElement("div");
                $(newEyeElement).addClass("ajapaik-eye-open").click(function (e) {
                    _gaq.push(["_trackEvent", "Map", "Pane photo eye click"]);
                    window.loadPhoto(e.target.dataset.id);
                }).attr("data-id", markers[i].id).attr("id", "eye" + markers[i].id).hide()
                    .hover(paneEyeHoverIn, paneEyeHoverOut);
                if (markers[i].id in userAlreadySeenPhotoIds) {
                    $(newEyeElement).addClass("ajapaik-eye-open-light-bg")
                }
                var newAzimuthElement = undefined;
                if (markers[i].azimuth) {
                    newAzimuthElement = document.createElement("div");
                    $(newAzimuthElement).addClass("ajapaik-azimuth").hover(paneAzimuthHoverIn, paneAzimuthHoverOut).hide().attr("data-id", markers[i].id);
                }
                var newRephotoCountElement = undefined;
                if (markers[i].rephotoCount > 0) {
                    newRephotoCountElement = document.createElement("div");
                    $(newRephotoCountElement).addClass("ajapaik-rephoto-count")
                        .hover(paneRephotoCountHoverIn, paneRephotoCountHoverOut).hide().html(markers[i].rephotoCount).attr("data-id", markers[i].id);
                }
                newAElement.appendChild(newImgElement);
                newAElement.appendChild(newEyeElement);
                if (newAzimuthElement) {
                    newAElement.appendChild(newAzimuthElement);
                }
                if (newRephotoCountElement) {
                    newAElement.appendChild(newRephotoCountElement);
                }
                photoPane.append(newAElement);
            }
        }

//        $(function () {
//            var lazyImages = $("img.lazy");
//            if (lazyImages.length > 0) {
//                lazyImages.lazyload(lazyloadSettings);
//            }
//        });

        if (typeof(markers) !== "undefined") {
            photoPane.justifiedGallery(justifiedGallerySettings);
        }

        setTimeout(function () {
            photoPaneContainer.trigger("scroll");
        }, 1000);

        if (typeof(window.map) !== "undefined") {
            google.maps.event.addListener(window.map, 'bounds_changed', scheduleDelayedCallback);
        }

        $('#google-plus-login-button').click(function () {
            _gaq.push(["_trackEvent", "Map", "Google+ login"]);
        });

        $('#logout-button').click(function () {
            _gaq.push(["_trackEvent", "Map", "Logout"]);
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

        $("a.iframe").fancybox({
            'width': '75%',
            'height': '75%',
            'autoScale': false,
            'hideOnContentClick': false
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