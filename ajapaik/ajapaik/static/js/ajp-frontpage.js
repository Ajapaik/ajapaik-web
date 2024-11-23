(function($) {
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
    /*global gtag*/
    /*global interpolate*/
    $(document).ready(function() {
        let pagingNextButton = $('#ajp-paging-next-button'),
            pagingPreviousButton = $('#ajp-paging-previous-button'),
            historicPhotoGalleryDiv = $('#ajp-frontpage-historic-photos'),
            albumSelectionDiv = $('#ajp-album-selection'),
            historicPhotoGallerySettings = {
                captions: false,
                rowHeight: 270,
                margins: 5,
                waitThumbnailsLoad: false,
                filter: function(el) {
                    return !$(el).hasClass('hidden');
                },
            },
            photoModal = $('#ajp-photo-modal'),
            fullScreenImage = $('#ajp-fullscreen-image'),
            rephotoFullScreenImage = $('#ajp-rephoto-full-screen-image'),
            similarFullScreenImage = $('#ajp-similar-photo-full-screen-image'),
            openPhotoDrawer = function(content) {
                photoModal.html(content);
                photoModal
                    .modal()
                    .find('#ajp-modal-photo')
                    .on('load', function() {
                        let fullScreenImageWrapper = $('#ajp-fullscreen-image-wrapper');
                        fullScreenImageWrapper.removeClass('ajp-photo-flipped');
                        fullScreenImageWrapper.removeClass('rotate90');
                        fullScreenImageWrapper.removeClass('rotate180');
                        fullScreenImageWrapper.removeClass('rotate270');
                        rephotoFullScreenImage
                            .attr('data-src', window.photoModalRephotoFullscreenImageUrl)
                            .attr('alt', window.currentPhotoDescription);
                        similarFullScreenImage
                            .attr('data-src', window.photoModalSimilarFullscreenImageUrl)
                            .attr('alt', window.currentPhotoDescription);
                        if (window.fullscreenEnabled) {
                            fullScreenImage
                                .attr('src', window.photoModalFullscreenImageUrl)
                                .attr('data-src', window.photoModalFullscreenImageUrl)
                                .attr('alt', window.currentPhotoDescription);
                        } else {
                            fullScreenImage
                                .attr('data-src', window.photoModalFullscreenImageUrl)
                                .attr('alt', window.currentPhotoDescription);
                        }
                        if (window.FB) {
                            window.FB.XFBML.parse($('#ajp-photo-modal-like').get(0));
                        }
                        $('#ajp-video-modal').hide();
                    });
            },
            syncStateToUrl = function() {
                let currentUrl = window.URI(window.location.href);
                currentUrl
                    .removeSearch('photo')
                    .removeSearch('page')
                    .removeSearch('order1')
                    .removeSearch('order2')
                    .removeSearch('order3')
                    .removeSearch('lat')
                    .removeSearch('lon')
                    .removeSearch('q')
                    .removeSearch('locationToolsOpen')
                    .removeSearch('myLikes')
                    .removeSearch('rephotosBy');
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
                if (window.albumQuery || window.photoQuery) {
                    currentUrl.addSearch('q', window.albumQuery || window.photoQuery);
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
            syncFilteringHighlights = function() {
                let orderingString = gettext('Ordering') + ': ';
                $('.ajp-white').attr('class', 'ajp-gray');
                if (window.order1 === 'time') {
                    $('#ajp-time-filter-icon').attr('class', 'ajp-white');
                    if (window.order3 === 'reverse') {
                        orderingString += gettext('earliest');
                    } else {
                        orderingString += gettext('latest');
                    }
                } else if (window.order1 === 'amount') {
                    $('#ajp-amount-filter-icon').attr('class', 'ajp-white');
                    if (window.order3 === 'reverse') {
                        orderingString += gettext('least');
                    } else {
                        orderingString += gettext('most');
                    }
                } else if (window.order1 === 'closest') {
                    $('#ajp-closest-filter-icon').attr('class', 'ajp-white');
                    if (window.order3 === 'reverse') {
                        orderingString = gettext('Pictures furthest from you');
                    } else {
                        orderingString = gettext('Pictures closest to you');
                    }
                }
                if (window.order2 === 'comments') {
                    $('#ajp-comments-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('commented');
                } else if (window.order2 === 'rephotos') {
                    $('#ajp-rephotos-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('rephotographed');
                } else if (window.order2 === 'added' && window.order1 !== 'closest') {
                    $('#ajp-added-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('added');
                } else if (window.order2 === 'geotags') {
                    $('#ajp-geotags-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('geotagged');
                } else if (window.order2 === 'likes') {
                    $('#ajp-likes-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('liked');
                } else if (window.order2 === 'interior-categorization') {
                    $('#ajp-interior-categorization-filter-icon').attr(
                        'class',
                        'ajp-white',
                    );
                    orderingString += ' ' + gettext('categorized');
                } else if (window.order2 === 'exterior-categorization') {
                    $('#ajp-exterior-categorization-filter-icon').attr(
                        'class',
                        'ajp-white',
                    );
                    orderingString += ' ' + gettext('categorized');
                } else if (window.order2 === 'datings') {
                    $('#ajp-datings-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('dated');
                } else if (window.order2 === 'transcriptions') {
                    $('#ajp-transcriptions-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('transcribed');
                } else if (window.order2 === 'annotations') {
                    $('#ajp-annotations-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('annotated');
                } else if (window.order2 === 'views') {
                    $('#ajp-views-filter-icon').attr('class', 'ajp-white');
                    orderingString += ' ' + gettext('viewed');
                } else if (window.order2 === 'stills') {
                    $('#ajp-stills-filter-icon').attr('class', 'ajp-white');
                } else if (window.order2 === 'similar_photos') {
                    $('#ajp-similar-photos-filter-icon').attr('class', 'ajp-white');
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
                    const orderingStringTarget = $('#ajp-header-title');
                    if (orderingStringTarget) {
                        orderingStringTarget.html(
                            orderingString +
                            ' <span id="ajp-header-arrow-drop-down" class="material-icons notranslate">arrow_drop_down</span>',
                        );
                    }
                }
                const dropdownOrderingString = $(
                    '#ajp-organiser-dropdown-sort-order-name',
                );
                if (dropdownOrderingString) {
                    dropdownOrderingString.html(orderingString);
                }
                const filterButton = $('#ajp-header-filter-icon');
                filterButton.attr('class', '');

                let filterCount = 0;
                let photoFilters =
                    window.location.search.indexOf('order1=') > -1
                        ? window.galleryFilters
                        : window.albumFilters;
                photoFilters.forEach(function(filter) {
                    if (
                        window.location.search.indexOf('&' + filter + '=1') > -1 ||
                        window.location.search.indexOf('?' + filter + '=1') > -1
                    ) {
                        filterCount++;
                    }
                });
                if (window.order3 === 'reverse') {
                    $('#ajp-reverse-filter-icon').attr('class', 'ajp-white');
                }
                if (
                    (window.order2 && window.order2 !== 'added') ||
                    window.order3 ||
                    filterCount > 0
                ) {
                    filterButton.attr('class', 'ajp-white');
                }
            },
            syncPagingButtons = function() {
                if (window.currentPage > 1) {
                    pagingPreviousButton.show().removeClass('ajp-invisible');
                } else {
                    pagingPreviousButton.hide();
                }
                if (window.currentPage < window.maxPage) {
                    pagingNextButton.show().removeClass('ajp-invisible');
                } else {
                    pagingNextButton.hide();
                }
                $('#ajp-pager-stats').text(
                    parseInt(window.start, 10) +
                    1 +
                    ' - ' +
                    window.end +
                    ' / ' +
                    window.total,
                );
                const currentURI = window.URI(window.location.href);
                currentURI
                    .removeSearch('page')
                    .addSearch('page', window.currentPage - 1);
                $('#ajp-paging-previous-button').prop('href', currentURI);
                currentURI
                    .removeSearch('page')
                    .addSearch('page', window.currentPage + 1);
                $('#ajp-paging-next-button').prop('href', currentURI);
            },
            setWindowPaginationParameters = function(response) {
                window.start = response.start;
                window.end = response.end;
                window.total = response.total;
                window.maxPage = response.max_page;
                window.currentPage = response.page;
                window.showPhotos = response.show_photos;
            },
            updateFrontpageAlbumsAsync = function() {
                $('#ajp-loading-overlay').show();
                $('#ajp-album-filter-box').removeClass('d-none');
                $('#ajp-photo-filter-box').addClass('d-none');
                $('#ajp-frontpage-historic-photos').addClass('d-none');
                syncStateToUrl();
                $.ajax({
                    url: window.frontpageAlbumsAsyncURL + window.location.search,
                    method: 'GET',
                    success: function(response) {
                        setWindowPaginationParameters(response);
                        syncStateToUrl();
                        syncPagingButtons();
                        const targetDiv = $('#ajp-album-selection');
                        targetDiv.empty();
                        targetDiv.removeClass('w-100');
                        let array = window.location.search.split('&q=');
                        if (array && array.length > 1) {
                            $('#ajp-album-filter-box').val(
                                decodeURIComponent(array[array.length - 1])
                                    .replace('%2C', ',')
                                    .replace('%3A', ':')
                                    .replace('%2F', '/')
                                    .replace('+', ' '),
                            );
                        }
                        if (response.albums.length > 0) {
                            for (let i = 0, l = response.albums.length; i < l; i += 1) {
                                targetDiv.append(
                                    tmpl('ajp-frontpage-album-template', response.albums[i]),
                                );
                            }
                            albumSelectionDiv.justifiedGallery();
                        } else {
                            const queryStr = interpolate(
                                gettext('No results found for: %(query)s'),
                                { query: decodeURI(array[array.length - 1]) },
                                true,
                            );
                            targetDiv.append(
                                tmpl('ajp-frontpage-album-search-empty-template', [
                                    queryStr,
                                    gettext('Did you mean to search from:') + ' ',
                                    gettext('all pictures'),
                                    window.location.origin +
                                    '/?order1=time&order2=added&page=1&q=' +
                                    array[array.length - 1],
                                ]),
                            );
                            targetDiv.addClass('w-100');
                            targetDiv.height(window.innerHeight);
                            albumSelectionDiv
                                .removeClass('d-none')
                                .removeClass('justified-gallery');
                        }
                        $('#ajp-loading-overlay').hide();
                        $(window).scrollTop(0);
                        $('.ajp-frontpage-album').hover(
                            function() {
                                $(this)
                                    .find('.ajp-album-selection-caption-bottom')
                                    .removeClass('d-none');
                            },
                            function() {
                                $(this)
                                    .find('.ajp-album-selection-caption-bottom')
                                    .addClass('d-none');
                            },
                        );
                    },
                    error: function() {
                        $('#ajp-loading-overlay').hide();
                    },
                });
            },
            updateModeSelection = function() {
                let selectedModeDiv = $('#ajp-header-selected-mode'),
                    title;
                selectedModeDiv.find('i').hide();
                albumSelectionDiv.addClass('ajp-invisible d-none');
                historicPhotoGalleryDiv.removeClass('ajp-invisible d-none');
                if (!window.showPhotos) {
                    title = gettext('Albums');
                    albumSelectionDiv.removeClass('ajp-invisible d-none');
                    historicPhotoGalleryDiv.addClass('ajp-invisible d-none');
                    $('#ajp-header-album-icon').show();
                    updateFrontpageAlbumsAsync();
                } else {
                    if (window.myLikes) {
                        title = gettext('My favorites');
                        $('#ajp-header-likes-icon').show();
                    } else if (window.rephotosBy) {
                        if (window.rephotosBy === window.currentProfileId) {
                            title = gettext('My rephotos');
                        } else {
                            const fmt = gettext('Rephotos by %(user)s');
                            title = interpolate(fmt, { user: window.rephotosByName }, true);
                        }
                        $('#ajp-header-rephotos-icon').show();
                    } else if (!window.albumId) {
                        title = gettext('All pictures');
                        $('#ajp-header-pictures-icon').show();
                        $('#ajp-header-album-icon').hide();
                        albumSelectionDiv.addClass('ajp-invisible d-none');
                        historicPhotoGalleryDiv.removeClass('ajp-invisible d-none');
                    }
                    window.updateFrontpagePhotosAsync();
                }
                selectedModeDiv
                    .find('#ajp-header-title')
                    .html(
                        title +
                        ' <span id="ajp-header-arrow-drop-down" class="material-icons notranslate">arrow_drop_down</span>',
                    );
            },
            doDelayedPhotoFiltering = function(val) {
                if (timeout) {
                    clearTimeout(timeout);
                }
                timeout = setTimeout(function() {
                    if (val !== oldPhotoSearchVal) {
                        oldPhotoSearchVal = val;
                        window.albumQuery = null;
                        window.photoQuery = val;
                        window.currentPage = null;
                        gtag('event', 'search_photos', { 'category': 'Frontpage' });
                        syncStateToUrl();
                        window.updateFrontpagePhotosAsync();
                    }
                }, 1000);
            },
            doDelayedAlbumFiltering = function(val) {
                if (albumSearchTimeout) {
                    clearTimeout(albumSearchTimeout);
                }
                albumSearchTimeout = setTimeout(function() {
                    if (!window.showPhotos && val !== oldAlbumSearchVal) {
                        oldAlbumSearchVal = val;
                        window.albumQuery = val;
                        window.photoQuery = null;
                        window.currentPage = null;
                        gtag('event', 'search_albums', { 'category': 'Frontpage' });
                        syncStateToUrl();
                        updateFrontpageAlbumsAsync();
                    }
                }, 1000);
            };
        window.updateFrontpagePhotosAsync = function() {
            const targetDiv = $('#ajp-frontpage-historic-photos');
            targetDiv.removeClass('hidden ajp-invisible');
            $('#ajp-loading-overlay').show();
            $('#ajp-album-filter-box').addClass('d-none');
            $('#ajp-photo-filter-box').removeClass('d-none');
            syncStateToUrl();
            $.ajax({
                url: window.frontpageAsyncURL + window.location.search,
                method: 'GET',
                success: function(response) {
                    setWindowPaginationParameters(response);
                    let collection;
                    let attribute = window.order2;
                    let message = '';
                    let filterCount = 0;
                    let query =
                        window.location.search.indexOf('&q=') > -1 &&
                        window.location.search.split('?q=')[1];

                    switch (window.order2) {
                        case 'rephotos':
                            collection = response.photos_with_rephotos;
                            break;
                        case 'comments':
                            collection = response.photos_with_comments;
                            break;
                    }
                    window.galleryFilters
                        .concat('rephotosBy', 'myLikes')
                        .forEach(function(filter) {
                            if (
                                window.location.search.indexOf('&' + filter + '=1') > -1 ||
                                window.location.search.indexOf('?' + filter + '=1') > -1
                            ) {
                                filterCount++;
                            }
                        });

                    if (collection !== undefined && collection === 0) {
                        let translationString = 'Picture set has no ' + attribute;
                        $('#ajp-sorting-error-message').text(gettext(translationString));
                        $('#ajp-sorting-error').show();
                        window.setTimeout(function() {
                            $('#ajp-sorting-error').hide();
                        }, 2000);
                    }

                    syncStateToUrl();
                    syncPagingButtons();
                    targetDiv.empty();
                    targetDiv.removeClass('w-100');
                    if (
                        (!response.videos || response.videos.length < 1) &&
                        response.photos.length < 1
                    ) {
                        if (!!window.albumId) {
                            message += ' ' + 'in this album';
                        }
                        if (query) {
                            message = 'No results found for: %(query)s' + message;
                            if (filterCount > 0) {
                                message +=
                                    '\nYou could also try to edit filters applied to your search';
                            }
                        } else {
                            let categoryMessage;
                            if (filterCount > 1) {
                                categoryMessage =
                                    'No pictures were found with the selected filters';
                            } else if (window.location.search.indexOf('people=1') > 0) {
                                categoryMessage = 'No pictures with marked faces were found';
                            } else if (window.location.search.indexOf('backsides=1') > 0) {
                                categoryMessage = 'No pictures with back sides were found';
                            } else if (window.location.search.indexOf('interiors=1') > 0) {
                                categoryMessage = 'No interior views were found';
                            } else if (window.location.search.indexOf('exteriors=1') > 0) {
                                categoryMessage = 'No exterior views were found';
                            } else if (
                                window.location.search.indexOf('ground_viewpoint_elevation=1') >
                                0
                            ) {
                                categoryMessage =
                                    'No pictures from the ground level were found';
                            } else if (
                                window.location.search.indexOf('raised_viewpoint_elevation=1') >
                                0
                            ) {
                                categoryMessage = 'No raised viewpoint pictures were found';
                            } else if (
                                window.location.search.indexOf('aerial_viewpoint_elevation=1') >
                                0
                            ) {
                                categoryMessage = 'No aerial pictures were found';
                            } else if (window.location.search.indexOf('no_geotags=1') > 0) {
                                categoryMessage = 'No pictures which have 0 geotags were found';
                            } else if (window.location.search.indexOf('high_quality=1') > 0) {
                                categoryMessage = 'No high-quality pictures were found';
                            } else if (window.location.search.indexOf('portrait=1') > 0) {
                                categoryMessage = 'No pictures in portrait format were found';
                            } else if (window.location.search.indexOf('square=1') > 0) {
                                categoryMessage = 'No pictures in square format were found';
                            } else if (window.location.search.indexOf('panoramic=1') > 0) {
                                categoryMessage = 'No pictures in panoramic format were found';
                            } else if (window.location.search.indexOf('landscape=1') > 0) {
                                categoryMessage = 'No pictures in landscape format were found';
                            } else if (window.location.search.indexOf('landscape=1') > 0) {
                                categoryMessage = 'No pictures in landscape format were found';
                            } else if (window.location.search.indexOf('rephotosBy=') > 0) {
                                categoryMessage = 'No rephotos were found';
                            } else if (window.location.search.indexOf('myLikes=1') > 0) {
                                categoryMessage = 'No liked pictures were found';
                            } else if (window.location.search.indexOf('dateFrom=') > 0 || window.location.search.indexOf('date=') > 0) {
                                categoryMessage = 'No pictures were found in date range';
                            } else {
                                categoryMessage = 'No pictures were found';
                            }
                            message = categoryMessage + message;
                        }
                        message = gettext(message);
                        if (query) {
                            message = interpolate(message, { query: decodeURI(query) }, true);
                        }
                        message = message.split('\n');
                        targetDiv.append(
                            tmpl('ajp-frontpage-photo-search-empty-template', message),
                        );

                        targetDiv.addClass('w-100');
                        targetDiv.height(window.innerHeight);
                        historicPhotoGalleryDiv
                            .removeClass('d-none')
                            .removeClass('justified-gallery');
                    }
                    if (response.videos) {
                        $.each(response.videos, function(k, v) {
                            targetDiv.append(tmpl('ajp-frontpage-video-template', v));
                        });
                    }
                    if (response.photos.length > 0) {
                        for (let i = 0, l = response.photos.length; i < l; i += 1) {
                            targetDiv.append(
                                tmpl('ajp-frontpage-photo-template', response.photos[i]),
                            );
                        }
                        historicPhotoGalleryDiv.justifiedGallery();
                    }
                    if (
                        response.videos &&
                        response.videos.length > 0 &&
                        response.photos.length === 0
                    ) {
                        historicPhotoGalleryDiv.justifiedGallery();
                    }
                    $('#ajp-loading-overlay').hide();
                    $(window).scrollTop(0);
                },
                error: function() {
                    $('#ajp-loading-overlay').hide();
                },
            });
        };
        if (getQueryParameterByName('q')) {
            const query = getQueryParameterByName('q');
            $('#ajp-album-filter-box')
                .val(
                    decodeURIComponent(query)
                        .replace('%2C', ',')
                        .replace('%3A', ':')
                        .replace('%2F', '/')
                        .replace('+', ' '),
                )
                .trigger('change');
            $('#ajp-photo-filter-box').val(
                decodeURIComponent(query)
                    .replace('%2C', ',')
                    .replace('%3A', ':')
                    .replace('%2F', '/')
                    .replace('+', ' '),
            );
            window.photoQuery = query;
            window.albumQuery = query;
        }
        updateModeSelection();
        window.updateLeaderboard();
        // Local implementations for common functionality
        window.handleAlbumChange = function() {
            window.location.href = '/?album=' + window.albumId;
        };
        window.startSuggestionLocation = function(photoId) {
            let id = photoId ?? window.currentlyOpenPhotoId;
            if (window.albumId) {
                window.open(
                    '/geotag/?album=' + window.albumId + '&photo=' + id,
                    '_blank',
                );
            } else {
                window.open('/geotag/?photo=' + id, '_blank');
            }
        };
        window.stopSuggestionLocation = function() {
            $('#ajp-geotagging-container').hide();
            $('#ajp-frontpage-container').show();
            $('#ajp-photo-modal').show();
            $('html').removeClass('ajp-html-game-map');
            $('body').addClass('ajp-body-frontpage').removeClass('ajp-body-game-map');
            $('.modal-backdrop').show();
            $('.footer').show();
            const currentUrl = window.URI(window.location.href),
                selectedPhoto = window.currentlySelectedPhotoId;
            currentUrl.removeSearch('photo');
            window.currentlySelectedPhotoId = null;
            window.history.replaceState(null, window.title, currentUrl);
            window.updateFrontpagePhotosAsync();
            window.locationToolsOpen = false;
            window.currentlySelectedPhotoId = selectedPhoto;
            syncStateToUrl();
            if (window.startSuggestionScrollTop) {
                setTimeout(function() {
                    $(window).scrollTop(window.startSuggestionScrollTop);
                    window.startSuggestionScrollTop = null;
                }, 1000);
            }
        };
        window.loadPhoto = function(id) {
            window.nextPhotoLoading = true;
            window.photoModalPhotoLat = null;
            window.photoModalPhotoLng = null;
            window.photoModalPhotoAzimuth = null;
            $.ajax({
                cache: false,
                url: '/photo/' + id + '/?isFrontpage=1',
                success: function(result) {
                    window.nextPhotoLoading = false;
                    openPhotoDrawer(result);
                    window.currentlySelectedPhotoId = id;
                    syncStateToUrl();
                    const imgContainer = $('#ajp-frontpage-image-container-' + id),
                        nextId = imgContainer.next().data('id'),
                        previousId = imgContainer.prev().data('id'),
                        nextButton = $('.ajp-photo-modal-next-button'),
                        previousButton = $('.ajp-photo-modal-previous-button'),
                        originalPhotoColumn = $('#ajp-photo-modal-original-photo-column'),
                        originalPhotoInfoColumn = $(
                            '#ajp-photo-modal-original-photo-info-column',
                        ),
                        rephotoColumn = $('#ajp-photo-modal-rephoto-column'),
                        similarPhotoColumn = $('#ajp-photo-modal-similar-photo-column');

                    window.currentPhotoReverseId = $('#ajp-reverse-side-button').data(
                        'id',
                    );
                    fullScreenImage = $('#ajp-fullscreen-image');
                    if (fullScreenImage) {
                        fullScreenImage
                            .attr('src', window.photoModalFullscreenImageUrl)
                            .attr('data-src', window.photoModalFullscreenImageUrl)
                            .attr('alt', window.currentPhotoDescription);
                    }
                    if (!nextId) {
                        nextButton.addClass('ajp-photo-modal-next-button-disabled');
                    } else {
                        nextButton.removeClass('ajp-photo-modal-next-button-disabled');
                    }
                    if (!previousId) {
                        previousButton.addClass('ajp-photo-modal-previous-button-disabled');
                    } else {
                        previousButton.removeClass(
                            'ajp-photo-modal-previous-button-disabled',
                        );
                    }
                    if (window.photoHistory && window.photoHistory.length > 0) {
                        previousButton.removeClass('disabled');
                    }
                    if (window.userClosedRephotoTools) {
                        $('#ajp-rephoto-selection').hide();
                        rephotoColumn.hide();
                        $('#ajp-photo-rephoto-info-column').hide();
                    }
                    if (window.userClosedSimilarPhotoTools) {
                        $('#ajp-similar-photo-selection').hide();
                        similarPhotoColumn.hide();
                        $('#ajp-photo-modal-similar-photo-info-column').hide();
                    }
                    if (
                        window.userClosedRephotoTools &&
                        window.userClosedSimilarPhotoTools
                    ) {
                        $('#ajp-photo-modal-map-container').show();
                        if (!window.photoModalPhotoLat && !window.photoModalPhotoLng) {
                            originalPhotoColumn.removeClass('col-lg-6').addClass('col-lg-12');
                            originalPhotoInfoColumn
                                .removeClass('col-lg-6')
                                .addClass('col-lg-12');
                        }
                    }
                    if (
                        (!window.photoModalPhotoLat && !window.photoModalPhotoLng) ||
                        (window.photoModalRephotoArray.length > 0 &&
                            !window.userClosedRephotoTools) ||
                        (window.photoModalSimilarPhotoArray.length > 0 &&
                            !window.userClosedSimilarPhotoTools)
                    ) {
                        $('#ajp-photo-modal-map-container').hide();
                    }
                    if (
                        window.photoModalRephotoArray &&
                        window.photoModalRephotoArray[0] &&
                        window.photoModalRephotoArray[0][2] != 'None' &&
                        window.photoModalRephotoArray[0][2] != ''
                    ) {
                        $('#ajp-photo-modal-date-row').show();
                    }
                },
                error: function() {
                    window.nextPhotoLoading = false;
                },
            });
            let fullscreenImageWrapper = $('#ajp-fullscreen-image-wrapper');
            fullscreenImageWrapper.removeClass('rotate90');
            fullscreenImageWrapper.removeClass('rotate180');
            fullscreenImageWrapper.removeClass('rotate270');
        };
        window.handleGeolocation = function(location) {
            if (window.clickedMapButton) {
                $('#ajp-geolocation-error').hide();
                window.location.href =
                    '/map?lat=' +
                    location.coords.latitude +
                    '&lng=' +
                    location.coords.longitude +
                    '&limitToAlbum=0&zoom=15';
            } else {
                $('#ajp-geolocation-error').hide();
                window.userLat = location.coords.latitude;
                window.userLon = location.coords.longitude;
                syncStateToUrl();
                syncFilteringHighlights();
                window.updateFrontpagePhotosAsync();
            }
        };
        window.closePhotoDrawer = function() {
            $('#ajp-photo-modal').modal('hide');
        };
        window.uploadCompleted = function() {
            $('#ajp-rephoto-upload-modal').modal('hide');
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
        photoModal
            .on('shown.bs.modal', function() {
                gtag('event', 'open_photo_modal', {
                    'category': 'Gallery',
                });
                syncStateToUrl();
                if (window.straightToSpecify) {
                    window.straightToSpecify = false;
                    $('#ajp-photo-modal-specify-location').click();
                    $('.modal-backdrop').hide();
                }
            })
            .on('hidden.bs.modal', function() {
                window.currentlySelectedPhotoId = null;
                syncStateToUrl();
                if (window.nextPageOnModalClose) {
                    window.nextPageOnModalClose = false;
                    window.setTimeout(function() {
                        $('#ajp-paging-next-button').click();
                    }, 1500);
                } else if (window.previousPageOnModalClose) {
                    window.previousPageOnModalClose = false;
                    if (window.currentPage > 1) {
                        window.setTimeout(function() {
                            $('#ajp-paging-previous-button').click();
                        }, 1500);
                    }
                }
                if (window.currentVideoId) {
                    $('#ajp-video-modal').show();
                }
                $('#ajp-fullscreen-image-wrapper').removeClass('ajp-photo-flipped');
            });
        $(document).on('click', '.ajp-frontpage-image-container', function(e) {
            e.preventDefault();
        });
        albumSelectionDiv
            .justifiedGallery(historicPhotoGallerySettings)
            .on('jg.complete', function() {
                albumSelectionDiv.removeClass('ajp-invisible');
                $('.footer').removeClass('ajp-invisible');
            });
        historicPhotoGalleryDiv
            .justifiedGallery(historicPhotoGallerySettings)
            .on('jg.complete', function() {
                historicPhotoGalleryDiv.removeClass('ajp-invisible');
                $('.footer').removeClass('ajp-invisible');
            });
        $(document).on('click', '.ajp-frontpage-image', function() {
            hideScoreboard();
            window.loadPhoto($(this).data('id'));
        });

        $(document).on('click', '#ajp-paging-previous-button', function(e) {
            e.preventDefault();
            if (window.currentPage > 1) {
                window.currentPage -= 1;
                syncStateToUrl();
                if (window.showPhotos) {
                    window.updateFrontpagePhotosAsync();
                } else {
                    updateFrontpageAlbumsAsync();
                }
            }
        });
        $(document).on('click', '.ajp-album-selection-map-button', function(e) {
            e.preventDefault();
            e.stopPropagation();
            window.location.href = $(this).attr('data-href');
        });
        $(document).on('click', '.ajp-album-selection-game-button', function(e) {
            e.preventDefault();
            e.stopPropagation();
            window.location.href = $(this).attr('data-href');
        });
        $('#ajp-mode-select')
            .find('a')
            .click(function(e) {
                e.preventDefault();
                let $this = $(this),
                    selectedMode = $this.data('mode');
                if ($this.hasClass('disabled')) {
                    return false;
                }
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
                let currentUrl = window.URI(window.location.href);
                currentUrl.removeSearch('photos');
                window.showPhotos = true;
                const ajpHeaderCollections = $('#ajp-header-collections');
                switch (selectedMode) {
                    case 'pictures':
                        ajpHeaderCollections.addClass('d-none');
                        window.history.replaceState(null, window.title, currentUrl);
                        break;
                    case 'albums':
                        ajpHeaderCollections.removeClass('d-none');
                        if (window.albumId) {
                            window.location.href = '/';
                        }
                        window.showPhotos = false;
                        window.history.replaceState(null, window.title, currentUrl);
                        window.order1 = null;
                        window.order2 = null;
                        window.order3 = null;
                        break;
                    case 'likes':
                        ajpHeaderCollections.addClass('d-none');
                        window.myLikes = true;
                        break;
                    case 'rephotos':
                        ajpHeaderCollections.addClass('d-none');
                        window.rephotosBy = window.currentProfileId;
                        window.rephotosByName = window.currentProfileName;
                        break;
                }
                updateModeSelection();
            });
        $(document).on(
            'change textInput input',
            '#ajp-album-filter-box',
            function() {
                doDelayedAlbumFiltering(this.value.toLowerCase());
            },
        );
        $(document).on(
            'change textInput input',
            '#ajp-photo-filter-box',
            function() {
                doDelayedPhotoFiltering($(this).val());
            },
        );
        $(document).on('click', '#ajp-paging-next-button', function(e) {
            e.preventDefault();
            if (window.currentPage < window.maxPage) {
                window.currentPage += 1;
                syncStateToUrl();
                if (window.showPhotos) {
                    window.updateFrontpagePhotosAsync();
                } else {
                    updateFrontpageAlbumsAsync();
                }
            }
        });
        window.addEventListener('load', function() {
            setTimeout(function() {
                window.addEventListener('popstate', function() {
                    window.location.reload();
                });
            }, 0);
        });
        $(document).on('click', '.ajp-frontpage-album', function(e) {
            e.preventDefault();
            const $this = $(this);
            if (
                window.isMobile &&
                window.albumWithOneClickDone != $this.attr('data-id')
            ) {
                window.albumWithOneClickDone = $this.attr('data-id');
                $this.find('.ajp-album-selection-caption-bottom').removeClass('d-none');
            } else {
                gtag('event', $('#ajp-album-filter-box').val() ? 'album_click_with_search_term' : 'album_click', {
                    'category': 'Gallery',
                });
                window.location.href = $this.attr('href');
            }
        });
        $(document).on('click', '.ajp-filtering-choice', function(e) {
            e.stopPropagation();
            e.preventDefault();
            window.currentPage = 1;
            const $this = $(this);
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
                    window.getGeolocation(
                        window.handleGeolocation,
                        window.geolocationError,
                    );
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
})(jQuery);
