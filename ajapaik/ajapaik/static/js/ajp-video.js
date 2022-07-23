(function () {
  'use strict';
  /*global docCookies*/
  /*global albumId*/
  /*global loadPhoto*/
  let videoModal = $('#ajp-video-modal'),
    video = $('#ajp-video'),
    videoSpeedButtons = $('#ajp-video-speed-buttons').find('button'),
    doc = $(document),
    stillButton,
    videoStillButton = $('#ajp-video-modal-still-button'),
    modalVideo,
    currentVideoTime,
    syncStateToUrl = function () {
      const currentUrl = window.URI(window.location.href);
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
            csrfmiddlewaretoken: docCookies.getItem('csrftoken'),
          },
          success: function (response) {
            loadPhoto(response.stillId);
            window.updateFrontpagePhotosAsync();
          },
          complete: function () {
            $('#ajp-loading-overlay').hide();
          },
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
    const id = $(this).data('id');
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
    const $this = $(this);
    $this.parent().find('button').removeClass('active');
    $this.addClass('active');
    modalVideo.get(0).playbackRate = $(this).data('speed');
  });
  videoSpeedButtons.click(function () {
    const $this = $(this);
    videoSpeedButtons.removeClass('active');
    $this.addClass('active');
    video.get(0).playbackRate = $this.data('speed');
  });
  videoModal.on('hidden.bs.modal', function () {
    window.currentVideoId = null;
    window.currentVideoTime = null;
    modalVideo.prop('src', '');
  });
  if (video.length > 0) {
    video.on('pause', function () {
      videoStillButton.addClass('enabled').removeClass('disabled');
    });
    video.on('play', function () {
      videoStillButton.addClass('disabled').removeClass('enabled');
    });
    video.on('timeupdate', function () {
      currentVideoTime = parseInt(video.get(0).currentTime, 10);
      syncStateToUrl();
    });
    videoStillButton.click(function () {
      if (!$(this).hasClass('disabled')) {
        $.ajax({
          url: '/video-still/',
          method: 'POST',
          data: {
            video: window.currentVideoId,
            timestamp: parseInt(video.get(0).currentTime * 1000, 10),
            album: albumId,
            csrfmiddlewaretoken: docCookies.getItem('csrftoken'),
          },
          success: function (response) {
            window.location.href = '/photo/' + response.stillId + '/';
          },
        });
      }
      if (typeof window.reportVideoStillClick === 'function') {
        window.reportVideoStillClick();
      }
    });
    video.on('loadedmetadata', function () {
      if (window.getQueryParameterByName('t')) {
        video.get(0).currentTime = parseInt(
          window.getQueryParameterByName('t'),
          10
        );
      }
    });
    $('#ajp-video-source-link').click(function () {
      if (typeof window.reportVideoSourceLinkClick === 'function') {
        window.reportVideoSourceLinkClick($(this).data('id'));
      }
    });
    $('.ajp-video-album-link').click(function () {
      if (typeof window.reportVideoAlbumLinkClick === 'function') {
        window.reportVideoAlbumLinkClick();
      }
    });
  }
  window.loadVideo = function (id, slug) {
    window.currentVideoId = id;
    $.ajax({
      cache: false,
      url: '/video/' + id + '/' + slug + '/',
      success: function (result) {
        videoModal.html(imageUrl);
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
      },
    });
  };
})();
