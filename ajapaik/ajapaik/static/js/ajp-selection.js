(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    /*global docCookies*/
    $(document).ready(function () {
        // TODO: Made in a rush, clean up when there's time
        var areaLat,
            areaLng;
        window.selectionPhotoRotationDegrees = 0;
        window.selectionPhotoFlipped = false;
        window.selectionPhotoInverted = false;
        $('#ajp-selection-middle-panel').find('.panel-body').sortable();
        window.updateLeaderboard();
        var openPhotoDrawer = function (content) {
            var fullScreenImage = $('#ajp-fullscreen-image');
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
                    openPhotoDrawer(imageUrl);
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

        async function handleErrorsSimilar(response) {
            const data = await response.json();
            if (data.error) {
                throw data;
            }
            return data;
        };

        window.selectionAddSimilarity = function (similarityType) {
            $('#ajp-loading-overlay').show();
            $.get('/photo-selection/', function (response) {
                var photos = []
                for (var key in response) {
                    photos.push(key)
                }
                fetch(similarPhotosUrl, {
                    method: 'POST',
                    beforeSend : function(xhr) {
                        xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
                    },
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        confirmed: true,
                        similarityType,
                        photos
                    })

                })
                .then(handleErrorsSimilar)
                .then(function(response) {
                    let points = response.points;
                    let message = response && points > 0
                        ?  interpolate(ngettext(
                            'You have gained %s point',
                            'You have gained %s points',
                            points
                        ),
                        [points]
                        )
                        : gettext('Your suggestion has been changed');
                    $.notify(message, {type: "success"});
                    $('#ajp-loading-overlay').hide();
                }).catch((error) => {
                    $('#ajp-loading-overlay').hide();
                    $.notify(gettext('Something went wrong, please check your connection. If the issue persists please contact us on Tawk.to'), {type: "danger"});
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
                if (len < 1) {
                    $('#ajp-photo-selection-create-album-button').addClass('d-none');
                    $('#ajp-photo-selection-clear-selection-button').addClass('d-none');
                    $('#ajp-photo-selection-categorize-scenes-button').addClass('d-none');
                    $('#ajp-photo-selection-edit-pictures-button').addClass('d-none');
                }
                if (len > 0) {
                    target.removeClass('d-none');
                } else {
                    target.addClass('d-none');
                }
                target.find('div').html(len);
            });
            $this.parent().parent().remove();
        });

        let container = 'body';
        let submitCategoryContent = `<div class='d-flex mb-4' style='justify-content:center;'><div class='d-flex' style='flex-direction:column;align-items:center;'><button onclick='clickSceneCategoryButton(this.id);' id='interior-button' class='btn mr-2 btn-light' style='display:grid;'><span class='material-icons notranslate ajp-icon-48'>hotel</span><span>` + gettext('Interior') + `</span></button></div><div class='d-flex' style='flex-direction:column;align-items:center;'><button onclick='clickSceneCategoryButton(this.id);' id='exterior-button' class='btn ml-2 btn-light' style='display:grid;'><span class='material-icons ajp-icon-48 notranslate'>home</span><span>` + gettext('Exterior') + `</span></button></div></div><div class='d-flex'><div class='d-flex' style='flex-direction:column;align-items:center;'><button onclick='clickViewpointElevationCategoryButton(this.id);' id='ground-button' class='btn mr-2 btn-light' style='display:grid;'><span class='material-icons notranslate ajp-icon-48'>nature_people</span><span>` + gettext('Ground') + `</span></button></div><div class='d-flex' style='flex-direction:column;align-items:center;'><button onclick='clickViewpointElevationCategoryButton(this.id);' id='raised-button' class='btn mr-2 btn-light' style='display:grid;'><span class='material-icons notranslate ajp-icon-48'>location_city</span><span>` + gettext('Raised') + `</span></button></div><div class='d-flex' style='flex-direction:column;align-items:center;'><button onclick='clickViewpointElevationCategoryButton(this.id);' id='aerial-button' class='btn ml-2 d-grid btn-light' style='display:grid;'><span class='material-icons ajp-icon-48 notranslate'>flight</span><span>` + gettext('Aerial') + `</span></button></div></div>`;
        let submitCategoryActionButtonTemplate = `<button id='send-suggestion-button' onclick='submitCategories();' class='btn btn-success mt-3 w-100' disabled>` + gettext('Submit') + `</button>`;
        submitCategoryContent += submitCategoryActionButtonTemplate;
        let submitCategoryTitle = gettext('Categorize scene');

        window.submitCategories = function () {
            $.get('/photo-selection/', function (response) {
                let photos = []
                for (var key in response) {
                    photos.push(key)
                }
                submitCategorySuggestion(photos, true);
            });
        };

        $('#ajp-photo-selection-categorize-scenes-button').popover({
            html: true,
            sanitize: false,
            content: submitCategoryContent,
            title: submitCategoryTitle,
            container,
        });

        let pictureEditContent = `<div class='d-flex' style='justify-content:center;'><div class='d-flex' style='flex-direction:column;align-items:center;'><button onclick='clickPhotoEditButton(this.id, true);' id='flip-button' class='btn mr-2' style='display:grid;'><span class='material-icons notranslate ajp-icon-48'>flip</span><span>` + gettext('Flip') + `</span></button></div><div class='d-flex' style='flex-direction:column;align-items:center;'><button onclick='clickPhotoEditButton(this.id, true);' id='invert-button' class='btn ml-2' style='display:grid;'><span class='material-icons ajp-icon-48 notranslate'>invert_colors</span><span>` + gettext('Invert') + `</span></button></div><div class='d-flex' style='flex-direction:column;align-items:center;'><button onclick='clickPhotoEditButton(this.id, true);' id='rotate-button' class='btn ml-2' style='display:grid;'><span class='material-icons ajp-icon-48 notranslate'>rotate_left</span><span>` + gettext('Rotate') + `</span></button></div></div>`;
        let pictureEditActionButtonTemplate = `<button id='send-edit-button' onclick="submitPictureEdits();" class='btn btn-success mt-3 w-100'>` + gettext('Submit') + `</button>`;
        pictureEditContent += pictureEditActionButtonTemplate;

        let pictureEditTitle = gettext('Edit');

        window.submitPictureEdits = function () {
            $.get('/photo-selection/', function (response) {
                let photos = []
                for (var key in response) {
                    photos.push(key)
                }
                submitPictureEditSuggestion(photos, true);
            });
        };

        $('#ajp-photo-selection-edit-pictures-button').popover({
            html: true,
            sanitize: false,
            content: pictureEditContent,
            title: pictureEditTitle,
            container
        });
    });
}(jQuery));