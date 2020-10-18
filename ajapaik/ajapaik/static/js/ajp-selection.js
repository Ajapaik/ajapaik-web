(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    /*global docCookies*/
    $(document).ready(function () {
        // TODO: Made in a rush, clean up when there's time
        var areaLat,
            areaLng;
        $('#ajp-selection-middle-panel').find('.panel-body').sortable();
        window.updateLeaderboard();
        var openPhotoDrawer = function (content) {
            var fullScreenImage = $('#ajp-full-screen-image');
            $('#ajp-photo-modal').html(content).modal().find('#ajp-modal-photo').on('load', function () {
                fullScreenImage.attr('data-src', window.photoModalFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
                window.FB.XFBML.parse($('#ajp-photo-modal-like').get(0));
            });
        };
        window.loadPhoto = function (id) {
            $.ajax({
                cache: false,
                url: '/photo/' + id + '/?isSelection=1',
                success: function (result) {
                    openPhotoDrawer(result);
                    var imgContainer = $('#ajp-frontpage-image-container-' + id),
                        nextId = imgContainer.next().data('id'),
                        previousId = imgContainer.prev().data('id'),
                        nextButton = $('.ajp-photo-modal-next-button'),
                        previousButton = $('.ajp-photo-modal-previous-button');
                    if (!nextId) {
                        nextButton.addClass('ajp-photo-modal-next-button-disabled');
                    } else {
                        nextButton.removeClass('ajp-photo-modal-next-button-disabled');
                    }
                    if (!previousId) {
                        previousButton.addClass('ajp-photo-modal-previous-button-disabled');
                    } else {
                        previousButton.removeClass('ajp-photo-modal-previous-button-disabled');
                    }
                }
            });
        };
        window.selectionAddSimilarity = function (type) {
            $('#ajp-loading-overlay').show();
            $.get('/photo-selection/', function (response) {
                var photos = []
                for (var key in response) {
                    photos.push(key)
                }
                $.ajax({
                    type: 'POST',
                    url: window.location.origin + '/api/v1/photos/similar/',
                    data: {
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken'),
                        confirmed: true,
                        similarity_type: type,
                        photos: photos.join(',')
                    },
                    success: function (response) {
                        var points = response.points
                        var message = response && points > 0
                            ?  interpolate(ngettext(
                                'You have gained %s points',
                                'You have gained %s points',
                                points
                            ),
                            [points]
                            )
                            : gettext('Your suggestion has been changed')
                        $.notify(message, {type: 'success'});
                    },
                    // Move the messages to API, 
                    error: function () {
                        $.notify(gettext('Something went wrong, please check your connection. If the issue persists please contact us on Tawk.to'), {type: 'danger'});
                    },
                    complete: function () {
                        $('#ajp-loading-overlay').hide();
                    }
                });
            });
        };
        $(document).on('click', '.ajp-photo-selection-thumbnail-link', function (e) {
            e.preventDefault();
            window.loadPhoto($(this).data('id'));
        });
        $(document).on('mouseenter', '.ajp-photo-selection-thumbnail-link', function () {
            $(this).find('.ajp-remove-from-selection-button').show();
        });
        $(document).on('mouseenter', '.ajp-photo-selection-thumbnail', function () {
            $(this).parent().find('.ajp-remove-from-selection-button').show();
        });
        $(document).on('mouseout', '.ajp-photo-selection-thumbnail', function () {
            $(this).parent().find('.ajp-remove-from-selection-button').hide();
        });
        $(document).on('mouseenter', '.ajp-remove-from-selection-button', function () {
            $(this).show();
        });
        $(document).on('mouseout', '.ajp-remove-from-selection-button', function () {
            $(this).hide();
        });
        $(document).on('click', '#ajp-photo-selection-clear-selection-button', function () {
            var data = {
                clear: true,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            };
            $.post(window.photoSelectionURL, data, function () {
                window.location.reload();
            });
        });
        $(document).on('click', '#ajp-photo-selection-add-similarity', function () {
            selectionAddSimilarity(1);
        });
        $(document).on('click', '#ajp-photo-selection-add-duplicate', function () {
            selectionAddSimilarity(2);
        });
        window.closePhotoDrawer = function () {
            $('#ajp-photo-modal').modal('hide');
        };
        window.startSuggestionLocation = function () {
            if (window.albumId) {
                window.open('/geotag/?album=' + window.albumId + '&photo=' + window.currentlyOpenPhotoId, '_blank');
            } else {
                window.open('/geotag/?photo=' + window.currentlyOpenPhotoId, '_blank');
            }
        };
        var input = document.getElementById('ajp-curator-add-area-name');
        if (input) {
            var options = {};
            var autocomplete = new window.google.maps.places.Autocomplete(input, options);
            window.google.maps.event.addListener(autocomplete, 'place_changed', function () {
                var place = autocomplete.getPlace();
                $('#ajp-curator-add-area-name-hidden').val(place.name);
                areaLat = place.geometry.location.lat();
                areaLng = place.geometry.location.lng();
                window._gaq.push(['_trackEvent', 'Selection', 'Autocomplete place changed']);
            });
        }
        $(document).on('click', '.ajp-remove-from-selection-button', function (e) {
            e.stopPropagation();
            e.preventDefault();
            var $this = $(this),
                data = {
                    id: $this.data('id'),
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                };
            $.post(window.photoSelectionURL, data, function (response) {
                var len = Object.keys(response).length,
                    target = $('#ajp-header-selection-indicator');
                if (len < 2) {
                    $('#ajp-photo-selection-add-similarity').addClass('d-none');
                    $('#ajp-photo-selection-add-duplicate').addClass('d-none');
                }
                if (len > 0) {
                    target.removeClass('d-none');
                } else {
                    target.addClass('d-none');
                }
                target.find('span').html(len);
            });
            $this.parent().parent().remove();
        });
    });
}(jQuery));