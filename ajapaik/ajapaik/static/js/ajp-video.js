(function () {
    'use strict';
    /*global docCookies*/
    /*global albumId*/
    /*global loadPhoto*/
    var videoModal = $('#ajp-video-modal'),
        videoviewVideo = $('#ajp-videoview-video'),
        videoviewSpeedButtons = $('#ajp-videoview-speed-buttons').find('button'),
        doc = $(document),
        stillButton,
        videoviewStillButton = $('#ajp-video-modal-still-button'),
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
                $('#ajp-loading-overlay').show();
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
                        window.updateFrontpagePhotosAsync();
                    },
                    complete: function() {
                        $('#ajp-loading-overlay').hide();
                    }
                });
                if (typeof window.reportModalVideoStillClick === 'function') {
                    window.reportModalVideoStillClick();
                }
            }
        },
        onTimeupdate = function () {
            currentVideoTime = parseInt(modalVideo.get(0).currentTime, 10);
            syncStateToUrl();
        };
    doc.on('click', '#ajp-video-modal-close-button', function (e) {
        e.preventDefault();
        $('#ajp-video-modal').modal('hide');
    });
    doc.on('click', '.ajp-frontpage-video-container', function (e) {
        e.preventDefault();
    });
    doc.on('click', '.ajp-frontpage-video', function () {
        var id = $(this).data('id');
        window.loadVideo(id, $(this).data('slug'));
        if (typeof window.reportVideoModalOpen === 'function') {
            window.reportVideoModalOpen(id);
        }
    });
    doc.on('click', '#ajp-video-modal-anonymous-icon', function () {
        modalVideo.get(0).pause();
        $('#ajp-anonymous-login-modal').modal();
        if (typeof window.reportVideoModalAnonymousLoginStart === 'function') {
            window.reportVideoModalAnonymousLoginStart();
        }
    });
    doc.on('click', '#ajp-video-modal-source-link', function () {
        if (typeof window.reportVideoModalSourceLinkClick === 'function') {
            window.reportVideoModalSourceLinkClick($(this).data('id'));
        }
    });
    doc.on('click', '#ajp-video-modal-speed-buttons button', function () {
        var $this = $(this);
        $this.parent().find('button').removeClass('active');
        $this.addClass('active');
        modalVideo.get(0).playbackRate = $(this).data('speed');
    });
    videoviewSpeedButtons.click(function () {
        var $this = $(this);
        videoviewSpeedButtons.removeClass('active');
        $this.addClass('active');
        videoviewVideo.get(0).playbackRate = $this.data('speed');
    });
    videoModal.on('hidden.bs.modal', function () {
        window.currentVideoId = null;
        window.currentVideoTime = null;
        modalVideo.prop('src', '');
    });
    if (videoviewVideo.length > 0) {
        videoviewVideo.on('pause', function () {
             videoviewStillButton.addClass('enabled').removeClass('disabled');
        });
        videoviewVideo.on('play', function () {
             videoviewStillButton.addClass('disabled').removeClass('enabled');
        });
        videoviewVideo.on('timeupdate', function () {
            currentVideoTime = parseInt(videoviewVideo.get(0).currentTime, 10);
            syncStateToUrl();
        });
        videoviewStillButton.click(function () {
            if (!$(this).hasClass('disabled')) {
                $.ajax({
                    url: '/video-still/',
                    method: 'POST',
                    data: {
                        video: window.currentVideoId,
                        timestamp: parseInt(videoviewVideo.get(0).currentTime * 1000, 10),
                        album: albumId,
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    success: function (response) {
                        window.location.href = '/photo/' + response.stillId + '/';
                    }
                });
            }
            if (typeof window.reportVideoviewVideoStillClick === 'function') {
                window.reportVideoviewVideoStillClick();
            }
        });
        videoviewVideo.on('loadedmetadata', function () {
            if (window.getQueryParameterByName('t')) {
                videoviewVideo.get(0).currentTime = parseInt(window.getQueryParameterByName('t'), 10);
            }
        });
        $('#ajp-videoview-source-link').click(function () {
            if (typeof window.reportVideoviewSourceLinkClick === 'function') {
                window.reportVideoviewSourceLinkClick($(this).data('id'));
            }
        });
        $('.ajp-videoview-album-link').click(function () {
            if (typeof window.reportVideoviewAlbumLinkClick === 'function') {
                window.reportVideoviewAlbumLinkClick();
            }
        });
    }
    window.loadVideo = function (id, slug) {
        window.currentVideoId = id;
        $.ajax({
            cache: false,
            url: '/video/' + id + '/' + slug + '/',
            success: function (result) {
                videoModal.html(result);
                videoModal.modal();
                modalVideo = videoModal.find('#ajp-modal-video');
                modalVideo.on('pause', onPause);
                modalVideo.on('play', onPlay);
                modalVideo.on('timeupdate', onTimeupdate);
                stillButton = videoModal.find('#ajp-video-modal-still-button');
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