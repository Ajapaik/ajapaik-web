(function () {
    'use strict';
    /*global BigScreen*/
    /*global fullScreenWidth*/
    /*global fullScreenHeight*/
    /*global favoriteRemoveURL*/
    /*global favoriteAddURL*/
    /*global albumId*/
    /*global photoId*/
    /*global docCookies*/
    /*global isUserFavorite*/
    /*global _gaq*/
    /*global taggerURL*/
    /*global filterURL*/
    /*global reportPermalinkFavoritingError */
    var fullScreenElement = $('#cat-permalink-full-screen-image'),
        prepareFullScreen = function () {
            var image = fullScreenElement,
                aspectRatio = fullScreenWidth / fullScreenHeight,
                newWidth = parseInt(screen.height * aspectRatio, 10),
                newHeight = parseInt(screen.width / aspectRatio, 10);
            if (newWidth > screen.width) {
                newWidth = screen.width;
            } else {
                newHeight = screen.height;
            }
            image.css('margin-left', (screen.width - newWidth) / 2 + 'px');
            image.css('margin-top', (screen.height - newHeight) / 2 + 'px');
            image.css('width', newWidth);
            image.css('height', newHeight);
            image.css('opacity', 1);
        };
    $('.cat-header-tag-link').click(function () {
        location.href = taggerURL;
    });
    $('.cat-header-filter-link').click(function () {
        location.href = filterURL;
    });
    $('#cat-permalink-full-screen-link').click(function (e) {
        e.preventDefault();
        if (BigScreen.enabled) {
            fullScreenElement.attr('src', fullScreenElement.attr('data-src')).load(function () {
                prepareFullScreen();
            });
            BigScreen.request(fullScreenElement.get(0));
            fullScreenElement.show();
        }
    });
    fullScreenElement.click(function () {
        if (BigScreen.enabled) {
            BigScreen.exit();
        }
    });
    $('#cat-permalink-favorite-button').click(function () {
        var $this = $(this),
            url,
            remove = false;
        if ($this.find('i').html() === 'favorite') {
            url = favoriteRemoveURL;
            remove = true;
        } else {
            url = favoriteAddURL;
        }
        $.ajax({
            url: url,
            data: {
                album: albumId,
                photo: photoId,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            },
            method: 'POST',
            success: function (response) {
                if (parseInt(response.error, 10) === 0) {
                    isUserFavorite = !remove;
                    $('#cat-permalink-like-count').html(response.favoriteCount);
                    if (remove) {
                        $this.find('i').html('favorite_border');
                    } else {
                        $this.find('i').html('favorite');
                    }
                } else {
                    reportPermalinkFavoritingError();
                }
            },
            error: function () {
                reportPermalinkFavoritingError();
            }
        });
    });
}());
