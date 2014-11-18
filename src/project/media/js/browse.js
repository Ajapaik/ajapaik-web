(function () {
    "use strict";
    /*jslint nomen: true */
    /*global FB */
    /*global geotaggedPhotos */
    /*global _gaq */
    /*global markers */

    var photoId,
        cityId,
        photoDrawerElement = $('#photo-drawer'),
        photoPaneContainer = $("#photo-pane-container"),
        i = 0,
        maxIndex = 2,
        lastHighlightedMarker,
        lastSelectedPaneElement;

    window.loadPhoto = function(id) {
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
        History.replaceState(null, null, "/kaart/?city__pk=" + window.cityId);
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

    window.toggleVisiblePaneElements = function () {
        if (window.map) {
            for (i = 0; i < markers.length; i += 1) {
                var currentElement = $("#element" + markers[i].id);
                if (window.map.getBounds().contains(markers[i].getPosition())) {
                    currentElement.show();
                } else {
                    currentElement.hide();
                }
            }
            photoPaneContainer.trigger("scroll");
        }
    };

    var dottedLineSymbol = {
        path: google.maps.SymbolPath.CIRCLE,
        strokeOpacity: 1,
        strokeWeight: 1.5,
        strokeColor: 'red',
        scale: 0.75
    };

    var line = new google.maps.Polyline({
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
    });

    var lineLength = 0.01;
    Math.radians = function(degrees) {
        return degrees * Math.PI / 180;
    };
    var calculateLineEndPoint = function(azimuth, startPoint) {
        azimuth = Math.radians(azimuth);
        var newX = Math.cos(azimuth) * lineLength + startPoint.lat();
        var newY = Math.sin(azimuth) * lineLength + startPoint.lng();
        return new google.maps.LatLng(newX, newY);
    };

    window.highlightSelected = function (markerId, fromMarker) {
        window.currentlySelectedMarkerId = markerId;
        var targetPaneElement = $("#element" + markerId);
        if (fromMarker) {
            photoPaneContainer.scrollTop(photoPaneContainer.scrollTop() + targetPaneElement.position().top);
        }
        if (window.currentlySelectedMarkerId == window.lastSelectedMarkerId) {
            return true;
        }

        if (lastSelectedPaneElement) {
            lastSelectedPaneElement.removeClass("selected-pane-element");
        }
        window.lastSelectedMarkerId = markerId;
        lastSelectedPaneElement = targetPaneElement;
        var markerTemp;
        for (i = 0; i < markers.length; i += 1) {
            if (lastHighlightedMarker) {
                if (lastHighlightedMarker.rephotoId) {
                    lastHighlightedMarker.setIcon("/media/gfx/ajapaik_marker_20px_blue.png");
                } else {
                    lastHighlightedMarker.setIcon("/media/gfx/ajapaik_marker_20px.png");
                }
            }
            if (markers[i].id == markerId) {
                targetPaneElement.find("img").attr("src", markers[i].thumb);
                if (markers[i].rephotoId) {
                    markers[i].setIcon("/media/gfx/ajapaik_marker_35px_blue.png");
                } else {
                    markers[i].setIcon("/media/gfx/ajapaik_marker_35px.png");
                }
                markers[i].setZIndex(maxIndex);
                maxIndex += 1;
                targetPaneElement.addClass("selected-pane-element");
                markerTemp = markers[i];
                console.log(markers[i].azimuth);
                line.setPath([markers[i].position, calculateLineEndPoint(markers[i].azimuth, markers[i].position)]);
                line.setMap(window.map);
                line.setVisible(true);
            }
        }
        lastHighlightedMarker = markerTemp;
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

    $(document).ready(function () {
        $('.top .score_container').hoverIntent(showScoreboard, hideScoreboard);

        $('#open-photo-drawer').click(function (e) {
            e.preventDefault();
            openPhotoDrawer();
        });

        if (typeof(markers) !== "undefined") {
            for (i = 0; i < markers.length; i += 1) {
                var newElementDiv = document.createElement("div");
                $(newElementDiv).addClass("element").click(function (e) {
                    window.highlightSelected(e.target.dataset.id, false);
                }).hide().attr("id", "element" + markers[i].id).attr("data-id", markers[i].id);
                var newImgElement = document.createElement("img");
                $(newImgElement).attr("data-original", markers[i].thumb).attr("title", markers[i].description)
                    .attr("data-id", markers[i].id).addClass("lazy").attr("height", 150);
                var newButtonElement = document.createElement("a");
                $(newButtonElement).addClass("btn green").click(function (e) {
                    window.loadPhoto(e.target.dataset.id);
                }).attr("data-id", markers[i].id).attr("id", "button" + markers[i].id).html(gettext("Open photo"));
                newElementDiv.appendChild(newImgElement);
                newElementDiv.appendChild(newButtonElement);
                $("#photo-pane").append(newElementDiv);
            }
        }

        $(function () {
            var lazyImages = $("img.lazy");
            if (lazyImages.length > 0) {
                lazyImages.lazyload({
                container: photoPaneContainer,
                effect: "fadeIn",
                threshold: 50
            });
            }
        });

        var timeout = setTimeout(function () {
            photoPaneContainer.trigger("scroll");
        }, 1000);

        if (typeof(window.map) !== "undefined") {
            google.maps.event.addListener(window.map, 'bounds_changed', function () {
                window.toggleVisiblePaneElements();
            });
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