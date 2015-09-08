(function () {
    'use strict';
    /*jslint nomen: true*/
    /*global $ */
    /*global loadAlbumURL */
    /*global getAlbumsURL */
    /*global favoriteAddURL */
    /*global favoriteRemoveURL */
    /*global URI */
    /*global tagURL */
    /*global filterURL */
    /*global gettext */
    /*global docCookies */
    /*global _gaq */
    /*global tmpl */
    /*global originalWindowTitle */
    window.CatTagger = function () {
        this.selectedAlbumId = null;
        this.selectedAlbumTitle = null;
        this.loadAlbumURL = loadAlbumURL;
        this.getAlbumsURL = getAlbumsURL;
        this.addFavoriteURL = favoriteAddURL;
        this.removeFavoriteURL = favoriteRemoveURL;
        this.filterURL = filterURL;
        this.tagURL = tagURL;
        this.currentPhotoIndex = -1;
        this.currentPhoto = null;
        this.currentPhotoTagIndex = -1;
        this.photos = null;
        this.originalWindowTitle = originalWindowTitle;
    };
    window.CatTagger.prototype = {
        switchToTaggingView: function () {
            $('#cat-album-selection').parent().addClass('hidden');
            $('#cat-tagger-container').removeClass('hidden');
            $('#cat-header-showing-album-pictures').removeClass('hidden').find('span').html(this.selectedAlbumTitle);
            $('#cat-header-showing-albums').addClass('hidden');
        },
        switchToAlbumSelection: function () {
            this.loadAlbums();
            this.selectedAlbumId = null;
            this.selectedAlbumTitle = null;
            $('#cat-album-selection').parent().removeClass('hidden');
            $('#cat-tagger-container').addClass('hidden');
            $('#cat-header-showing-album-pictures').addClass('hidden');
            $('#cat-header-showing-albums').removeClass('hidden');
            this.syncStateToURL();
        },
        nextPhoto: function () {
            this.currentPhotoIndex += 1;
            this.currentPhotoTagIndex = -1;
            this.currentPhoto = this.photos[this.currentPhotoIndex];
            $('#cat-tagger-current-photo').attr('src', this.currentPhoto.image.replace('[DIM]', '800'));
            $('#cat-tagger-current-photo-link').attr('href', this.currentPhoto.source.url)
                .attr('data-id', this.currentPhoto.id);
            $('#cat-tagger-favorite-button').attr('data-id', this.currentPhoto.id);
            $('#cat-tagger-info-button').attr('data-id', this.currentPhoto.id);
            $('#cat-tagger-photo-description-container').addClass('hidden');
            $('#cat-tagger-photo-description').html(this.currentPhoto.title);
            var sourceDiv = $('#cat-tagger-photo-source');
            sourceDiv.find('a').attr('href', this.currentPhoto.source.url).find('span').html(this.currentPhoto.source.name);
            this.updateFavoriteButton();
        },
        updateFavoriteButton: function () {
            var favoriteButton = $('#cat-tagger-favorite-button');
            if (this.currentPhoto.is_user_favorite) {
                favoriteButton.find('i').html('favorite');
            } else {
                favoriteButton.find('i').html('favorite_outline');
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
                $('#cat-tagger-left-text').html(gettext((parts[0].toString().capitalizeFirstLetter())));
                $('#cat-tagger-right').html(this.allTags[currentTag].rightIcon).parent().attr('data-tag', currentTag);
                $('#cat-tagger-right-text').html(gettext(parts[(parts.length - 1)].capitalizeFirstLetter()));
                $('#cat-tagger-na').parent().attr('data-tag', currentTag);
            }
        },
        syncStateToURL: function () {
            var currentURL = URI(location.href),
                replacementTitle = originalWindowTitle;
            currentURL.removeSearch('album');
            if (this.selectedAlbumId) {
                currentURL.addSearch('album', this.selectedAlbumId);
                replacementTitle = this.selectedAlbumTitle + ' - ' + this.originalWindowTitle;
            }
            document.title = replacementTitle;
            history.replaceState(null, window.title, currentURL);
        },
        reportTaggingError: function () {
            _gaq.push(['_trackEvent', 'tagging', 'error', 'tag', -1000, true]);
        },
        reportAlbumLoadError: function () {
            _gaq.push(['_trackEvent', 'tagging', 'error', 'album', -1000, true]);
        },
        reportFavoritingError: function () {
            _gaq.push(['_trackEvent', 'tagging', 'error', 'favorite', -1000, true]);
        },
        reportImageLoadError: function () {
            _gaq.push(['_trackEvent', 'tagging', 'error', 'image', -1000, true]);
        },
        reportAlbumsLoadError: function () {
            _gaq.push(['_trackEvent', 'tagging', 'error', 'albums', -1000, true]);
        },
        loadAlbums: function () {
            var that = this;
            $.ajax({
                url: that.getAlbumsURL,
                data: {
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                method: 'POST',
                success: function (response) {
                    if (parseInt(response.error, 10) === 0) {
                        var i,
                            l = response.albums.length,
                            targetDiv = $('#cat-album-selection'),
                            fmt = gettext('%(users)s users have made %(decisions)s decisions about %(pictures)s pictures. You are contributor number %(rank)s.'),
                            statString = interpolate(fmt, {
                                users: response.stats.users,
                                decisions: response.stats.decisions,
                                pictures: response.stats.tagged,
                                rank: response.stats.rank
                            }, true);
                        $('#cat-footer-text').html(statString).show();
                        targetDiv.empty();
                        for (i = 0; i < l; i += 1) {
                            targetDiv.append(tmpl('cat-album-selection-album-template', response.albums[i]));
                        }
                        targetDiv.justifiedGallery();
                    } else {
                        that.reportAlbumsLoadError();
                    }
                },
                error: function () {
                    that.reportAlbumsLoadError();
                }
            });
        },
        loadAlbum: function () {
            var loadingOverlay = $('#cat-loading-overlay'),
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
                        that.syncStateToURL();
                        loadingOverlay.hide();
                        that.photos = response.photos;
                        that.selectedAlbumTitle = response.title;
                        that.switchToTaggingView();
                        that.nextPhoto();
                        $('#cat-footer-text').hide();
                    } else {
                        that.reportAlbumLoadError();
                    }
                },
                error: function () {
                    that.reportAlbumLoadError();
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
            $(document).on('click', '.cat-album-selection-element', function (e) {
                e.preventDefault();
                var $this = $(this);
                that.selectedAlbumId = $this.data('id');
                that.selectedAlbumTitle = $this.data('title');
                that.loadAlbum();
            });
            $('#cat-tagger-info-button').click(function () {
                $('#cat-tagger-photo-description-container').toggleClass('hidden');
            });
            $('#cat-tagger-favorite-button').click(function () {
                var $this = $(this),
                    url,
                    remove = false;
                if ($this.hasClass('active')) {
                    url = that.removeFavoriteURL;
                    remove = true;
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
                            that.currentPhoto.is_user_favorite = !remove;
                            that.updateFavoriteButton();
                        } else {
                            that.reportFavoritingError();
                        }
                    },
                    error: function () {
                        that.reportFavoritingError();
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
                        } else {
                            that.reportTaggingError();
                        }
                    },
                    error: function () {
                        that.reportTaggingError();
                    }
                });
            });
            $('#cat-tagger-current-photo').load(function () {
                that.nextTag();
            }).error(function () {
                that.reportImageLoadError();
            });
            $('#cat-show-albums-link').click(function () {
                that.switchToAlbumSelection();
            });
            $('.cat-header-filter-link').click(function () {
                if (that.selectedAlbumId) {
                    location.href = that.filterURL + '?album=' + that.selectedAlbumId;
                } else {
                    location.href = that.filterURL;
                }
            });
        },
        initializeState: function (state) {
            if (state.albumId) {
                this.selectedAlbumId = state.albumId;
                this.selectedAlbumTitle = state.albumName;
                this.loadAlbum();
                this.switchToTaggingView();
            } else {
                this.switchToAlbumSelection();
            }
            this.allTags = state.allTags;
        }
    };
}());