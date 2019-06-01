(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    /*global docCookies*/
    /*global gettext*/
    /*global getQueryParameterByName*/
    /*global showPhotoMapIfApplicable*/
    /*global FB*/
    /*global tmpl*/
    /*global JSON*/
    /*global _gaq*/
    /*global interpolate*/
    $(document).ready(function () {
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
            photoModal = $('#ajapaik-photo-modal'),
            fullScreenImage = $('#ajapaik-full-screen-image'),
            rephotoFullScreenImage = $('#ajapaik-rephoto-full-screen-image'),
            openPhotoDrawer = function (content) {
                photoModal.html(content);
                photoModal.modal().find('#ajapaik-modal-photo').on('load', function () {
                    fullScreenImage.removeClass('ajapaik-photo-flipped');
                    rephotoFullScreenImage.attr('data-src', window.photoModalRephotoFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
                    if (window.fullscreenEnabled) {
                        fullScreenImage.attr('src', window.photoModalFullscreenImageUrl)
                            .attr('data-src', window.photoModalFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
                    } else {
                        fullScreenImage.attr('data-src', window.photoModalFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
                    }
//                    showPhotoMapIfApplicable();
                    $('.ajapaik-minimap-confirm-geotag-button').removeClass('ajapaik-minimap-confirm-geotag-button-done');
                    if (window.FB) {
                        window.FB.XFBML.parse($('#ajapaik-photo-modal-like').get(0));
                    }
                    $('#ajapaik-video-modal').hide();
                });
            },
            syncStateToUrl = function () {
                var currentUrl = window.URI(window.location.href);
                currentUrl.removeSearch('photo').removeSearch('page').removeSearch('order1').removeSearch('order2')
                    .removeSearch('order3').removeSearch('lat').removeSearch('lon').removeSearch('q')
                    .removeSearch('locationToolsOpen').removeSearch('myLikes').removeSearch('rephotosBy');
                if (window.currentlySelectedPhotoId) {
                    currentUrl.addSearch('photo', window.currentlySelectedPhotoId);
                }
                if (window.showPhotos) {
                    if (window.order1) {
                        currentUrl.addSearch('order1', window.order1);
                    }
                    if (window.order2) {
                        currentUrl.addSearch('order2', window.order2);
                    }
                    if (window.order3) {
                        currentUrl.addSearch('order3', window.order3);
                    }
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
                if (window.myLikes) {
                    currentUrl.addSearch('myLikes', 1);
                }
                if (window.rephotosBy) {
                    currentUrl.addSearch('rephotosBy', window.rephotosBy);
                }
                if (window.albumQuery) {
                    currentUrl.addSearch('q', window.albumQuery);
                } else if (window.photoQuery) {
                    currentUrl.addSearch('q', window.photoQuery);
                }
                if (window.locationToolsOpen) {
                    currentUrl.addSearch('locationToolsOpen', 1);
                }
                window.history.replaceState(null, window.title, currentUrl);
            },
            oldPhotoSearchVal,
            oldAlbumSearchVal,
            timeout,
            albumSearchTimeout,
            syncFilteringHighlights = function () {
                var orderingString = '';
                $('.ajapaik-filter-white').attr('class', 'ajapaik-filter-gray');
                if (window.order1 === 'time') {
                    $('#ajapaik-time-filter-icon').attr('class', 'ajapaik-filter-white');
                    if (window.order3 === 'reverse') {
                        orderingString += gettext('Earliest');
                    } else {
                        orderingString += gettext('Latest');
                    }
                } else if (window.order1 === 'amount') {
                    $('#ajapaik-amount-filter-icon').attr('class', 'ajapaik-filter-white');
                    if (window.order3 === 'reverse') {
                        orderingString += gettext('Least');
                    } else {
                        orderingString += gettext('Most');
                    }
                } else if (window.order1 === 'closest') {
                    $('#ajapaik-closest-filter-icon').attr('class', 'ajapaik-filter-white');
                    if (window.order3 === 'reverse') {
                        orderingString = gettext('Pictures furthest from you');
                    } else {
                        orderingString = gettext('Pictures closest to you');
                    }
                }
                if (window.order2 === 'comments') {
                    $('#ajapaik-comments-filter-icon').attr('class', 'ajapaik-filter-white');
                    orderingString += ' ' + gettext('commented');
                } else if (window.order2 === 'rephotos') {
                    $('#ajapaik-rephotos-filter-icon').attr('class', 'ajapaik-filter-white');
                    orderingString += ' ' + gettext('rephotographed');
                } else if (window.order2 === 'added' && window.order1 !== 'closest') {
                    $('#ajapaik-added-filter-icon').attr('class', 'ajapaik-filter-white');
                    orderingString += ' ' + gettext('added');
                } else if (window.order2 === 'geotags') {
                    $('#ajapaik-geotags-filter-icon').attr('class', 'ajapaik-filter-white');
                    orderingString += ' ' + gettext('geotagged');
                } else if (window.order2 === 'likes') {
                    $('#ajapaik-likes-filter-icon').attr('class', 'ajapaik-filter-white');
                    orderingString += ' ' + gettext('liked');
                } else if (window.order2 === 'datings') {
                    $('#ajapaik-datings-filter-icon').attr('class', 'ajapaik-filter-white');
                    orderingString += ' ' + gettext('dated');
                } else if (window.order2 === 'views') {
                    $('#ajapaik-views-filter-icon').attr('class', 'ajapaik-filter-white');
                    orderingString += ' ' + gettext('viewed');
                } else if (window.order2 === 'stills') {
                    $('#ajapaik-stills-filter-icon').attr('class', 'ajapaik-filter-white');
                } else if (window.order2 === 'similar_photos') {
                    $('#ajapaik-similar-photos-filter-icon').attr('class', 'ajapaik-filter-white');
                }
                if (window.order1 !== 'closest') {
                    orderingString += ' ' + gettext('pictures');
                }
                if (window.order2 === 'stills') {
                    if (window.order3 === 'reverse') {
                        orderingString = gettext('By reverse timestamp');
                    } else {
                        orderingString = gettext('By timestamp');
                    }
                }
                if (getQueryParameterByName('photos')) {
                    orderingString = gettext('Pictures from the map');
                    var orderingStringTarget = $('#ajapaik-header-title');
                    if (orderingStringTarget) {
                        orderingStringTarget.html(orderingString + ' <i id="ajapaik-header-arrow-drop-down" class="material-icons notranslate">arrow_drop_down</i>');
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
            },
            syncPagingButtons = function () {
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
            },
            updateFrontpageAlbumsAsync = function () {
                $('#ajapaik-loading-overlay').show();
                $('#ajapaik-filtering-dropdown').addClass('d-none');
                $('#ajapaik-album-filter-box').removeClass('d-none');
                $('#ajapaik-photo-filter-box').addClass('d-none');
                $('#ajapaik-frontpage-historic-photos').addClass('d-none');
                syncStateToUrl();
                $.ajax({
                    url: window.frontpageAlbumsAsyncURL + window.location.search,
                    method: 'GET',
                    success: function (response) {
                        window.start = response.start;
                        window.end = response.end;
                        window.total = response.total;
                        window.maxPage = response.max_page;
                        window.currentPage = response.page;
                        window.showPhotos = response.show_photos;
                        syncStateToUrl();
                        syncPagingButtons();
                        var targetDiv = $('#ajapaik-album-selection');
                        targetDiv.empty();
                        for (var i = 0, l = response.albums.length; i < l; i += 1) {
                            targetDiv.append(tmpl('ajapaik-frontpage-album-template', response.albums[i]));
                        }
                        albumSelectionDiv.justifiedGallery();
                        $('#ajapaik-loading-overlay').hide();
                        $(window).scrollTop(0);
                        $('.ajapaik-frontpage-album').hover(function () {
                            $(this).find('.ajapaik-album-selection-caption-bottom').removeClass('d-none');
                        }, function () {
                            $(this).find('.ajapaik-album-selection-caption-bottom').addClass('d-none');
                        });
                    },
                    error: function () {
                        $('#ajapaik-loading-overlay').hide();
                    }
                });
            },
            updateModeSelection = function () {
                var selectedModeDiv = $('#ajapaik-header-selected-mode'),
                    title;
                selectedModeDiv.find('i').hide();
                albumSelectionDiv.addClass('ajapaik-invisible d-none');
                historicPhotoGalleryDiv.removeClass('ajapaik-invisible d-none');
                if (!window.showPhotos) {
                    title = gettext('Albums');
                    albumSelectionDiv.removeClass('ajapaik-invisible d-none');
                    historicPhotoGalleryDiv.addClass('ajapaik-invisible d-none');
                    $('#ajapaik-header-album-icon').show();
                    updateFrontpageAlbumsAsync();
                } else if (window.myLikes) {
                    title = gettext('My favorites');
                    $('#ajapaik-header-likes-icon').show();
                    window.updateFrontpagePhotosAsync();
                } else if (window.rephotosBy) {
                    if (window.rephotosBy === window.currentProfileId) {
                        title = gettext('My rephotos');
                    } else {
                        var fmt = gettext('Rephotos by %(user)s');
                        title = interpolate(fmt, {user: window.rephotosByName}, true);
                    }
                    $('#ajapaik-header-rephotos-icon').show();
                    window.updateFrontpagePhotosAsync();
                } else if (!window.albumId) {
                    title = gettext('All photos');
                    $('#ajapaik-header-pictures-icon').show();
                    albumSelectionDiv.addClass('ajapaik-invisible d-none');
                    historicPhotoGalleryDiv.removeClass('ajapaik-invisible d-none');
                    window.updateFrontpagePhotosAsync();
                } else if (window.albumId) {
                    window.updateFrontpagePhotosAsync();
                }
                selectedModeDiv.find('span').html(title + ' <i id="ajapaik-header-arrow-drop-down" class="material-icons notranslate">arrow_drop_down</i>');
            },
            doDelayedPhotoFiltering = function (val) {
                if (timeout) {
                    clearTimeout(timeout);
                }
                timeout = setTimeout(function () {
                    if (val !== oldPhotoSearchVal) {
                        oldPhotoSearchVal = val;
                        window.albumQuery = null;
                        window.photoQuery = val;
                        window.currentPage = null;
                        _gaq.push(['_trackEvent', 'Frontpage', 'Search photos']);
                        syncStateToUrl();
                        window.updateFrontpagePhotosAsync();
                    }
                }, 1000);
            },
            doDelayedAlbumFiltering = function (val) {
                if (albumSearchTimeout) {
                    clearTimeout(albumSearchTimeout);
                }
                albumSearchTimeout = setTimeout(function () {
                    if (val !== oldAlbumSearchVal) {
                        oldAlbumSearchVal = val;
                        window.albumQuery = val;
                        window.photoQuery = null;
                        window.currentPage = null;
                        _gaq.push(['_trackEvent', 'Frontpage', 'Search albums']);
                        syncStateToUrl();
                        updateFrontpageAlbumsAsync();
                    }
                }, 1000);
            };
        window.updateFrontpagePhotosAsync = function () {
            var targetDiv = $('#ajapaik-frontpage-historic-photos');
            targetDiv.removeClass('hidden ajapaik-invisible');
            $('#ajapaik-loading-overlay').show();
            $('#ajapaik-filtering-dropdown').removeClass('d-none');
            $('#ajapaik-album-filter-box').addClass('d-none');
            $('#ajapaik-photo-filter-box').removeClass('d-none');
            syncStateToUrl();
            $.ajax({
                url: window.frontpageAsyncURL + window.location.search,
                method: 'GET',
                success: function (response) {
                    window.start = response.start;
                    window.end = response.end;
                    window.total = response.total;
                    window.maxPage = response.max_page;
                    window.currentPage = response.page;
                    window.showPhotos = response.show_photos;
                    let collection;
                    let attribute = window.order2;
                    switch(window.order2){
                        case 'rephotos':
                            collection = response.photos_with_rephotos;
                            break;
                        case 'comments':
                            collection = response.photos_with_comments;
                            break;
                    }
                    if (collection !== undefined && collection === 0) {
                        $('#ajapaik-sorting-error-message').text(gettext('Picture set has no ' + attribute));
                        $('#ajapaik-sorting-error').show();
                        window.setTimeout(function () {
                            $('#ajapaik-sorting-error').hide();
                        }, 2000);
                    }
                    syncStateToUrl();
                    syncPagingButtons();
                    targetDiv.empty();
                    if (response.videos) {
                        $.each(response.videos, function (k, v) {
                            targetDiv.append(tmpl('ajapaik-frontpage-video-template', v));
                        });
                    }
                    if (response.photos.length > 0) {
                        for (var i = 0, l = response.photos.length; i < l; i += 1) {
                            targetDiv.append(tmpl('ajapaik-frontpage-photo-template', response.photos[i]));
                        }
                        historicPhotoGalleryDiv.justifiedGallery();
                    }
                    if (response.videos && response.videos.length > 0 && response.photos.length === 0) {
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
        if (getQueryParameterByName('q')) {
            var query = getQueryParameterByName('q');
            $('#ajapaik-album-filter-box').val(query).trigger('change');
            $('#ajapaik-photo-filter-box').val(query);
            window.photoQuery = query;
            window.albumQuery = query;
        }
        updateModeSelection();
        window.updateLeaderboard();
        // Local implementations for common functionality
        window.handleAlbumChange = function () {
            window.location.href = '/?album=' + window.albumId;
        };
        window.startGuessLocation = function (photoId) {
            var startLat,
                startLon;
            window.startGuessScrollTop = $(window).scrollTop();
            if (window.photoModalPhotoLat && window.photoModalPhotoLng) {
                startLat = window.photoModalPhotoLat;
                startLon = window.photoModalPhotoLng;
            } else if (window.albumLat && window.albumLon) {
                startLat = window.albumLat;
                startLon = window.albumLon;
            } else if (window.photoModalExtraLat && window.photoModalExtraLng) {
                startLat = window.photoModalExtraLat;
                startLon = window.photoModalExtraLng;
            } else {
                startLat = 59;
                startLon = 26;
            }
            $('#ajapaik-frontpage-container').hide();
            $('#ajapaik-photo-modal').hide();
            $('html').addClass('ajapaik-html-game-map');
            $('body').removeClass('ajapaik-body-frontpage').addClass('ajapaik-body-game-map');
            $('.modal-backdrop').hide();
            $('.footer').hide();
            $('#ajp-geotagging-container').show().data('AjapaikGeotagger').initializeGeotaggerState({
                thumbSrc: '/photo-thumb/' + photoId + '/400/',
                photoFlipped: window.photoModalCurrentPhotoFlipped,
                fullScreenSrc: window.photoModalFullscreenImageUrl,
                description: window.currentPhotoDescription,
                sourceKey: window.currentPhotoSourceKey,
                sourceName: window.currentPhotoSourceName,
                sourceURL: window.currentPhotoSourceURL,
                startLat: startLat,
                startLng: startLon,
                photoId: photoId,
                uniqueGeotagCount: window.photoModalGeotaggingUserCount,
                uniqueGeotagWithAzimuthCount: window.photoModalAzimuthCount,
                mode: 'vantage',
                markerLocked: true,
                isGame: false,
                isMapview: false,
                isGallery: true,
                tutorialClosed: docCookies.getItem('ajapaik_closed_geotagger_instructions') === 'true',
                hintUsed: true
            });
            window.locationToolsOpen = true;
            syncStateToUrl();
        };
        window.stopGuessLocation = function () {
            $('#ajp-geotagging-container').hide();
            $('#ajapaik-frontpage-container').show();
            $('#ajapaik-photo-modal').show();
            $('html').removeClass('ajapaik-html-game-map');
            $('body').addClass('ajapaik-body-frontpage').removeClass('ajapaik-body-game-map');
            $('.modal-backdrop').show();
            $('.footer').show();
            var currentUrl = window.URI(window.location.href),
                selectedPhoto = window.currentlySelectedPhotoId;
            currentUrl.removeSearch('photo');
            window.currentlySelectedPhotoId = null;
            window.history.replaceState(null, window.title, currentUrl);
            window.updateFrontpagePhotosAsync();
            window.locationToolsOpen = false;
            window.currentlySelectedPhotoId = selectedPhoto;
            syncStateToUrl();
//            showPhotoMapIfApplicable();
            if (window.startGuessScrollTop) {
                setTimeout(function () {
                    $(window).scrollTop(window.startGuessScrollTop);
                    window.startGuessScrollTop = null;
                }, 1000);
            }
        };
        window.loadPhoto = function (id) {
            window.nextPhotoLoading = true;
            window.photoModalPhotoLat = null;
            window.photoModalPhotoLng = null;
            window.photoModalPhotoAzimuth = null;
            $.ajax({
                cache: false,
                url: '/photo/' + id + '/?isFrontpage=1',
                success: function (result) {
                    window.nextPhotoLoading = false;
                    openPhotoDrawer(result);
                    window.currentlySelectedPhotoId = id;
                    syncStateToUrl();
                    var imgContainer = $('#ajapaik-frontpage-image-container-' + id),
                        nextId = imgContainer.next().data('id'),
                        previousId = imgContainer.prev().data('id'),
                        nextButton = $('.ajapaik-photo-modal-next-button'),
                        previousButton = $('.ajapaik-photo-modal-previous-button'),
                        originalPhotoColumn = $('#ajapaik-photo-modal-original-photo-column'),
                        originalPhotoInfoColumn = $('#ajapaik-photo-modal-original-photo-info-column'),
                        rephotoColumn = $('#ajapaik-photo-modal-rephoto-column'),
                        mainPhotoContainer = $('#ajapaik-modal-photo-container');
                    mainPhotoContainer.AjapaikFaceTagger();
                    mainPhotoContainer.data('AjapaikFaceTagger').initializeFaceTaggerState({photoId: id});
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
                        previousButton.removeClass('disabled');
                    }
                    if (window.userClosedRephotoTools) {
                        $('#ajapaik-rephoto-selection').hide();
                        $('#ajapaik-photo-modal-map-container').show();
                        rephotoColumn.hide();
                        $('#ajapaik-photo-modal-rephoto-info-column').hide();
                        if (!window.photoModalPhotoLat && !window.photoModalPhotoLng) {
                            originalPhotoColumn.removeClass("col-lg-6").addClass("col-lg-12");
                            originalPhotoInfoColumn.removeClass("col-lg-6").addClass("col-lg-12");
                        }   
                    }
                    if ((!window.photoModalPhotoLat && !window.photoModalPhotoLng) || (window.photoModalRephotoArray.length > 0 && !window.userClosedRephotoTools)) {
                        $('#ajapaik-photo-modal-map-container').hide();
                    }
                    if (window.photoModalRephotoArray && window.photoModalRephotoArray[0] && window.photoModalRephotoArray[0][2] !== 'None' && window.photoModalRephotoArray[0][2] !== '') {
                        $('#ajapaik-photo-modal-date-row').show();
                    }
                    // showPhotoMapIfApplicable();
                    $('.ajapaik-minimap-confirm-geotag-button').removeClass('ajapaik-minimap-confirm-geotag-button-done');
                },
                error: function () {
                    window.nextPhotoLoading = false;
                }
            });
        };
        window.handleGeolocation = function (location) {
            if (window.clickedMapButton) {
                $('#ajapaik-geolocation-error').hide();
                window.location.href = '/map?lat=' + location.coords.latitude + '&lng=' + location.coords.longitude + '&limitToAlbum=0&zoom=15';
            } else {
                $('#ajapaik-geolocation-error').hide();
                window.userLat = location.coords.latitude;
                window.userLon = location.coords.longitude;
                syncStateToUrl();
                syncFilteringHighlights();
                window.updateFrontpagePhotosAsync();
            }
        };
        window.closePhotoDrawer = function () {
            $('#ajapaik-photo-modal').modal('hide');
        };
        window.uploadCompleted = function () {
            $('#ajapaik-rephoto-upload-modal').modal('hide');
            window.location.reload();
        };
        // Reactions to specific URL params
        if (getQueryParameterByName('photo')) {
            window.loadPhoto(getQueryParameterByName('photo'));
        }
        if (getQueryParameterByName('order1') === 'closest') {
            if (!getQueryParameterByName('lat') || !getQueryParameterByName('lon')) {
                window.useButtonLink = false;
                window.getGeolocation(window.handleGeolocation);
            }
        }
        if (parseInt(getQueryParameterByName('locationToolsOpen'), 10) === 1) {
            window.straightToSpecify = true;
        }
        if (getQueryParameterByName('video')) {
            window.loadVideo(getQueryParameterByName('video'));
        }
        if (getQueryParameterByName('t')) {
            window.currentVideoTimeTarget = getQueryParameterByName('t');
        }
        // Page element functionality
        photoModal.on('shown.bs.modal', function () {
//            showPhotoMapIfApplicable();
            $('.ajapaik-minimap-confirm-geotag-button').removeClass('ajapaik-minimap-confirm-geotag-button-done');
            _gaq.push(['_trackEvent', 'Gallery', 'Photo modal open']);
            syncStateToUrl();
            if (window.straightToSpecify) {
                window.straightToSpecify = false;
                $('#ajapaik-photo-modal-specify-location').click();
                $('.modal-backdrop').hide();
            }
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
            if (window.currentVideoId) {
                $('#ajapaik-video-modal').show();
            }
            $('#ajapaik-full-screen-image').removeClass('ajapaik-photo-flipped');
        });
        $(document).on('click', '.ajapaik-frontpage-image-container', function (e) {
            e.preventDefault();
        });
        albumSelectionDiv.justifiedGallery(historicPhotoGallerySettings).on('jg.complete', function () {
            albumSelectionDiv.removeClass('ajapaik-invisible');
            $('.footer').removeClass('ajapaik-invisible');
        });
        historicPhotoGalleryDiv.justifiedGallery(historicPhotoGallerySettings).on('jg.complete', function () {
            historicPhotoGalleryDiv.removeClass('ajapaik-invisible');
            $('.footer').removeClass('ajapaik-invisible');
        });
        $(document).on('click', '.ajapaik-frontpage-image', function () {
            hideScoreboard();
            window.loadPhoto($(this).data('id'));
        });

        $(document).on('click', '#ajapaik-paging-previous-button', function (e) {
            e.preventDefault();
            if (window.currentPage > 1) {
                window.currentPage -= 1;
                window.history.pushState({ajapaikTag: true}, '', window.location);
                syncStateToUrl();
                if (window.showPhotos) {
                    window.updateFrontpagePhotosAsync();
                } else {
                    updateFrontpageAlbumsAsync();
                }
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
        $('#ajapaik-mode-select').find('a').click(function (e) {
            e.preventDefault();
            var $this = $(this),
                selectedMode = $this.data('mode');
            if ($this.hasClass('disabled')) {
                return false;
            }
            window.albumQuery = null;
            if (!window.order1) {
                window.order1 = 'time';
            }
            if (!window.order2) {
                window.order2 = 'added';
            }
            window.currentPage = 1;
            syncStateToUrl();
            syncFilteringHighlights();
            window.myLikes = false;
            window.rephotosBy = null;
            window.rephotosByName = null;
            switch (selectedMode) {
                case 'pictures':
                    window.showPhotos = true;
                    var currentUrl1 = window.URI(window.location.href);
                    currentUrl1.removeSearch('photos');
                    window.history.replaceState(null, window.title, currentUrl1);
                    //window.updateFrontpagePhotosAsync();
                    break;
                case 'albums':
                    if (window.albumId) {
                        window.location.href = '/';
                    }
                    window.showPhotos = false;
                    var currentUrl2 = window.URI(window.location.href);
                    currentUrl2.removeSearch('photos').removeSearch('q');
                    window.history.replaceState(null, window.title, currentUrl2);
                    window.order1 = null;
                    window.order2 = null;
                    window.order3 = null;
                    //updateFrontpageAlbumsAsync();
                    break;
                case 'likes':
                    window.myLikes = true;
                    window.showPhotos = true;
                    //window.updateFrontpagePhotosAsync();
                    break;
                case 'rephotos':
                    window.rephotosBy = window.currentProfileId;
                    window.rephotosByName = window.currentProfileName;
                    window.showPhotos = true;
                    //window.updateFrontpagePhotosAsync();
                    break;
            }
            updateModeSelection();
        });
        $(document).on('change textInput input', '#ajapaik-album-filter-box', function () {
            doDelayedAlbumFiltering(this.value.toLowerCase());
        });
        $(document).on('change textInput input', '#ajapaik-photo-filter-box', function () {
            doDelayedPhotoFiltering($(this).val());
        });
        $(document).on('click', '#ajapaik-paging-next-button', function (e) {
            e.preventDefault();
            if (window.currentPage < window.maxPage) {
                window.currentPage += 1;
                window.history.pushState({ajapaikTag: true}, '', window.location);
                syncStateToUrl();
                if (window.showPhotos) {
                    window.updateFrontpagePhotosAsync();
                } else {
                    updateFrontpageAlbumsAsync();
                }
            }
        });
        window.addEventListener('load', function () {
            setTimeout(function () {
                window.addEventListener('popstate', function () {
                    window.location.reload();
                });
            }, 0);
        });
        $(document).on('click', '.ajapaik-frontpage-album', function (e) {
            e.preventDefault();
            var $this = $(this);
            if (window.isMobile && window.albumWithOneClickDone != $this.attr('data-id')) {
                window.albumWithOneClickDone = $this.attr('data-id');
                $this.find('.ajapaik-album-selection-caption-bottom').removeClass('d-none');
            } else {
                if ($('#ajapaik-album-filter-box').val()) {
                    _gaq.push(['_trackEvent', 'Gallery', 'Album click with search term']);
                } else {
                    _gaq.push(['_trackEvent', 'Gallery', 'Album click']);
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
            if (window.order1 === 'closest') {
                window.order2 = null;
                if (!window.userLat || !window.userLon) {
                    window.getGeolocation(window.handleGeolocation, window.geolocationError);
                }
            }
            if (window.order1 === 'amount') {
                if (!window.order2) {
                    window.order2 = 'comments';
                }
                if (window.order2 === 'added') {
                    window.order2 = 'geotags';
                }
            }
            if (window.order2 && window.order1 === 'closest') {
                window.order1 = 'time';
            }
            if (window.order1 === 'time' && !window.order2) {
                window.order2 = 'added';
            }
            syncStateToUrl();
            syncFilteringHighlights();
            window.updateFrontpagePhotosAsync();
        });
        syncFilteringHighlights();
    });
}(jQuery));
