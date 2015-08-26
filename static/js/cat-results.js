(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global URI */
    /*global getPhotosURL */
    /*global tmpl */
    window.Cat = function () {
        this.selectedAlbumId = null;
        this.getPhotosURL = getPhotosURL;
        this.photoLoadTimeout = null;
    };
    window.Cat.prototype = {
        switchToAlbumSelection: function () {
            this.selectedAlbumId = null;
            this.syncStateToURL();
            $('#cat-header-showing-albums').removeClass('hidden');
            $('#cat-header-showing-pictures').addClass('hidden');
            $('#cat-album-selection').removeClass('hidden');
            $('#cat-photo-view').addClass('hidden');
        },
        switchToPhotoView: function () {
            this.syncStateToURL();
            this.loadPhotos();
            $('#cat-header-showing-albums').addClass('hidden');
            $('#cat-header-showing-pictures').removeClass('hidden');
            $('#cat-album-selection').addClass('hidden');
            $('#cat-photo-view').removeClass('hidden');
        },
        syncStateToURL: function () {
            var currentURL = URI(location.href);
            if (this.selectedAlbumId) {
                currentURL.removeSearch('album').addSearch('album', this.selectedAlbumId);
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
                    console.log('error');
                }
            });
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
                captions: false
            });
            $('.cat-album-selection-element').click(function (e) {
                e.preventDefault();
                that.selectedAlbumId = $(this).data('id');
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
        },
        initializeState: function (state) {
            if (state.albumId || state.showPictures) {
                this.switchToPhotoView();
            } else {
                this.switchToAlbumSelection();
            }
        }
    };
}());