(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        window.updateLeaderboard();
        window.albumId = null;
        window.photoHistory = [];
        var historicPhotoGalleryDiv = $('#ajapaik-frontpage-historic-photos'),
            historicPhotoAjaxQueryInProgress = false,
            historicPhotoGallerySettings = {
                captions: false,
                rowHeight: 270,
                margins: 5
            },
            getInfiniteScrollPhotos,
            openPhotoDrawer,
            fullScreenImage = $('#ajapaik-frontpage-full-screen-image'),
            photoModal = $('#ajapaik-photo-modal'),
            initializeStateFromURLParameters,
            refreshAlbumName,
            refreshAlbumPhotoCount,
            queryData,
            predefinedSet,
            predefinedSetSplit,
            previousPhoto;
        getInfiniteScrollPhotos = function () {
            if (!historicPhotoAjaxQueryInProgress && window.historicPhotoInfiniteStart <= window.currentAlbumPhotoCount) {
                historicPhotoAjaxQueryInProgress = true;
                queryData = {
                    start: window.historicPhotoInfiniteStart,
                    type: 'historic',
                    album: window.albumId
                };
                if (predefinedSetSplit) {
                    queryData.set = predefinedSetSplit;
                }
                $.ajax({
                    cache: false,
                    url: '/frontpage_infinity/',
                    data: queryData,
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
        refreshAlbumName = function (id) {
            window.albumName =  $('.ajapaik-navmenu').find("[data-id='" + id + "']").data('name');
        };
        refreshAlbumPhotoCount = function (id) {
            window.currentAlbumPhotoCount =  $('.ajapaik-navmenu').find("[data-id='" + id + "']").data('photos');
        };
        window.syncStateToURL = function () {
            var historyReplacementString = '/';
            if (predefinedSet) {
                historyReplacementString += 'photos/?set=' + predefinedSet;
            } else if (window.albumId) {
                historyReplacementString += 'photos/?album=' + window.albumId;
            }
            window.History.replaceState(null, window.title + ' – ' + window.albumName, historyReplacementString);
        };
        window.handleAlbumChange = function () {
            if (window.albumId != window.previousAlbumId) {
                historicPhotoGalleryDiv.empty();
                window.historicPhotoInfiniteStart = 0;
                historicPhotoGalleryDiv.justifiedGallery(historicPhotoGallerySettings);
                refreshAlbumName(window.albumId);
                refreshAlbumPhotoCount(window.albumId);
                $('#ajapaik-header-album-name').html(window.albumName);
                $('#ajapaik-album-name-container').css('visibility', 'visible');
                $('#ajapaik-header-game-button').show();
                $('#ajapaik-header-map-button').show();
                predefinedSet = null;
                predefinedSetSplit = null;
                getInfiniteScrollPhotos();
                syncStateToURL();
                window.updateLeaderboard();
            } else if (predefinedSet) {
                historicPhotoGalleryDiv.empty();
                window.historicPhotoInfiniteStart = 0;
                historicPhotoGalleryDiv.justifiedGallery(historicPhotoGallerySettings);
                getInfiniteScrollPhotos();
            }
            if (window.albumId == window.previousAlbumId) {
                $(window).scrollTop(0);
            }
        };
        initializeStateFromURLParameters = function () {
            window.albumId = window.getQueryParameterByName('album');
            predefinedSet = window.getQueryParameterByName('set');
            if (predefinedSet) {
                predefinedSetSplit = predefinedSet.split(',');
            }
            window.handleAlbumChange();
        };
        $('.ajapaik-navmenu').on('shown.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').show();
        }).on('hidden.bs.offcanvas', function () {
            $('#ajapaik-album-selection-overlay').hide();
        });
        initializeStateFromURLParameters();
        window.loadPhoto = function (id, previous) {
            if (!previous && previousPhoto) {
                window.photoHistory.push(previousPhoto);
                previousPhoto = null;
            }
            $.ajax({
                cache: false,
                url: '/foto/' + id + '/?isFrontpage=1',
                success: function (result) {
                    openPhotoDrawer(result);
                    if (window.FB !== undefined) {
                        window.FB.XFBML.parse();
                    }
                    previousPhoto = id;
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
                window.FB.XFBML.parse();
            });
        };
        $(document).on('click', '.ajapaik-frontpage-image-container', function (e) {
            e.preventDefault();
        });
        window.closePhotoDrawer = function () {
            $('#ajapaik-photo-modal').modal('toggle');
        };
        historicPhotoGalleryDiv.justifiedGallery(historicPhotoGallerySettings);
        getInfiniteScrollPhotos();
        $(document).on('click', '.ajapaik-frontpage-image-image', function (e) {
            window.loadPhoto(e.target.dataset.id);
        });
        $(window).scroll(function () {
            if ($(window).scrollTop() + $(window).height() === $(document).height() && !historicPhotoAjaxQueryInProgress) {
                getInfiniteScrollPhotos();
            }
        });
        $('.ajapaik-navbar').autoHidingNavbar();
    });
}(jQuery));