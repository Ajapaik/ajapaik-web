(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        window.updateLeaderboard();
        if (window.getQueryParameterByName('forceAlbum')) {
            window.forceAlbum = true;
        }
        var pagingNextButton = $('#ajapaik-paging-next-button'),
            pagingPreviousButton = $('#ajapaik-paging-previous-button'),
            historicPhotoGalleryDiv = $('#ajapaik-frontpage-historic-photos'),
            albumSelectionDiv = $('#ajapaik-album-selection'),
            historicPhotoGallerySettings = {
                captions: false,
                rowHeight: 270,
                margins: 5,
                waitThumbnailsLoad: false,
                filter: function (el) {
                    return !$(el).hasClass('hidden');
                }
            },
            openPhotoDrawer,
            fullScreenImage = $('#ajapaik-full-screen-image'),
            rephotoFullScreenImage = $('#ajapaik-rephoto-full-screen-image'),
            photoModal = $('#ajapaik-photo-modal'),
            syncStateToUrl,
            oldVal;
        window.handleAlbumChange = function () {
            window.location.href = '/?album=' + window.albumId;
        };
        window.startGuessLocation = function (photoId) {
            if (window.albumId) {
                window.open('/game/?album=' + window.albumId + '&photo=' + photoId + '&fromButton=1', '_blank');
            } else {
                window.open('/game/?photo=' + photoId + '&fromButton=1', '_blank');
            }
        };
        window.loadPhoto = function (id) {
            window.nextPhotoLoading = true;
            $.ajax({
                cache: false,
                url: '/foto/' + id + '/?isFrontpage=1',
                success: function (result) {
                    window.nextPhotoLoading = false;
                    openPhotoDrawer(result);
                    window.currentlySelectedPhotoId = id;
                    syncStateToUrl();
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
                    if (window.photoHistory && window.photoHistory.length > 0) {
                        $('.ajapaik-photo-modal-previous-button').removeClass('disabled');
                    }
                    if (window.userClosedRephotoTools) {
                        $('#ajapaik-rephoto-selection').hide();
                        $('#ajapaik-photo-modal-rephoto-column').hide();
                        if (window.isMapview) {
                            $('#ajapaik-photo-modal-original-photo-info-column').removeClass('col-xs-5').removeClass('col-xs-6').addClass('col-xs-12');
                            $('#ajapaik-photo-modal-original-photo-column').removeClass('col-xs-5').removeClass('col-xs-6').addClass('col-xs-12');
                        } else {
                            $('#ajapaik-photo-modal-original-photo-info-column').removeClass('col-xs-4').removeClass('col-xs-5').addClass('col-xs-10');
                            $('#ajapaik-photo-modal-original-photo-column').removeClass('col-xs-4').removeClass('col-xs-5').addClass('col-xs-10');
                        }
                        $('#ajapaik-photo-modal-rephoto-info-column').hide();
                    }
                    if (window.photoModalRephotoArray && window.photoModalRephotoArray[0] && window.photoModalRephotoArray[0][2] !== 'None' && window.photoModalRephotoArray[0][2] !== '') {
                        $('#ajapaik-photo-modal-date-row').show();
                    }
                    var originalPhotoColumn = $('#ajapaik-photo-modal-original-photo-column');
                    originalPhotoColumn.mouseenter(function () {
                        if (!window.isMobile) {
                            $(this).find('.ajapaik-thumbnail-selection-icon').show();
                            $('.ajapaik-flip-photo-overlay-button').show();
                            if (window.userClosedRephotoTools) {
                                $('#ajapaik-show-rephoto-selection-overlay-button').show();
                            }
                        }
                    });
                    originalPhotoColumn.mouseleave(function () {
                        if (!window.isMobile) {
                            $(this).find('.ajapaik-thumbnail-selection-icon').hide();
                            $('.ajapaik-flip-photo-overlay-button').hide();
                            $('#ajapaik-show-rephoto-selection-overlay-button').hide();
                        }
                    });
                    var rephotoColumn = $('#ajapaik-photo-modal-rephoto-column');
                    rephotoColumn.mouseenter(function () {
                        if (!window.isMobile) {
                            if (!window.userClosedRephotoTools) {
                                $('#ajapaik-close-rephoto-overlay-button').show();
                                $('#ajapaik-invert-rephoto-overlay-button').show();
                            }
                        }
                    });
                    rephotoColumn.mouseleave(function () {
                        if (!window.isMobile) {
                            if (!window.userClosedRephotoTools) {
                                $('#ajapaik-close-rephoto-overlay-button').hide();
                                $('#ajapaik-invert-rephoto-overlay-button').hide();
                            }
                        }
                    });
                },
                error: function () {
                    window.nextPhotoLoading = false;
                }
            });
        };
        window.handleGeolocation = function (location) {
            $('#ajapaik-geolocation-error').hide();
            window.userLat = location.coords.latitude;
            window.userLon = location.coords.longitude;
            window.setTimeout(function () {
                $('#ajapaik-frontpage-show-pictures-link').click();
            }, 500);
            syncStateToUrl();
            syncFilteringHighlights();
            updateFrontpagePhotosAsync();
        };
        // TODO: Decide what to do, this redirect breaks UX
        //if (window.isMobile && !window.forceAlbum) {
        //    if (window.order1 === 'time' && window.order2 === 'added') {
        //        window.order1 = 'closest';
        //        window.order2 = undefined;
        //        window.getGeolocation(window.handleGeolocation);
        //    }
        //}
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
            // TODO: Unfinished
            $.noop();
        };
        syncStateToUrl = function () {
            var currentUrl = window.URI(window.location.href);
            currentUrl.removeSearch('photo').removeSearch('page').removeSearch('order1').removeSearch('order2')
                .removeSearch('order3').removeSearch('lat').removeSearch('lon').removeSearch('q');
            if (window.currentlySelectedPhotoId) {
                currentUrl.addSearch('photo', window.currentlySelectedPhotoId);
            }
            if (window.order1) {
                currentUrl.addSearch('order1', window.order1);
            }
            if (window.order2) {
                currentUrl.addSearch('order2', window.order2);
            }
            if (window.order3) {
                currentUrl.addSearch('order3', window.order3);
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
            if (window.albumQuery) {
                currentUrl.addSearch('q', window.albumQuery);
            }
            window.History.replaceState(null, window.title, currentUrl);
        };
        openPhotoDrawer = function (content) {
            photoModal.html(content);
            photoModal.modal().find('#ajapaik-modal-photo').on('load', function () {
                fullScreenImage.prop('src', window.photoModalFullscreenImageUrl);
                fullScreenImage.removeClass('ajapaik-photo-flipped');
                if (window.photoModalCurrentPhotoFlipStatus) {
                    fullScreenImage.addClass('ajapaik-photo-flipped');
                }
                rephotoFullScreenImage.prop('src', window.photoModalRephotoFullscreenImageUrl);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0],
                    window.photoModalFullscreenImageSize[1], '#ajapaik-full-screen-image');
                if (window.photoModalRephotoFullscreenImageSize) {
                    window.prepareFullscreen(window.photoModalRephotoFullscreenImageSize[0],
                        window.photoModalRephotoFullscreenImageSize[1], '#ajapaik-rephoto-full-screen-image');
                }
                window.FB.XFBML.parse($('#ajapaik-photo-modal-like').get(0));
            });
        };
        photoModal.on('shown.bs.modal', function () {
            window._gaq.push(['_trackEvent', 'Gallery', 'Photo modal open']);
            syncStateToUrl();
        }).on('hidden.bs.modal', function () {
            window.currentlySelectedPhotoId = null;
            syncStateToUrl();
            if (window.nextPageOnModalClose) {
                window.nextPageOnModalClose = false;
                window.setTimeout(function () {
                    $('#ajapaik-paging-next-button').click();
                }, 1500);
            } else if (window.previousPageOnModalClose) {
                window.previousPageOnModalClose = false;
                if (window.currentPage > 1) {
                    window.setTimeout(function () {
                        $('#ajapaik-paging-previous-button').click();
                    }, 1500);
                }
            }
            $('#ajapaik-full-screen-image').removeClass('ajapaik-photo-flipped');
        });
        $(document).on('click', '.ajapaik-frontpage-image-container', function (e) {
            e.preventDefault();
        });
        window.closePhotoDrawer = function () {
            $('#ajapaik-photo-modal').modal('toggle');
        };
        albumSelectionDiv.justifiedGallery(historicPhotoGallerySettings);
        historicPhotoGalleryDiv.justifiedGallery(historicPhotoGallerySettings);
        $(document).on('click', '.ajapaik-frontpage-image', function () {
            window.loadPhoto($(this).data('id'));
        });
        $('.ajapaik-navbar').autoHidingNavbar();
        window.uploadCompleted = function () {
            $('#ajapaik-rephoto-upload-modal').modal('toggle');
            window.location.reload();
        };
        //if (!window.docCookies.getItem('ajapaik_closed_general_info')) {
        //    $('#ajapaik-header-about-button').click();
        //    window.docCookies.setItem('ajapaik_closed_general_info', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', 'ajapaik.ee', false);
        //}
        var syncPagingButtons = function () {
            if (window.currentPage > 1) {
                pagingPreviousButton.show().removeClass('ajapaik-invisible');
            } else {
                pagingPreviousButton.hide();
            }
            if (window.currentPage < window.maxPage) {
                pagingNextButton.show().removeClass('ajapaik-invisible');
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
            var orderingString = '';
            $('.ajapaik-filter-white').attr('class', 'ajapaik-filter-gray');
            if (window.order1 === 'time') {
                $('#ajapaik-time-filter-icon').attr('class', 'ajapaik-filter-white');
                if (window.order3 === 'reverse') {
                    orderingString += window.gettext('Earliest');
                } else {
                    orderingString += window.gettext('Latest');
                }
            } else if (window.order1 === 'amount') {
                $('#ajapaik-amount-filter-icon').attr('class', 'ajapaik-filter-white');
                if (window.order3 === 'reverse') {
                    orderingString += window.gettext('Least');
                } else {
                    orderingString += window.gettext('Most');
                }
            } else if (window.order1 === 'closest') {
                $('#ajapaik-closest-filter-icon').attr('class', 'ajapaik-filter-white');
                if (window.order3 === 'reverse') {
                    orderingString = window.gettext('Pictures furthest from you');
                } else {
                    orderingString = window.gettext('Pictures closest to you');
                }
            }
            if (window.order2 === 'comments') {
                $('#ajapaik-comments-filter-icon').attr('class', 'ajapaik-filter-white');
                orderingString += ' ' + window.gettext('commented');
            } else if (window.order2 === 'rephotos') {
                $('#ajapaik-rephotos-filter-icon').attr('class', 'ajapaik-filter-white');
                orderingString += ' ' + window.gettext('rephotographed');
            } else if (window.order2 === 'added') {
                $('#ajapaik-added-filter-icon').attr('class', 'ajapaik-filter-white');
                orderingString += ' ' + window.gettext('added');
            } else if (window.order2 === 'geotags') {
                $('#ajapaik-geotags-filter-icon').attr('class', 'ajapaik-filter-white');
                orderingString += ' ' + window.gettext('geotagged');
            }
            if (window.order1 !== 'closest') {
                orderingString += ' ' + window.gettext('pictures');
            }
            if (window.getQueryParameterByName('photos')) {
                orderingString = window.gettext('Pictures from the map');
                var orderingStringTarget = $('#ajapaik-header-title');
                if (orderingStringTarget) {
                    orderingStringTarget.html(orderingString);
                }
            }
            var dropdownOrderingString = $('#ajapaik-filter-dropdown-filter-name');
            if (dropdownOrderingString) {
                dropdownOrderingString.html(orderingString);
            }
            var filterButton = $('#ajapaik-header-filter-icon');
            filterButton.attr('class', '');
            if (window.order2 !== 'added') {
                filterButton.attr('class', 'ajapaik-filter-white');
            }
            if (window.order3 === 'reverse') {
                $('#ajapaik-reverse-filter-icon').attr('class', 'ajapaik-filter-white');
            }
        };
        var updateFrontpagePhotosAsync = function () {
            $('#ajapaik-loading-overlay').show();
            $.ajax({
                url: '/frontpage_async/' + window.location.search,
                method: 'GET',
                success: function (response) {
                    window.start = response.start;
                    window.end = response.end;
                    window.total = response.total;
                    window.maxPage = response.max_page;
                    window.currentPage = response.page;
                    if (window.order2 == 'rephotos' && response.photos_with_rephotos === 0) {
                        $('#ajapaik-sorting-error-message').text(window.gettext('Picture set has no rephotos'));
                        $('#ajapaik-sorting-error').show();
                        window.setTimeout(function () {
                            $('#ajapaik-sorting-error').hide();
                        }, 2000);
                    }
                    if (window.order2 == 'comments' && response.photos_with_comments === 0) {
                        $('#ajapaik-sorting-error-message').text(window.gettext('Picture set has no comments'));
                        $('#ajapaik-sorting-error').show();
                        window.setTimeout(function () {
                            $('#ajapaik-sorting-error').hide();
                        }, 2000);
                    }
                    syncStateToUrl();
                    syncPagingButtons();
                    var targetDiv = $('#ajapaik-frontpage-historic-photos');
                    targetDiv.empty();
                    if (response.photos) {
                        for (var i = 0, l = response.photos.length; i < l; i += 1) {
                            targetDiv.append(window.tmpl('ajapaik-frontpage-photo-template', response.photos[i]));
                        }
                        //historicPhotoGalleryDiv.justifiedGallery(historicPhotoGallerySettings).on('jg.complete', function () {
                        //    historicPhotoGalleryDiv.removeClass('ajapaik-invisible');
                        //    $('.footer').removeClass('ajapaik-invisible');
                        //});
                        historicPhotoGalleryDiv.justifiedGallery();
                    }
                    $('#ajapaik-loading-overlay').hide();
                    $(window).scrollTop(0);
                },
                error: function () {
                    $('#ajapaik-loading-overlay').hide();
                }
            });
        };
        $(document).on('click', '#ajapaik-paging-previous-button', function (e) {
            e.preventDefault();
            if (window.currentPage > 1) {
                window.currentPage -= 1;
                syncStateToUrl();
                updateFrontpagePhotosAsync();
            }
        });
        $(document).on('click', '.ajapaik-album-selection-map-button', function (e) {
            e.preventDefault();
            e.stopPropagation();
            window.location.href = $(this).attr('data-href');
        });
        $(document).on('click', '.ajapaik-album-selection-game-button', function (e) {
            e.preventDefault();
            e.stopPropagation();
            window.location.href = $(this).attr('data-href');
        });
        $(document).on('click', '#ajapaik-frontpage-show-pictures-link', function (e) {
            e.preventDefault();
            if (!window.albumId) {
                if (!window.order1) {
                    window.order1 = 'time';
                }
                if (!window.order2) {
                    window.order2 = 'added';
                }
                if (!window.currentPage) {
                    window.currentPage = 1;
                }
                window.albumQuery = null;
                syncStateToUrl();
                syncFilteringHighlights();
                $('#ajapaik-frontpage-show-pictures-link').hide();
                $('#ajapaik-frontpage-show-albums-link').removeClass('hidden');
                $('#ajapaik-album-selection').hide();
                $('#ajapaik-header-album-icon').hide();
                $('#ajapaik-header-pictures-icon').attr('class', '');
                $('#ajapaik-filter-dropdown-filter-name').show();
                $('#ajapaik-pager').removeClass('ajapaik-invisible');
                $('#ajapaik-filtering-dropdown').removeClass('hidden');
                $('#ajapaik-album-filter-box').hide();
                $('#ajapaik-header-title').text(window.gettext('All pictures'));
                $('#ajapaik-frontpage-historic-photos').removeClass('hidden').justifiedGallery();
            } else {
                window.location.href = '/?order1=time&order2=added';
            }
        });
        $(document).on('change textInput input', '#ajapaik-album-filter-box', function () {
            var val = this.value.toLowerCase();
            if (val !== oldVal) {
                oldVal = val;
                window.albumQuery = val;
                window.currentPage = null;
                window.order1 = null;
                window.order2 = null;
                var titles = $('.ajapaik-caption-album-selection-album-title');
                for (var i = 0, l = titles.length; i < l; i += 1) {
                    if (titles[i].innerHTML.toLowerCase().match(val)) {
                        $(titles[i]).parent().parent().removeClass('hidden');
                    } else {
                        $(titles[i]).parent().parent().addClass('hidden');
                    }
                }
                syncStateToUrl();
                albumSelectionDiv.justifiedGallery();
            }
        });
        if (window.getQueryParameterByName('q')) {
            $('#ajapaik-album-filter-box').val(window.getQueryParameterByName('q')).trigger('change');
        }
        $('.ajapaik-frontpage-album').hover(function () {
            $(this).find('.ajapaik-caption-album-selection-upper').removeClass('ajapaik-invisible');
        }, function () {
            $(this).find('.ajapaik-caption-album-selection-upper').addClass('ajapaik-invisible');
        });
        $(document).on('click', '#ajapaik-paging-next-button', function (e) {
            e.preventDefault();
            if (window.currentPage < window.maxPage) {
                window.currentPage += 1;
                syncStateToUrl();
                updateFrontpagePhotosAsync();
            }
        });
        $(document).on('click', '.ajapaik-frontpage-album', function (e) {
            e.preventDefault();
            var $this = $(this);
            if (window.isMobile && window.albumWithOneClickDone != $this.attr('data-id')) {
                window.albumWithOneClickDone = $this.attr('data-id');
                $this.find('.ajapaik-caption-album-selection-upper').removeClass('ajapaik-invisible');
            } else {
                if ($('#ajapaik-album-filter-box').val()) {
                    window._gaq.push(['_trackEvent', 'Gallery', 'Album click with search term']);
                } else {
                    window._gaq.push(['_trackEvent', 'Gallery', 'Album click']);
                }
                window.location.href = $this.attr('href');
            }
        });
        $(document).on('click', '.ajapaik-filtering-choice', function (e) {
            e.stopPropagation();
            e.preventDefault();
            window.currentPage = 1;
            var $this = $(this);
            if ($this.data('order1')) {
                window.order1 = $this.data('order1');
            }
            if ($this.data('order2')) {
                window.order2 = $this.data('order2');
            }
            if ($this.data('order3')) {
                if (window.order3 === 'reverse') {
                    window.order3 = null;
                } else {
                    window.order3 = $this.data('order3');
                }
            }
            if ($this.data('order1') === 'none') {
                window.order1 = null;
            }
            if ($this.data('order2') === 'none') {
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
            if (window.order1 === 'closest') {
                if (window.order2) {
                    window.order1 = 'time';
                    syncStateToUrl();
                    syncFilteringHighlights();
                    updateFrontpagePhotosAsync();
                } else {
                    window.getGeolocation(window.handleGeolocation, window.geolocationError);
                }
            } else {
                syncStateToUrl();
                syncFilteringHighlights();
                updateFrontpagePhotosAsync();
            }
        });
        syncFilteringHighlights();
    });
}(jQuery));