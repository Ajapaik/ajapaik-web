(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global URI */
    /*global getPhotosURL */
    /*global taggerURL */
    /*global tmpl */
    /*global console */
    window.Cat = function () {
        this.selectedAlbumId = null;
        this.selectedAlbumTitle = null;
        this.getPhotosURL = getPhotosURL;
        this.taggerURL = taggerURL;
        this.photoLoadTimeout = null;
        this.page = 0;
        this.currentResultSetStart = null;
        this.currentResultSetEnd = null;
        this.totalResults = 0;
        this.filterNames = [];
    };
    window.Cat.prototype = {
        switchToAlbumSelection: function () {
            this.selectedAlbumId = null;
            this.selectedAlbumTitle = null;
            this.page = 0;
            this.removeFiltersFromURL();
            this.updatePaging();
            this.syncStateToURL();
            $('#cat-header-showing-albums').removeClass('hidden');
            $('#cat-header-showing-pictures').addClass('hidden');
            $('#cat-header-showing-album-pictures').addClass('hidden');
            $('#cat-album-selection').removeClass('hidden').parent().removeClass('col-xs-7 col-sm-8 col-lg-9');
            $('#cat-photo-view').addClass('hidden');
            $('#cat-filtering-panel').addClass('hidden');
            $('#cat-pager').addClass('hidden');
        },
        switchToPhotoView: function () {
            this.loadPhotos();
            $('#cat-header-showing-albums').addClass('hidden');
            var showingAlbumPictures = $('#cat-header-showing-album-pictures');
            if (this.selectedAlbumId) {
                showingAlbumPictures.removeClass('hidden').find('span')
                    .html(this.selectedAlbumTitle);
            } else {
                $('#cat-header-showing-pictures').removeClass('hidden');
                showingAlbumPictures.addClass('hidden');
            }
            $('#cat-pager').removeClass('hidden');
            $('#cat-album-selection').addClass('hidden').parent().addClass('col-xs-7 col-sm-8 col-lg-9');
            $('#cat-photo-view').removeClass('hidden');
            $('#cat-filtering-panel').removeClass('hidden');
        },
        removeFiltersFromURL: function () {
            var i,
                l = this.filterNames.length,
                currentURL = URI(location.href);
            for (i = 0; i < l; i += 1) {
                currentURL.removeSearch(this.filterNames[i]);
            }
            history.replaceState(null, window.title, currentURL);
        },
        syncStateToURL: function () {
            var currentURL = URI(location.href);
            currentURL.removeSearch('album').removeSearch('page');
            if (this.selectedAlbumId) {
                currentURL.addSearch('album', this.selectedAlbumId);
            }
            if (this.page) {
                currentURL.addSearch('page', this.page);
            }
            history.replaceState(null, window.title, currentURL);
        },
        loadPhotos: function () {
            var that = this;
            $.ajax({
                url: this.getPhotosURL + location.search,
                method: 'GET',
                success: function (response) {
                    var i,
                        l = response.photos.length,
                        targetDiv = $('#cat-photo-view');
                    that.currentResultSetStart = response.currentResultSetStart;
                    that.currentResultSetEnd = response.currentResultSetEnd;
                    that.totalResults = response.totalResults;
                    that.updateResultSetStats();
                    targetDiv.empty();
                    for (i = 0; i < l; i += 1) {
                        targetDiv.append(tmpl('cat-results-photo-template', response.photos[i]));
                    }
                    targetDiv.justifiedGallery();
                },
                error: function () {
                    console.log('Error getting photos');
                }
            });
        },
        updatePaging: function () {
            $('#cat-pager-page').html(this.page);
        },
        updateResultSetStats: function () {
            $('#cat-result-set-stats').html(this.currentResultSetStart + ' - ' + this.currentResultSetEnd + ' / ' + this.totalResults);
        },
        initializeFilterBox: function () {
            $('.cat-filtering-checkbox').attr('checked', false);
            $('.cat-filtering-button').removeClass('active');
        },
        delayedLoadPhotos: function () {
            var that = this;
            if (that.photoLoadTimeout) {
                clearTimeout(that.photoLoadTimeout);
            }
            that.photoLoadTimeout = setTimeout(function () {
                that.loadPhotos();
            }, 1000);
        },
        initialize: function () {
            var that = this;
            $('#cat-album-selection').justifiedGallery({
                rowHeight: 270,
                margins: 5,
                captions: false
            });
            $('#cat-photo-view').justifiedGallery({
                rowHeight: 270,
                margins: 5,
                captions: false,
                waitThumbnailsLoad: false
            });
            $('.cat-album-selection-element').click(function (e) {
                e.preventDefault();
                var $this = $(this);
                that.selectedAlbumId = $this.data('id');
                that.selectedAlbumTitle = $this.data('title');
                that.page = 0;
                that.initializeFilterBox();
                that.removeFiltersFromURL();
                that.syncStateToURL();
                that.switchToPhotoView();
            });
            $('.cat-filtering-checkbox').change(function () {
                var currentURL = URI(location.href);
                if (this.checked) {
                    currentURL.addSearch(this.name, this.value);
                } else {
                    currentURL.removeSearch(this.name, this.value);
                }
                that.page = 0;
                currentURL.removeSearch('page').addSearch('page', that.page);
                that.updatePaging();
                history.replaceState(null, window.title, currentURL);
                that.delayedLoadPhotos();
            });
            $('#cat-pager-previous').click(function (e) {
                e.preventDefault();
                if (that.page > 0) {
                    that.page -= 1;
                    that.updatePaging();
                    that.syncStateToURL();
                    that.delayedLoadPhotos();
                }
            });
            $('#cat-pager-next').click(function (e) {
                e.preventDefault();
                that.page += 1;
                $('#cat-pager-page').html(that.page);
                that.syncStateToURL();
                that.delayedLoadPhotos();
            });
            $('#cat-show-albums-link').click(function () {
                that.updatePaging();
                that.switchToAlbumSelection();
            });
            $('#cat-show-pictures-link').click(function () {
                that.selectedAlbumId = null;
                that.selectedAlbumTitle = null;
                that.page = 0;
                that.removeFiltersFromURL();
                that.initializeFilterBox();
                that.updatePaging();
                that.syncStateToURL();
                that.switchToPhotoView();
            });
            $('#cat-header-tag-link').click(function () {
                if (that.selectedAlbumId) {
                    location.href = that.taggerURL + '?album=' + that.selectedAlbumId;
                } else {
                    location.href = that.taggerURL;
                }
            });
        },
        initializeState: function (state) {
            if (state.albumId || state.showPictures) {
                this.selectedAlbumId = state.albumId;
                this.selectedAlbumTitle = state.albumName;
                this.switchToPhotoView();
            } else {
                this.switchToAlbumSelection();
            }
            this.page = state.page;
            this.filterNames = state.filterNames;
            this.currentResultSetStart = state.currentResultSetStart;
            this.currentResultSetEnd = state.currentResultSetEnd;
        }
    };
}());