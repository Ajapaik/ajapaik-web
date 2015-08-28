(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global console */
    /*global loadAlbumURL */
    /*global favoriteAddURL */
    /*global favoriteRemoveURL */
    /*global tagURL */
    /*global docCookies */
    window.CatTagger = function () {
        this.selectedAlbumId = null;
        this.selectedAlbumTitle = null;
        this.selectedAlbumSubtitle = null;
        this.loadAlbumURL = loadAlbumURL;
        this.addFavoriteURL = favoriteAddURL;
        this.removeFavoriteURL = favoriteRemoveURL;
        this.tagURL = tagURL;
        this.currentPhotoIndex = -1;
        this.currentPhoto = null;
        this.currentPhotoTagIndex = -1;
        this.photos = null;
    };
    window.CatTagger.prototype = {
        switchToTaggingView: function () {
            $('#cat-album-selection').parent().addClass('hidden');
            $('#cat-tagger-container').removeClass('hidden');
            $('#cat-tagger-current-album-title').html(this.selectedAlbumTitle);
            $('#cat-tagger-current-album-subtitle').html(this.selectedAlbumSubtitle);
        },
        switchToAlbumSelection: function () {
            this.selectedAlbumId = null;
            this.selectedAlbumTitle = null;
            this.selectedAlbumSubtitle = null;
            $('#cat-album-selection').parent().removeClass('hidden');
            $('#cat-tagger-container').addClass('hidden');
        },
        nextPhoto: function () {
            this.currentPhotoIndex += 1;
            this.currentPhotoTagIndex = -1;
            this.currentPhoto = this.photos[this.currentPhotoIndex];
            $('#cat-tagger-current-photo').attr('src', this.currentPhoto.image.replace('[DIM]', '800'));
            $('#cat-tagger-photo-description').html(this.currentPhoto.title).addClass('hidden');
            this.updateFavoriteButton();
            this.nextTag();
        },
        updateFavoriteButton: function () {
            var favoriteButton = $('#cat-tagger-favorite-button');
            if (this.currentPhoto.is_user_favorite) {
                favoriteButton.addClass('active');
            } else {
                favoriteButton.removeClass('active');
            }
        },
        nextTag: function () {
            this.currentPhotoTagIndex += 1;
            if (this.currentPhotoTagIndex > 1) {
                this.nextPhoto();
            } else {
                var currentTag = this.currentPhoto.tag[this.currentPhotoTagIndex],
                    parts = currentTag.split('_');
                $('#cat-tagger-left').html(this.allTags[currentTag].leftIcon).parent().attr('data-tag', currentTag);
                $('#cat-tagger-left-text').html(parts[0].capitalize());
                $('#cat-tagger-right').html(this.allTags[currentTag].rightIcon).parent().attr('data-tag', currentTag);
                $('#cat-tagger-right-text').html(parts[(parts.length - 1)].capitalize());
                $('#cat-tagger-na').parent().attr('data-tag', currentTag);
            }
        },
        loadAlbum: function () {
            var loadingOverlay = $('#ajapaik-loading-overlay'),
                that = this;
            loadingOverlay.show();
            $.ajax({
                url: this.loadAlbumURL,
                data: {
                    id: this.selectedAlbumId,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                method: 'POST',
                success: function (response) {
                    if (parseInt(response.error, 10) === 0) {
                        loadingOverlay.hide();
                        that.photos = response.photos;
                        that.selectedAlbumTitle = response.title;
                        that.selectedAlbumSubtitle = response.subtitle;
                        that.switchToTaggingView();
                        that.nextPhoto();
                    }
                },
                error: function () {
                    console.log('Error getting album data');
                    loadingOverlay.hide();
                }
            });
        },
        initialize: function () {
            var that = this;
            $('#cat-album-selection').justifiedGallery({
                rowHeight: 270,
                margins: 5,
                captions: false
            });
            $('.cat-album-selection-element').click(function (e) {
                e.preventDefault();
                var $this = $(this);
                that.selectedAlbumId = $this.data('id');
                that.selectedAlbumTitle = $this.data('title');
                that.loadAlbum();
            });
            $('#cat-tagger-info-button').click(function () {
                var target = $('#cat-tagger-photo-description');
                if (target.hasClass('hidden')) {
                    target.removeClass('hidden');
                } else {
                    target.addClass('hidden');
                }
            });
            $('#cat-tagger-favorite-button').click(function () {
                var $this = $(this),
                    url;
                if ($this.hasClass('active')) {
                    url = that.removeFavoriteURL;
                } else {
                    url = that.addFavoriteURL;
                }
                $.ajax({
                    url: url,
                    data: {
                        album: that.selectedAlbumId,
                        photo: that.currentPhoto.id,
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    method: 'POST',
                    success: function (response) {
                        if (parseInt(response.error, 10) === 0) {
                            that.currentPhoto.is_user_favorite = true;
                            that.updateFavoriteButton();
                        }
                    },
                    error: function () {
                        console.log('Error saving favorite');
                    }
                });
            });
            $('.cat-tagger-tag-button').click(function () {
                var $this = $(this);
                $.ajax({
                    url: that.tagURL,
                    data: {
                        id: that.selectedAlbumId,
                        photo: that.currentPhoto.id,
                        tag: $this.data('tag'),
                        value: $this.data('value'),
                        source: 'web',
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    method: 'POST',
                    success: function (response) {
                        if (parseInt(response.error, 10) === 0) {
                            that.nextTag();
                        }
                    },
                    error: function () {
                        console.log('Error saving tag');
                    }
                });
            });
        },
        initializeState: function (state) {
            if (state.albumId) {
                this.selectedAlbumId = state.albumId;
                this.selectedAlbumTitle = state.albumName;
                this.switchToTaggingView();
            } else {
                this.switchToAlbumSelection();
            }
            this.allTags = state.allTags;
        }
    };
}());