(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        window.updateLeaderboard();
        window.nextPhotoLoading = false;
        window.userClosedRephotoTools = false;
        window.useButtonLink = true;
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
            currentlySelectedPhotoId,
            currentPhotoIds = [];
        $('.ajapaik-frontpage-image-container').each(function () {
            currentPhotoIds.push($(this).data('id'));
        });
        window.refreshFacebookCommentsCount(currentPhotoIds);
        window.handleCommentsCountResponse = function (response) {
            var target,
                commentCounts = [];
            for (var key in response) {
                if (response.hasOwnProperty(key)) {
                    target = $('[data-fb-id="' + key + '"]');
                    if (!response[key].comments) {
                        target.hide();
                    } else {
                        commentCounts.push({id: key.split(/[/]+/).pop(), comments: response[key].comments});
                        target.show().removeClass('hidden');
                    }
                }
            }
            $.post(window.updateCommentCountsURL, {
                //comments: commentCounts,
                'comments': JSON.stringify([
                    {
                        id: '12127', comments: 2
                    }
                ]),
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            }, function () {});
        };
        window.handleAlbumChange = function () {
            window.location.href = '/photos/' + window.albumId + '/1';
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
            if (window.albumId) {
                $('#ajapaik-album-selection-navmenu').scrollTop($(".ajapaik-album-selection-item[data-id='" + window.albumId + "']").offset().top);
            }
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
                    var imgContainer = $('#ajapaik-frontpage-image-container-' + id),
                        nextId = imgContainer.next().data('id'),
                        previousId = imgContainer.prev().data('id'),
                        nextButton = $('.ajapaik-photo-modal-next-button'),
                        previousButton = $('.ajapaik-photo-modal-previous-button');
                    if (!nextId) {
                        nextButton.addClass('ajapaik-photo-modal-next-button-disabled');
                    } else {
                        nextButton.removeClass('ajapaik-photo-modal-next-button-disabled');
                    }
                    if (!previousId) {
                        previousButton.addClass('ajapaik-photo-modal-previous-button-disabled');
                    } else {
                        previousButton.removeClass('ajapaik-photo-modal-previous-button-disabled');
                    }
                },
                error: function () {
                    window.nextPhotoLoading = false;
                }
            });
        };
        window.handleGeolocation = function (location) {
            if (window.useButtonLink) {
                window.location.href = window.originalClosestLink + '&lat=' + location.coords.latitude  + '&lng=' + location.coords.longitude;
            } else {
                window.location.href = '?order=closest&lat=' + location.coords.latitude  + '&lng=' + location.coords.longitude;
            }

        };
        if (window.getQueryParameterByName('order') === 'closest') {
            if (!window.getQueryParameterByName('lat') || !window.getQueryParameterByName('lng')) {
                window.useButtonLink = false;
                window.getGeolocation(window.handleGeolocation);
            }
        }
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
            if (window.getQueryParameterByName('set')) {
                historyReplacementString += '&set=' + window.getQueryParameterByName('set');
            }
            if (historyReplacementString.indexOf('?') === -1) {
                historyReplacementString = historyReplacementString.replace('&', '?');
            }
            window.History.replaceState(null, window.title, historyReplacementString);
        };
        openPhotoDrawer = function (content) {
            photoModal.html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
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
            window._gaq.push(['_trackEvent', 'Gallery', 'Photo modal open']);
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
        if (window.FB) {
            window.FB.XFBML.parse();
        }
        $('.ajapaik-navbar').autoHidingNavbar();
        window.uploadCompleted = function () {
            $('#ajapaik-rephoto-upload-modal').modal('toggle');
        };
        if (!window.docCookies.getItem('ajapaik_closed_general_info')) {
            $('#ajapaik-header-about-button').click();
            window.docCookies.setItem('ajapaik_closed_general_info', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
        }
    });
}(jQuery));