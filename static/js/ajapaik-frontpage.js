(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        window.updateLeaderboard();
        window.nextPhotoLoading = false;
        window.userClosedRephotoTools = false;
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
            syncStateToUrl,
            currentlySelectedPhotoId;
        window.handleAlbumChange = function () {
            window.location.href = '/photos/' + window.albumId + '/1/';
        };
        window.startGuessLocation = function (photoId) {
            if (window.albumId) {
                window.open('/game/?album=' + window.albumId + '&photo=' + photoId, '_blank');
            } else {
                window.open('/game/?photo=' + photoId, '_blank');
            }
        };
        $('.ajapaik-navmenu').on('shown.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').show();
        }).on('hidden.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').hide();
        });
        window.loadPhoto = function (id) {
            window.nextPhotoLoading = true;
            $.ajax({
                cache: false,
                url: '/foto/' + id + '/?isFrontpage=1',
                success: function (result) {
                    window.nextPhotoLoading = false;
                    openPhotoDrawer(result);
                    currentlySelectedPhotoId = id;
                },
                error: function () {
                    window.nextPhotoLoading = false;
                }
            });
        };
        if (window.getQueryParameterByName('photo')) {
            window.loadPhoto(window.getQueryParameterByName('photo'));
        }
        window.flipPhoto = function () {
            $.noop();
        };
        syncStateToUrl = function () {
            var historyReplacementString = location.protocol + '//' + location.host + location.pathname;
            if (currentlySelectedPhotoId) {
                historyReplacementString += '?photo=' + currentlySelectedPhotoId;
            }
            //var historyReplacementString = '/game/';
            //if (window.albumId) {
            //    historyReplacementString += '?album=' + window.albumId;
            //} else if (window.areaId) {
            //    historyReplacementString += '?area=' + window.areaId;
            //}
            window.History.replaceState(null, window.title, historyReplacementString);
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
                window.FB.XFBML.parse();
            });
        };
        photoModal.on('shown.bs.modal', function () {
            syncStateToUrl();
        }).on('hidden.bs.modal', function () {
            currentlySelectedPhotoId = null;
            syncStateToUrl();
        });
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