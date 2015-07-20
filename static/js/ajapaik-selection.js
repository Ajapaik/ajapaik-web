(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        var areaLat,
            areaLng;
        $('#ajapaik-selection-middle-panel').find('.panel-body').sortable();
        window.updateLeaderboard();
        var openPhotoDrawer = function (content) {
            var fullScreenImage = $('#ajapaik-full-screen-image');
            $('#ajapaik-photo-modal').html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
                fullScreenImage.prop('src', window.photoModalFullscreenImageUrl);
                window.prepareFullscreen(window.photoModalFullscreenImageSize[0], window.photoModalFullscreenImageSize[1], '#ajapaik-full-screen-image');
                window.FB.XFBML.parse($('#ajapaik-photo-modal-like').get(0));
            });
        };
        window.loadPhoto = function (id) {
            $.ajax({
                cache: false,
                url: '/foto/' + id + '/?isSelection=1',
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
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
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
                window.open('/game/?album=' + window.albumId + '&photo=' + photoId + '&fromButton=1', '_blank');
            } else {
                window.open('/game/?photo=' + photoId + '&fromButton=1', '_blank');
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
            var album = $('#ajapaik-curator-album-select').val(),
                allElements = $('.ajapaik-photo-selection-thumbnail-link'),
                allIds = [],
                i,
                l,
                parentAlbum = $('#ajapaik-curator-change-album-parent').val();
            if (album == -1) {
                album = null;
            }
            if (parentAlbum == -1) {
                parentAlbum = null;
            }
            for (i = 0, l = allElements.length; i < l; i += 1) {
                allIds.push($(allElements[i]).data('id'));
            }
            $('#ajapaik-loading-overlay').show();
            $.ajax({
                type: 'POST',
                url: '/upload-selection/',
                data: {
                    selection: JSON.stringify(allIds),
                    album: album,
                    name: $('#ajapaik-curator-add-album-name').val(),
                    description: $('#ajapaik-curator-add-album-description').val(),
                    open: $('#ajapaik-curator-add-album-public-mutable').is(':checked'),
                    public: $('#ajapaik-curator-add-album-public').is(':checked'),
                    parent_album: parentAlbum,
                    areaLat: areaLat,
                    areaLng: areaLng,
                    csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
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
                        //var feedbackModalDiv = $('#ajapaik-curator-feedback-modal');
                        $('#ajapaik-curator-add-album-name').val(null);
                        $('#ajapaik-curator-add-area-name-hidden').val(null);
                        //feedbackModalDiv.modal('show').on('shown.bs.modal', function () {
                        //    //$($(this).find('#ajapaik-curator-share-button-container')).empty().append(tmpl('ajapaik-curator-share-set-button', {gameLink: albumPlayLink}));
                        //    //window.FB.XFBML.parse();
                        //});
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
        $(document).on('click', '.ajapaik-remove-from-selection-button', function (e) {
            e.stopPropagation();
            e.preventDefault();
            var $this = $(this),
                data = {
                    id: $this.data('id'),
                    csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
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