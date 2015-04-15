(function ($) {
    'use strict';
    $(document).ready(function () {
        var albumGalleryDiv = $('#ajapaik-frontpage-albums-tab'),
            historicPhotoGalleryDiv = $('#ajapaik-frontpage-photos-tab'),
            //rephotoGalleryDiv = $('#ajapaik-frontpage-rephotos-tab'),
            getInfiniteScrollPhotos,
            initialHistoricPhotoLoad = true,
            //initialRephotoLoad = true,
            historicPhotoAjaxQueryInProgress = false,
            //rephotoAjaxQueryInProgress = false,
            activeTab = 'albums',
            infoModalDiv = $('#ajapaik-info-modal');
        albumGalleryDiv.justifiedGallery({
            captions: false,
            rowHeight: 270,
            margins: 5
        });
        historicPhotoGalleryDiv.justifiedGallery({
            captions: false,
            rowHeight: 270,
            margins: 5
        });
        $('.ajapaik-frontpage-album-image-image').click(function (e) {
            e.preventDefault();
            window.albumId = e.target.dataset.id;
            $.ajax({
                url: window.infoModalURL + window.albumId + '/',
                success: function (resp) {
                    infoModalDiv.html(resp);
                    infoModalDiv.modal().on('shown.bs.modal', function () {
                        $(window).resize(window.adjustModalMaxHeightAndPosition).trigger('resize');
                        window.FB.XFBML.parse();
                    });
                }
            });
        });
        /*rephotoGalleryDiv.justifiedGallery({
            captions: false,
            rowHeight: 270,
            margins: 5
        }).on('jg.complete', function () {
            var toResize = $('.ajapaik-frontpage-original-resize'),
                i,
                l,
                current,
                currentParent,
                rephotoWidth,
                rephotoHeight;
            for (i = 0, l = toResize.length; i < l; i += 1) {
                current = $(toResize[i]);
                currentParent = current.parent();
                rephotoWidth = currentParent.width();
                rephotoHeight = currentParent.height();
                current.css('width', rephotoWidth).css('height', rephotoHeight);
                current.find('img').css('width', rephotoWidth).css('height', rephotoHeight);
            }
        });*/
        $('#ajapaik-header').find('.score_container').hoverIntent(window.showScoreboard, window.hideScoreboard);
        window.updateLeaderboard();
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
        getInfiniteScrollPhotos = function () {
            if (activeTab === 'historic') {
                if (!historicPhotoAjaxQueryInProgress &&
                        window.historicPhotoInfiniteStart <= window.totalHistoricPhotoCount) {
                    historicPhotoAjaxQueryInProgress = true;
                    $.ajax({
                        cache: false,
                        url: '/frontpage_infinity/',
                        data: {
                            start: window.historicPhotoInfiniteStart,
                            type: activeTab
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
            } /*else if (activeTab === 'rephoto') {
                if (!rephotoAjaxQueryInProgress && window.rephotoInfiniteStart <= window.totalRephotoCount) {
                    rephotoAjaxQueryInProgress = true;
                    $.ajax({
                        cache: false,
                        url: '/frontpage_infinity/',
                        data: {
                            start: window.rephotoInfiniteStart,
                            type: activeTab
                        },
                        success: function (result) {
                            var i,
                                l;
                            for (i = 0, l = result.length; i < l; i += 1) {
                                rephotoGalleryDiv.append(window.tmpl('ajapaik-frontpage-rephoto', result[i]));
                            }
                            window.rephotoInfiniteStart += window.photoPageSize;
                            rephotoGalleryDiv.justifiedGallery('norewind');
                            rephotoAjaxQueryInProgress = false;
                        }
                    });
                }
            }*/
        };
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
            if (initialHistoricPhotoLoad && $(e.target).attr('href') === '#ajapaik-frontpage-photos-tab') {
                activeTab = 'historic';
                getInfiniteScrollPhotos();
                initialHistoricPhotoLoad = false;
            } /*else if (initialRephotoLoad && $(e.target).attr('href') === '#ajapaik-frontpage-rephotos-tab') {
                activeTab = 'rephoto';
                getInfiniteScrollPhotos();
                initialRephotoLoad = false;
            }*/
        });
        $(window).scroll(function () {
            if (activeTab === 'historic') {
                if ($(window).scrollTop() + $(window).height() === $(document).height() && !historicPhotoAjaxQueryInProgress &&
                        window.historicPhotoInfiniteStart <= window.totalHistoricPhotoCount) {
                    getInfiniteScrollPhotos();
                }
            } /*else if (activeTab === 'rephoto') {
                if ($(window).scrollTop() + $(window).height() === $(document).height() && !rephotoAjaxQueryInProgress &&
                        window.rephotoInfiniteStart <= window.totalRephotoCount) {
                    getInfiniteScrollPhotos();
                }
            }*/
        });
    });
}(jQuery));