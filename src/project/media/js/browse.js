(function () {
    "use strict";
    /*jslint nomen: true */
    /*global FB */
    /*global geotaggedPhotos */
    /*global _gaq */
    /*global markers */
    /*global cityId */
    /*global google */

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
            lastRow: 'nojustify',
            margins: 3,
            sizeRangeSuffixes: {
                'lt100':'',
                'lt240':'',
                'lt320':'',
                'lt500':'',
                'lt640':'',
                'lt1024':''
            }
        },
        lazyloadSettings = {
            container: photoPaneContainer,
            effect: "fadeIn",
            threshold: 50
        },
        lastEvent,
        mapRefreshInterval = 1000;

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
        History.replaceState(null, null, "/kaart/?city__pk=" + cityId);
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
        targetPaneElement = $("#element" + markerId);
        if (fromMarker) {
            photoPaneContainer.scrollTop(targetPaneElement.position().top);
        }
        if (currentlySelectedMarkerId == lastSelectedMarkerId) {
            return true;
        }
        $.post("/log_user_map_action/", {user_action: "saw_marker", photo_id: markerId}, function () {});
        if (lastSelectedPaneElement) {
            lastSelectedPaneElement.find(".ajapaik-eye-open").removeClass("ajapaik-eye-open-white");
        }
        lastSelectedMarkerId = markerId;
        lastSelectedPaneElement = targetPaneElement;
        for (i = 0; i < markers.length; i += 1) {
            if (lastHighlightedMarker) {
                if (lastHighlightedMarker.rephotoId) {
                    setIcon(lastHighlightedMarker, "blue", 20);
                } else {
                    setIcon(lastHighlightedMarker, null, 20);
                }
            }
            if (markers[i].id == markerId) {
                targetPaneElement.find("img").attr("src", markers[i].thumb);
                if (markers[i].rephotoId) {
                    setIcon(markers[i], "blue", 35);
                } else {
                    setIcon(markers[i], null, 35);
                }
                markers[i].setZIndex(maxIndex);
                maxIndex += 1;
                targetPaneElement.find(".ajapaik-eye-open").addClass("ajapaik-eye-open-white");
                markerTemp = markers[i];
                if (markers[i].azimuth) {
                    line.setPath([markers[i].position, calculateLineEndPoint(markers[i].azimuth, markers[i].position)]);
                    line.setMap(window.map);
                    line.setVisible(true);
                } else {
                    line.setVisible(false);
                }
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

    $(document).ready(function () {
        $('.top .score_container').hoverIntent(showScoreboard, hideScoreboard);

        $('#open-photo-drawer').click(function (e) {
            e.preventDefault();
            openPhotoDrawer();
        });

        if (typeof(markers) !== "undefined") {
            for (i = 0; i < markers.length; i += 1) {
                var newAElement = document.createElement("a");
                $(newAElement).click(function (e) {
                    e.preventDefault();
                    window.highlightSelected(e.target.dataset.id, false);
                }).attr("id", "element" + markers[i].id).attr("data-id", markers[i].id);
                var newImgElement = document.createElement("img");
                $(newImgElement).attr("src", "").attr("data-original", markers[i].thumb).attr("title", markers[i].description)
                    .attr("data-id", markers[i].id).addClass("lazy").attr("height", 150).attr("width", markers[i].thumbWidth);
                $(newAElement).attr("src", markers[i].thumb);
                var newEyeElement = document.createElement("div");
                $(newEyeElement).addClass("ajapaik-eye-open").click(function (e) {
                    window.loadPhoto(e.target.dataset.id);
                }).attr("data-id", markers[i].id).attr("id", "eye" + markers[i].id).hover(function() {
                    $(this).addClass("ajapaik-eye-open-white");
                }, function() {
                    var t = $(this);
                    if (t.attr("data-id") !== currentlySelectedMarkerId) {
                        $(this).removeClass("ajapaik-eye-open-white");
                    }
                });
                if (markers[i].rephotoId) {
                    $(newEyeElement).addClass("ajapaik-eye-open-blue");
                } else {
                    $(newEyeElement).addClass("ajapaik-eye-open-black");
                }
                newAElement.appendChild(newImgElement);
                newAElement.appendChild(newEyeElement);
                photoPane.append(newAElement);
            }
        }

        if (typeof(markers) !== "undefined") {
            photoPane.justifiedGallery(justifiedGallerySettings);
        }

        $(function () {
            var lazyImages = $("img.lazy");
            if (lazyImages.length > 0) {
                lazyImages.lazyload(lazyloadSettings);
            }
        });

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