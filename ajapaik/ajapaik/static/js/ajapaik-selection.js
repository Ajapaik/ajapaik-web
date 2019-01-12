(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    /*global docCookies*/
    $(document).ready(function () {
        // TODO: Made in a rush, clean up when there's time
        var areaLat,
            areaLng;
        $('#ajapaik-selection-middle-panel').find('.panel-body').sortable();
        $('#ajapaik-photo-selection-create-tan-tour-button').popover();
        window.updateLeaderboard();
        var openPhotoDrawer = function (content) {
            var fullScreenImage = $('#ajapaik-full-screen-image');
            $('#ajapaik-photo-modal').html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
                fullScreenImage.attr('data-src', window.photoModalFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1], '#ajapaik-full-screen-image');
                window.FB.XFBML.parse($('#ajapaik-photo-modal-like').get(0));
            });
        };
        window.loadPhoto = function (id) {
            $.ajax({
                cache: false,
                url: '/photo/' + id + '/?isSelection=1',
                success: function (result) {
                    openPhotoDrawer(result);
                    var imgContainer = $('#ajapaik-frontpage-image-container-' + id),
                        nextId = imgContainer.next().data('id'),
                        previousId = imgContainer.prev().data('id'),
                        nextButton = $('.ajapaik-photo-modal-next-button'),
                        previousButton = $('.ajapaik-photo-modal-previous-button');
                    if (!nextId) {
                        nextButton.addClass('ajapaik-photo-modal-next-button-disabled');
                    } else {
                        nextButton.removeClass('ajapaik-photo-modal-next-button-disabled');
                    }
                    if (!previousId) {
                        previousButton.addClass('ajapaik-photo-modal-previous-button-disabled');
                    } else {
                        previousButton.removeClass('ajapaik-photo-modal-previous-button-disabled');
                    }
                }
            });
        };
        $(document).on('click', '.ajapaik-photo-selection-thumbnail-link', function (e) {
            e.preventDefault();
            window.loadPhoto($(this).data('id'));
        });
        $(document).on('mouseenter', '.ajapaik-photo-selection-thumbnail-link', function () {
            $(this).find('.ajapaik-remove-from-selection-button').show();
        });
        $(document).on('mouseenter', '.ajapaik-photo-selection-thumbnail', function () {
            $(this).parent().find('.ajapaik-remove-from-selection-button').show();
        });
        $(document).on('mouseout', '.ajapaik-photo-selection-thumbnail', function () {
            $(this).parent().find('.ajapaik-remove-from-selection-button').hide();
        });
        $(document).on('mouseenter', '.ajapaik-remove-from-selection-button', function () {
            $(this).show();
        });
        $(document).on('mouseout', '.ajapaik-remove-from-selection-button', function () {
            $(this).hide();
        });
        $(document).on('click', '#ajapaik-photo-selection-clear-selection-button', function () {
            var data = {
                clear: true,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            };
            $.post(window.photoSelectionURL, data, function () {
                window.location.reload();
            });
        });
        window.closePhotoDrawer = function () {
            $('#ajapaik-photo-modal').modal('toggle');
        };
        window.startGuessLocation = function (photoId) {
            if (window.albumId) {
                window.open('/geotag/?album=' + window.albumId + '&photo=' + photoId, '_blank');
            } else {
                window.open('/geotag/?photo=' + photoId, '_blank');
            }
        };
        var input = document.getElementById('ajapaik-curator-add-area-name');
        if (input) {
            var options = {};
            var autocomplete = new window.google.maps.places.Autocomplete(input, options);
            window.google.maps.event.addListener(autocomplete, 'place_changed', function() {
                var place = autocomplete.getPlace();
                $('#ajapaik-curator-add-area-name-hidden').val(place.name);
                areaLat = place.geometry.location.lat();
                areaLng = place.geometry.location.lng();
                window._gaq.push(['_trackEvent', 'Selection', 'Autocomplete place changed']);
            });
        }
        $(document).on('click', '#ajapaik-curator-confirm-album-selection-button', function () {
            var albums =  $('#id_albums').val(),
                allElements = $('.ajapaik-photo-selection-thumbnail-link'),
                allIds = [],
                i,
                l;
            for (i = 0, l = allElements.length; i < l; i += 1) {
                allIds.push($(allElements[i]).data('id'));
            }
            $('#ajapaik-loading-overlay').show();
            $.ajax({
                type: 'POST',
                url: '/upload-selection/',
                data: {
                    selection: JSON.stringify(allIds),
                    albums: albums,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success: function (response) {
                    $('#ajapaik-loading-overlay').hide();
                    if (response.error) {
                        $('#ajapaik-curator-upload-error').show();
                        $('#ajapaik-curator-upload-error-message').html(response.error);
                        $('#ajapaik-selection-top-panel').find('.alert-error').html(response.error).removeClass('hidden');
                        $('#ajapaik-selection-top-panel').find('.alert-success').html('').addClass('hidden');
                    } else {
                        $('#ajapaik-selection-top-panel').find('.alert-error').html('').addClass('hidden');
                        $('#ajapaik-selection-top-panel').find('.alert-success').html(response.message).removeClass('hidden');
                        $('#ajapaik-curator-upload-error').hide();
                        $('#ajapaik-curator-upload-error-message').html(window.gettext('System error'));
                        $('#ajapaik-choose-albums-modal').modal('hide');
                        $('#ajapaik-curator-add-album-name').val(null);
                        $('#ajapaik-curator-add-area-name-hidden').val(null);
                        $('#ajapaik-curator-add-area-name').val(null);
                        areaLat = null;
                        areaLng = null;
                        window.loadPossibleParentAlbums();
                        window.loadSelectableAlbums();
                    }
                    window.loadSelectableAlbums();
                    window._gaq.push(['_trackEvent', 'Selection', 'Upload success']);
                },
                error: function () {
                    $('#ajapaik-loading-overlay').hide();
                    $('#ajapaik-curator-upload-error').show();
                    $('#ajapaik-selection-top-panel').find('.alert-error').html(window.gettext('System error')).removeClass('hidden');
                    window._gaq.push(['_trackEvent', 'Selection', 'Upload error']);
                }
            });
        });
        $(document).on('click', '#ajapaik-photo-selection-create-album-button', function () {
            $('#ajapaik-choose-albums-modal').modal();
            window.loadSelectableAlbums();
            window.loadPossibleParentAlbums();
        });
        $(document).on('click', '#ajapaik-photo-selection-create-tan-tour-button', function () {
            if (!$(this).hasClass('btn-disabled')) {
                var ids = [];
                $('.ajapaik-photo-selection-thumbnail-link').map(function (i, e) {
                    ids.push($(e).data('id'));
                });
                $.ajax({
                    url: '/then-and-now-tours/generate-ordered-tour/',
                    traditional: true,
                    method: 'POST',
                    data: {
                        ids: ids,
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    success: function (response) {
                        if (response.tour) {
                            location.href = '/then-and-now-tours/map/' + response.tour + '/';
                        }
                    }
                });
            }
        });
        $(document).on('click', '.ajapaik-remove-from-selection-button', function (e) {
            e.stopPropagation();
            e.preventDefault();
            var $this = $(this),
                data = {
                    id: $this.data('id'),
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                };
            $.post(window.photoSelectionURL, data, function (response) {
                var len = Object.keys(response).length,
                    target = $('#ajapaik-header-selection-indicator');
                if (len > 0) {
                    target.removeClass('hidden');
                } else {
                    target.addClass('hidden');
                }
                target.find('span').html(len);
            });
            $this.parent().parent().remove();
        });
    });
}(jQuery));