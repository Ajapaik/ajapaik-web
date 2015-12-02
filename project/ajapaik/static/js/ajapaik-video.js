(function () {
    'use strict';
    /*global docCookies*/
    /*global albumId*/
    /*global loadPhoto*/
    var videoModal = $('#ajapaik-video-modal'),
        doc = $(document),
        stillButton,
        modalVideo,
        currentVideoTime,
        syncStateToUrl = function () {
            var currentUrl = window.URI(window.location.href);
            currentUrl.removeSearch('video').removeSearch('t');
            if (window.currentVideoId) {
                currentUrl.addSearch('video', window.currentVideoId);
                if (currentVideoTime) {
                    currentUrl.addSearch('t', currentVideoTime);
                }
            }
            window.history.replaceState(null, window.title, currentUrl);
        },
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
                        video: window.currentVideoId,
                        timestamp: parseInt(modalVideo.get(0).currentTime * 1000, 10),
                        album: albumId,
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    success: function (response) {
                        loadPhoto(response.stillId);
                    }
                });
            }
        },
        onTimeupdate = function () {
            currentVideoTime = parseInt(modalVideo.get(0).currentTime, 10);
            syncStateToUrl();
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
        $('#ajapaik-anonymous-login-modal').modal();
    });
    videoModal.on('hidden.bs.modal', function () {
        window.currentVideoId = null;
        window.currentVideoTime = null;
    });
    window.loadVideo = function (id, slug) {
        window.currentVideoId = id;
        $.ajax({
            cache: false,
            url: '/video/' + id + '/' + slug + '/',
            success: function (result) {
                videoModal.html(result);
                videoModal.modal();
                modalVideo = videoModal.find('#ajapaik-modal-video');
                modalVideo.on('pause', onPause);
                modalVideo.on('play', onPlay);
                modalVideo.on('timeupdate', onTimeupdate);
                stillButton = videoModal.find('#ajapaik-video-modal-still-button');
                stillButton.on('click', onStill);
                modalVideo.on('loadedmetadata', function () {
                    if (window.currentVideoTimeTarget) {
                        modalVideo.get(0).currentTime = window.currentVideoTimeTarget;
                        window.currentVideoTimeTarget = null;
                    }
                });
                syncStateToUrl();
            }
        });
    };
}());