(function ($) {
    'use strict';
    /*jslint nomen: true*/
    $(document).ready(function () {
        window.updateLeaderboard();
        var historicPhotoGalleryDiv = $('#ajapaik-frontpage-historic-photos'),
            albumSelectionDiv = $('#ajapaik-album-selection-menu'),
            getInfiniteScrollPhotos,
            historicPhotoAjaxQueryInProgress = false,
            openPhotoDrawer,
            photoDrawerOpen = false,
            fullScreenImage = $('#ajapaik-frontpage-full-screen-image'),
            photoModal = $('#ajapaik-photo-modal');
        window.albumId = null;
        $('#full_leaderboard').bind('click', function (e) {
            e.preventDefault();
            var url = window.leaderboardFullURL;
            if (window.albumId) {
                url += 'album/' + window.albumId;
            }
            $.ajax({
                url: url,
                success: function (response) {
                    var modalWindow = $('#ajapaik-full-leaderboard-modal');
                    modalWindow.find('.scoreboard').html(response);
                    modalWindow.modal().on('shown.bs.modal', function () {
                        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                    });
                }
            });
            window._gaq.push(['_trackEvent', 'Frontpage', 'Full leaderboard']);
        });
        window.handleAlbumChange = function () {
            if (window.albumId != window.previousAlbumId) {
                historicPhotoGalleryDiv.empty();
                window.historicPhotoInfiniteStart = 0;
                historicPhotoGalleryDiv.justifiedGallery({
                    captions: false,
                    rowHeight: 270,
                    margins: 5
                });
                $('#ajapaik-header-album-name').html(window.albumName);
                $('#ajapaik-album-name-container').css('visibility', 'visible');
                $('#ajapaik-header-game-button').show();
                $('#ajapaik-header-map-button').show();
                getInfiniteScrollPhotos();
            }
        };
        $('.ajapaik-navmenu').on('shown.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').show();
        }).on('hidden.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').hide();
        });
        window.loadPhoto = function (id) {
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
        window.flipPhoto = function () {
            $.noop();
        };
        openPhotoDrawer = function (content) {
            photoDrawerOpen = true;
            photoModal.html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
                $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                fullScreenImage.prop('src', window.photoModalFullscreenImageUrl);
                $('#ajapaik-guess-panel-photo').prop('src', window.photoModalCurrentImageUrl);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1]);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1], '#ajapaik-frontpage-full-screen-image');
                $('#ajapaik-guess-panel-description').html(window.currentPhotoDescription).show();
                $('.ajapaik-game-show-description-button').hide();
                window.FB.XFBML.parse();
            });
        };
        window.closePhotoDrawer = function () {
            $('#ajapaik-photo-modal').modal('toggle');
            photoDrawerOpen = false;
        };
        $(document).on('click', '.ajapaik-frontpage-image-image', function (e) {
            window.loadPhoto(e.target.dataset.id);
        });
        albumSelectionDiv.justifiedGallery({
            rowHeight: 270,
            margins: 0,
            captions: false
        });
        historicPhotoGalleryDiv.justifiedGallery({
            captions: false,
            rowHeight: 270,
            margins: 5
        });
        getInfiniteScrollPhotos = function () {
            if (!historicPhotoAjaxQueryInProgress) {
                historicPhotoAjaxQueryInProgress = true;
                $.ajax({
                    cache: false,
                    url: '/frontpage_infinity/',
                    data: {
                        start: window.historicPhotoInfiniteStart,
                        type: 'historic',
                        album: window.albumId
                    },
                    success: function (result) {
                        var i, l;
                        for (i = 0, l = result.length; i < l; i += 1) {
                            historicPhotoGalleryDiv.append(window.tmpl('ajapaik-frontpage-historic-photo', result[i]));
                        }
                        window.historicPhotoInfiniteStart += window.photoPageSize;
                        historicPhotoGalleryDiv.justifiedGallery('norewind');
                        historicPhotoAjaxQueryInProgress = false;
                    }
                });
            }
        };
        getInfiniteScrollPhotos();
        $(window).scroll(function () {
            if ($(window).scrollTop() + $(window).height() === $(document).height() && !historicPhotoAjaxQueryInProgress) {
                getInfiniteScrollPhotos();
            }
        });
    });
}(jQuery));