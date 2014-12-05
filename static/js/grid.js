(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global docCookies */
    /*global History */
    /*global FB */
    /*global _gaq */
    /*global URI */
    /*global document */
    /*global window */
    /*global setTimeout */
    /*global screen */
    /*global location */
    $(document).ready(function () {
        var galleryDiv = $('#gallery'),
            browseDiv = $('.container'),
            doGridAjaxQuery,
            ajaxQueryInProgress = false,
            loadMoreLink = $('#ajapaik-grid-load-more-link'),
            photoDrawerElement = $('#photo-drawer'),
            openPhotoDrawer,
            closePhotoDrawer,
            photoId;

        galleryDiv.justifiedGallery({
            rowHeight: 120,
            waitThumbnailsLoad: false,
            margins: 3,
            sizeRangeSuffixes: {
                'lt100': '',
                'lt240': '',
                'lt320': '',
                'lt500': '',
                'lt640': '',
                'lt1024': ''
            }
        });

        $.ajaxSetup({
            headers: { 'X-CSRFToken': docCookies.getItem('csrftoken') }
        });

        doGridAjaxQuery = function () {
            var i,
                newA,
                newImg;
            if (!ajaxQueryInProgress && window.start <= window.totalPhotoCount) {
                ajaxQueryInProgress = true;
                $.ajax({
                    cache: false,
                    url: '/grid_infinity/',
                    data: {city__pk: window.cityId, start: window.start},
                    success: function (result) {
                        for (i = 0; i < result.length; i += 1) {
                            newA = document.createElement('a');
                            newImg = document.createElement('img');
                            $(newA).addClass('ajapaik-grid-image-container').attr('href', result[i][1]);
                            $(newImg).attr('src', '').attr('data-src', result[i][1]).attr('width', result[i][2])
                                .attr('height', result[i][3]).attr('alt', result[i][0])
                                .addClass('lazyload').addClass('ajapaik-grid-image')
                                .attr('data-id', result[i][0]);
                            newA.appendChild(newImg);
                            $('#gallery').append(newA);
                        }
                        window.start += window.pageSize;
                        galleryDiv.justifiedGallery('norewind');
                        setTimeout(function () { $('.ajapaik-grid-image-container').css('opacity', 1); }, 100);
                        ajaxQueryInProgress = false;
                        $('.ajapaik-grid-image').on('click', function (e) {
                            e.preventDefault();
                            window.loadPhoto(e.target.dataset.id);
                        });
                        if (galleryDiv.innerHeight() < (browseDiv.height() * 1.5)) {
                            doGridAjaxQuery();
                        }
                    }
                });
            }
            if (window.start > window.totalPhotoCount) {
                loadMoreLink.hide();
                $('#ajapaik-grid-no-more-photos').show();
            }
        };

        if (galleryDiv.innerHeight() < browseDiv.height()) {
            window.start += window.pageSize;
            doGridAjaxQuery();
        }

        openPhotoDrawer = function (content) {
            photoDrawerElement.html(content);
            photoDrawerElement.animate({ top: '10%' });
        };

        closePhotoDrawer = function () {
            var historyReplacementString = '/grid/?city__pk=' + window.cityId;
            photoDrawerElement.animate({ top: '-1000px' });
            History.replaceState(null, null, historyReplacementString);
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
//                    $('a.iframe').fancybox({
//                        'width': '75%',
//                        'height': '75%',
//                        'autoScale': false,
//                        'hideOnContentClick': false
//                    });
                }
            });
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

        loadMoreLink.on('click', function (e) {
            e.preventDefault();
            doGridAjaxQuery();
        });

        browseDiv.scroll(function () {
            if ((browseDiv.scrollTop() - (browseDiv.height() * 0.75)) > 0 && !ajaxQueryInProgress && window.start <= window.totalPhotoCount) {
                doGridAjaxQuery();
            }
        });

        $('.ajapaik-grid-image-container').on('click', function (e) {
            e.preventDefault();
            var targetId = e.target.dataset.id;
            window.loadPhoto(targetId);
        });

        $('.ajapaik-grid-image').on('click', function (e) {
            e.preventDefault();
            var targetId = e.target.dataset.id;
            window.loadPhoto(targetId);
        });

        photoDrawerElement.delegate('#ajapaik-close-photo-drawer', 'click', function (e) {
            e.preventDefault();
            closePhotoDrawer();
        });

        photoDrawerElement.delegate('a.add-rephoto', 'click', function (e) {
            e.preventDefault();
            $('#notice').modal();
            _gaq.push(['_trackEvent', 'Map', 'Add rephoto']);
        });

        photoDrawerElement.delegate('#random-photo', 'click', function (e) {
            e.preventDefault();
            var imagesOnPage = $('.ajapaik-grid-image');
            window.loadPhoto(imagesOnPage[Math.floor(Math.random() * imagesOnPage.length)].dataset.id);
        });
    });
}());