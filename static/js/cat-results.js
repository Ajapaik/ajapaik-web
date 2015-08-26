(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global URI */
    /*global getPhotosURL */
    /*global tmpl */
    /*global console */
    window.Cat = function () {
        this.selectedAlbumId = null;
        this.selectedAlbumTitle = null;
        this.getPhotosURL = getPhotosURL;
        this.photoLoadTimeout = null;
        this.page = 0;
    };
    window.Cat.prototype = {
        switchToAlbumSelection: function () {
            this.selectedAlbumId = null;
            this.selectedAlbumTitle = null;
            this.page = 0;
            this.updatePaging();
            this.syncStateToURL();
            $('#cat-header-showing-albums').removeClass('hidden');
            $('#cat-header-showing-pictures').addClass('hidden');
            $('#cat-header-showing-album-pictures').addClass('hidden');
            $('#cat-album-selection').removeClass('hidden');
            $('#cat-photo-view').addClass('hidden');
            $('#cat-filtering-panel').addClass('hidden');
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
            $('#cat-album-selection').addClass('hidden');
            $('#cat-photo-view').removeClass('hidden');
            $('#cat-filtering-panel').removeClass('hidden');
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
            $.ajax({
                url: this.getPhotosURL + location.search,
                method: 'GET',
                success: function (response) {
                    var i,
                        l = response.length,
                        targetDiv = $('#cat-photo-view');
                    targetDiv.empty();
                    for (i = 0; i < l; i += 1) {
                        targetDiv.append(tmpl('cat-results-photo-template', response[i]));
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
                that.updatePaging();
                that.syncStateToURL();
                that.switchToPhotoView();
            });
            $('.cat-results-photo-container').click(function (e) {
                e.preventDefault();
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
        }
    };
}());