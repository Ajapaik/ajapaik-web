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
        window.updateLeaderboard();
        var openPhotoDrawer = function (content) {
            var fullScreenImage = $('#ajapaik-full-screen-image');
            $('#ajapaik-photo-modal').html(content).modal().find('#ajapaik-modal-photo').on('load', function () {
                fullScreenImage.attr('data-src', window.photoModalFullscreenImageUrl).attr('alt', window.currentPhotoDescription);
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
        window.selectionAddSimilarity = function(type) {
            $('#ajapaik-loading-overlay').show();
            $.get('/photo-selection/', function (response) {
                let photos = []
                for (let key in response) {
                    photos.push(key)
                }
                $.ajax({
                    type: 'POST',
                    url: window.location.origin + "/api/v1/photos/similar/",
                    data: {
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken'),
                        confirmed: true,
                        similarity_type: type,
                        photos: photos.join(",")
                    },
                    success: function (response) {
                        let points = response.points
                        let message = response && points > 0
                            ?  interpolate(ngettext(
                                'You have gained %s points',
                                'You have gained %s points',
                                points
                            ),
                            [points]
                            )
                            : gettext('Your guess has been changed')
                        $.notify(message, {type: 'success'});
                    },
                    error: function () {
                        $.notify(gettext('Something went wrong, please check your connection. If the issue persists please contact us on Tawk.to'), {type: 'danger'});
                    },
                    complete: function () {
                        $('#ajapaik-loading-overlay').hide();
                    }
                });
            });
        }
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
        $(document).on('click', '#ajapaik-photo-selection-add-similarity', function () {
            selectionAddSimilarity(1);
        });
        $(document).on('click', '#ajapaik-photo-selection-add-duplicate', function () {
            selectionAddSimilarity(2);
        });
        window.closePhotoDrawer = function () {
            $('#ajapaik-photo-modal').modal('hide');
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
                if (len < 2) {
                    $('#ajapaik-photo-selection-add-similarity').addClass('d-none');
                    $('#ajapaik-photo-selection-add-duplicate').addClass('d-none');
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