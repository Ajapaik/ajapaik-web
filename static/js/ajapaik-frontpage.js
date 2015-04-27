(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        window.updateLeaderboard();
        window.photoHistory = [];
        window.photoHistoryIndex = null;
        window.nextPhotoLoading = false;
        var historicPhotoGalleryDiv = $('#ajapaik-frontpage-historic-photos'),
            historicPhotoGallerySettings = {
                captions: false,
                rowHeight: 270,
                margins: 5,
                waitThumbnailsLoad: false
            },
            openPhotoDrawer,
            fullScreenImage = $('#ajapaik-frontpage-full-screen-image'),
            photoModal = $('#ajapaik-photo-modal'),
            previousPhoto;
        window.handleAlbumChange = function () {
            window.location.href = '/photos/' + window.albumId + '/1/';
        };
        window.startGuessLocation = function (photoId) {
            window.open('/map/photo/' + photoId + '/?photoModalOpen=1&straightToSpecify=1&fromModal=1', '_blank');
        };
        $('.ajapaik-navmenu').on('shown.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').show();
        }).on('hidden.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').hide();
        });
        window.loadPhoto = function (id, previous) {
            window.nextPhotoLoading = true;
            var loadingFromHistory = false;
            if (previous) {
                // We can only go back if we have history and we haven't reached the beginning
                if (window.photoHistory.length > 0 && window.photoHistoryIndex >= 0) {
                    // Move back 1 step, don't go to -1
                    if (window.photoHistoryIndex > 0) {
                        window.photoHistoryIndex -= 1;
                    }
                    // Get the photo id to load from history
                    id = window.photoHistory[window.photoHistoryIndex];
                    loadingFromHistory = true;
                }
            } else {
                // There's no history or we've reached the end, load a new photo
                if (window.photoHistory.length === 0 || window.photoHistoryIndex === (window.photoHistory.length - 1)) {
                    $.noop();
                } else {
                    // There's history and we haven't reached the end
                    window.photoHistoryIndex += 1;
                    id = window.photoHistory[window.photoHistoryIndex];
                    loadingFromHistory = true;
                }
            }
            $.ajax({
                cache: false,
                url: '/foto/' + id + '/?isFrontpage=1',
                success: function (result) {
                    window.nextPhotoLoading = false;
                    openPhotoDrawer(result);
                    if (!loadingFromHistory) {
                        window.photoHistory.push(id);
                        window.photoHistoryIndex = window.photoHistory.length - 1;
                    }
                },
                error: function () {
                    window.nextPhotoLoading = false;
                }
            });
        };
        window.flipPhoto = function () {
            $.noop();
        };
        openPhotoDrawer = function (content) {
            photoModal.html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
                $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                fullScreenImage.prop('src', window.photoModalFullscreenImageUrl);
                $('#ajapaik-guess-panel-photo').prop('src', window.photoModalCurrentImageUrl);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1]);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1], '#ajapaik-frontpage-full-screen-image');
                $('#ajapaik-guess-panel-description').html(window.currentPhotoDescription).show();
                $('.ajapaik-game-show-description-button').hide();
                // TODO: Restore
                //window.FB.XFBML.parse();
            });
        };
        $(document).on('click', '.ajapaik-frontpage-image-container', function (e) {
            e.preventDefault();
        });
        window.closePhotoDrawer = function () {
            $('#ajapaik-photo-modal').modal('toggle');
        };
        historicPhotoGalleryDiv.justifiedGallery(historicPhotoGallerySettings);
        $(document).on('click', '.ajapaik-frontpage-image-image', function (e) {
            window.loadPhoto(e.target.dataset.id);
        });
        $('.ajapaik-navbar').autoHidingNavbar();
        window.uploadCompleted = function (response) {
            $('#ajapaik-rephoto-upload-modal').modal('toggle');
        };
    });
}(jQuery));