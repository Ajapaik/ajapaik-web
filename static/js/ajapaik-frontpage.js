(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        window.updateLeaderboard();
        var pagingNextButton = $('#ajapaik-paging-next-button'),
            pagingPreviousButton = $('#ajapaik-paging-previous-button');
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
            currentPhotoIds = [];
        $('.ajapaik-frontpage-image-container').each(function () {
            currentPhotoIds.push($(this).data('id'));
        });
        window.handleAlbumChange = function () {
            //window.location.href = '/photos/' + window.albumId + '/1';
            syncStateToUrl();
            updateFrontpagePhotosAsync();
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
                    window.currentlySelectedPhotoId = id;
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
            //if (window.useButtonLink) {
            //    window.location.href = window.originalClosestLink + '&lat=' + location.coords.latitude  + '&lng=' + location.coords.longitude;
            //} else {
            //    window.location.href = '?order1=closest&order2=closest&lat=' + location.coords.latitude  + '&lng=' + location.coords.longitude;
            //}
        };
        if (window.getQueryParameterByName('order1') === 'closest') {
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
            var currentUrl = window.URI(window.location.href);
            currentUrl.removeSearch('photo').removeSearch('page').removeSearch('order1').removeSearch('order2')
                .removeSearch('lat').removeSearch('lon');
            if (window.currentlySelectedPhotoId) {
                currentUrl.addSearch('photo', window.currentlySelectedPhotoId);
            }
            if (window.order1) {
                currentUrl.addSearch('order1', window.order1);
            }
            if (window.order2) {
                currentUrl.addSearch('order2', window.order2);
            }
            if (window.currentPage) {
                currentUrl.addSearch('page', window.currentPage);
            }
            if (window.userLat) {
                currentUrl.addSearch('lat', window.userLat);
            }
            if (window.userLon) {
                currentUrl.addSearch('lon', window.userLon);
            }
            //var historyReplacementString = location.protocol + '//' + location.host + location.pathname;
            //if (currentlySelectedPhotoId) {
            //    historyReplacementString += '?photo=' + currentlySelectedPhotoId;
            //}
            //if (window.getQueryParameterByName('set')) {
            //    historyReplacementString += '&set=' + window.getQueryParameterByName('set');
            //}
            //if (historyReplacementString.indexOf('?') === -1) {
            //    historyReplacementString = historyReplacementString.replace('&', '?');
            //}
            window.History.replaceState(null, window.title, currentUrl);
        };
        openPhotoDrawer = function (content) {
            photoModal.html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
                fullScreenImage.prop('src', window.photoModalFullscreenImageUrl);
                //$('#ajapaik-guess-panel-photo').prop('src', window.photoModalCurrentImageUrl);
                //window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1]);
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
            window.currentlySelectedPhotoId = null;
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
        //if (window.FB) {
        //    window.FB.XFBML.parse();
        //}
        $('.ajapaik-navbar').autoHidingNavbar();
        window.uploadCompleted = function () {
            $('#ajapaik-rephoto-upload-modal').modal('toggle');
        };
        if (!window.docCookies.getItem('ajapaik_closed_general_info')) {
            $('#ajapaik-header-about-button').click();
            window.docCookies.setItem('ajapaik_closed_general_info', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
        }
        var syncPagingButtons = function () {
            if (window.currentPage > 1) {
                pagingPreviousButton.show();
            }
            if (window.currentPage < window.maxPage) {
                pagingNextButton.show();
            } else {
                pagingNextButton.hide();
            }
            $('#ajapaik-pager-stats').text((parseInt(window.start, 10) + 1) + ' - ' + window.end + ' / ' + window.total);
            var currentURI = window.URI(window.location.href);
            currentURI.removeSearch('page').addSearch('page', window.currentPage - 1);
            $('#ajapaik-paging-previous-button').prop('href', currentURI);
            currentURI.removeSearch('page').addSearch('page', window.currentPage + 1);
            $('#ajapaik-paging-next-button').prop('href', currentURI);
        };
        var syncFilteringHighlights = function () {
            $('.ajapaik-filter-white').attr('class', 'ajapaik-filter-gray');
            if (window.order1 === 'time') {
                $('#ajapaik-time-filter-icon').attr('class', 'ajapaik-filter-white');
            } else if (window.order1 === 'amount') {
                $('#ajapaik-amount-filter-icon').attr('class', 'ajapaik-filter-white');
            } else if (window.order1 === 'closest') {
                $('#ajapaik-closest-filter-icon').attr('class', 'ajapaik-filter-white');
            }
            if (window.order2 === 'comments') {
                $('#ajapaik-comments-filter-icon').attr('class', 'ajapaik-filter-white');
            } else if (window.order2 === 'rephotos') {
                $('#ajapaik-rephotos-filter-icon').attr('class', 'ajapaik-filter-white');
            } else if (window.order2 === 'added') {
                $('#ajapaik-added-filter-icon').attr('class', 'ajapaik-filter-white');
            } else if (window.order2 === 'geotags') {
                $('#ajapaik-geotags-filter-icon').attr('class', 'ajapaik-filter-white');
            }
        };
        var updateFrontpagePhotosAsync = function () {
            $.ajax({
                url: '/frontpage_async/' + window.location.search,
                method: 'GET',
                success: function (response) {
                    window.start = response.start;
                    window.end = response.end;
                    window.total = response.total;
                    window.maxPage = response.max_page;
                    window.currentPage = response.page;
                    syncStateToUrl();
                    syncPagingButtons();
                    var targetDiv = $('#ajapaik-frontpage-historic-photos');
                    targetDiv.empty();
                    if (response.photos) {
                        for (var i = 0, l = response.photos.length; i < l; i += 1) {
                            targetDiv.append(window.tmpl('ajapaik-frontpage-photo-template', response.photos[i]));
                        }
                        historicPhotoGalleryDiv.justifiedGallery(historicPhotoGallerySettings);
                    }
                }
            });
        };
        $(document).on('click', '#ajapaik-paging-previous-button', function (e) {
            e.preventDefault();
            window.currentPage -= 1;
            syncStateToUrl();
            updateFrontpagePhotosAsync();
        });
        $(document).on('click', '#ajapaik-paging-next-button', function (e) {
            e.preventDefault();
            window.currentPage += 1;
            syncStateToUrl();
            updateFrontpagePhotosAsync();
        });
        $(document).on('click', '.ajapaik-filtering-choice', function (e) {
            if (e.target.dataset.order1) {
                window.order1 = e.target.dataset.order1;
            }
            if (e.target.dataset.order2) {
                window.order2 = e.target.dataset.order2;
            }
            if (e.target.dataset.order1 === 'null') {
                window.order1 = null;
            }
            if (e.target.dataset.order2 === 'null') {
                window.order2 = null;
            }
            if (window.order1 === 'amount' && !window.order2) {
                window.order2 = 'comments';
            }
            if (window.order1 === 'time' && !window.order2) {
                window.order2 = 'added';
            }
            if (window.order1 !== 'time' && window.order2 === 'added') {
                window.order2 = 'comments';
            }
            syncStateToUrl();
            syncFilteringHighlights();
            updateFrontpagePhotosAsync();
        });
        $('a.dropdown-toggle').click(function () {
            var target = $('#ajapaik-frontpage-filtering-dropdown');
            if (target.hasClass('open')) {
                target.removeClass('open');
            } else {
                target.addClass('open');
            }
        });
    });
}(jQuery));