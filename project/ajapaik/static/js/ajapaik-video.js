(function () {
    'use strict';
    /*global docCookies*/
    /*global albumId*/
    /*global loadPhoto*/
    var videoModal = $('#ajapaik-video-modal'),
        doc = $(document),
        stillButton,
        modalVideo,
        currentVideoId,
        onPause = function () {
            stillButton.addClass('enabled').removeClass('disabled');
        },
        onPlay = function () {
            stillButton.removeClass('enabled').addClass('disabled');
        },
        onStill = function () {
            if (!$(this).hasClass('disabled')) {
                $.ajax({
                    url: '/video-still/',
                    method: 'POST',
                    data: {
                        video: currentVideoId,
                        timestamp: parseInt(modalVideo.get(0).currentTime * 1000, 10),
                        album: albumId,
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    success: function (response) {
                        loadPhoto(response.stillId);
                    }
                });
            }
        };
    doc.on('click', '#ajapaik-video-modal-close-button', function (e) {
        e.preventDefault();
        $('#ajapaik-video-modal').modal('toggle');
    });
    doc.on('click', '.ajapaik-frontpage-video-container', function (e) {
        e.preventDefault();
    });
    doc.on('click', '.ajapaik-frontpage-video', function () {
        window.loadVideo($(this).data('id'), $(this).data('slug'));
    });
    doc.on('click', '#ajapaik-video-modal-anonymous-icon', function () {
        $('#ajapaik-header-profile-button').click();
    });
    window.loadVideo = function (id, slug) {
        currentVideoId = id;
        $.ajax({
            cache: false,
            url: '/video/' + id + '/' + slug + '/',
            success: function (result) {
                videoModal.html(result);
                videoModal.modal();
                modalVideo = videoModal.find('#ajapaik-modal-video');
                modalVideo.on('pause', onPause);
                modalVideo.on('play', onPlay);
                stillButton = videoModal.find('#ajapaik-video-modal-still-button');
                stillButton.on('click', onStill);
            }
        });
    };
}());