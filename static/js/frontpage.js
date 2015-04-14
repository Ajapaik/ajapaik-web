(function ($) {
    'use strict';
    $(document).ready(function () {
        var albumGalleryDiv = $('#ajapaik-frontpage-albums-tab'),
            historicPhotoGalleryDiv = $('#ajapaik-frontpage-photos-tab'),
            rephotoGalleryDiv = $('#ajapaik-frontpage-rephotos-tab'),
            getInfiniteScrollPhotos,
            initialHistoricPhotoLoad = true,
            initialRephotoLoad = true,
            historicPhotoAjaxQueryInProgress = false,
            rephotoAjaxQueryInProgress = false,
            activeTab = 'albums';
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
        rephotoGalleryDiv.justifiedGallery({
            captions: false,
            rowHeight: 270,
            margins: 5
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
            } else if (activeTab === 'rephoto') {
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
                            var i, l;
                            for (i = 0, l = result.length; i < l; i += 1) {
                                rephotoGalleryDiv.append(window.tmpl('ajapaik-frontpage-rephoto', result[i]));
                            }
                            window.rephotoInfiniteStart += window.photoPageSize;
                            rephotoGalleryDiv.justifiedGallery('norewind');
                            rephotoAjaxQueryInProgress = false;
                        }
                    });
                }
            }
        };
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
            if (initialHistoricPhotoLoad && $(e.target).attr('href') === '#ajapaik-frontpage-photos-tab') {
                activeTab = 'historic';
                getInfiniteScrollPhotos();
                initialHistoricPhotoLoad = false;
            } else if (initialRephotoLoad && $(e.target).attr('href') === '#ajapaik-frontpage-rephotos-tab') {
                activeTab = 'rephoto';
                getInfiniteScrollPhotos();
                initialRephotoLoad = false;
            }
        });
        $(window).scroll(function () {
            if (activeTab === 'historic') {
                if ($(window).scrollTop() + $(window).height() === $(document).height() && !historicPhotoAjaxQueryInProgress &&
                        window.historicPhotoInfiniteStart <= window.totalHistoricPhotoCount) {
                    getInfiniteScrollPhotos();
                }
            } else if (activeTab === 'rephoto') {
                if ($(window).scrollTop() + $(window).height() === $(document).height() && !rephotoAjaxQueryInProgress &&
                        window.rephotoInfiniteStart <= window.totalRephotoCount) {
                    getInfiniteScrollPhotos();
                }
            }
        });
    });
}(jQuery));