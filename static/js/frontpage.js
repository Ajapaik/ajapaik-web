(function ($) {
    'use strict';
    $(document).ready(function () {
        window.updateLeaderboard();
        var historicPhotoGalleryDiv = $('#ajapaik-frontpage-historic-photos'),
            albumSelectionDiv = $('#ajapaik-album-selection-menu'),
            getInfiniteScrollPhotos,
            historicPhotoAjaxQueryInProgress = false;
        window.albumId = null;
        $('.ajapaik-navbar').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);
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
                getInfiniteScrollPhotos();
            }
        };
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
            if (!historicPhotoAjaxQueryInProgress &&
                    window.historicPhotoInfiniteStart <= window.totalHistoricPhotoCount) {
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
            if ($(window).scrollTop() + $(window).height() === $(document).height() && !historicPhotoAjaxQueryInProgress &&
                    window.historicPhotoInfiniteStart <= window.totalHistoricPhotoCount) {
                getInfiniteScrollPhotos();
            }
        });
    });
}(jQuery));