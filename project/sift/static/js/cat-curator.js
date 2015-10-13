$(function () {
    'use strict';
    /*global tmpl*/
    /*global searchURL*/
    /*global loadAlbumsURL*/
    /*global docCookies*/
    /*global albumInfoURL*/
    /*global albumEditURL*/
    /*global selectionUploadURL*/
    /*global gettext*/
    /*global JSON*/
    var resultCount = 0,
        start = 200,
        resultIds = [],
        fullResultSet = {},
        selectionDiv = $('#cat-curator-selection'),
        resultDiv = $('#cat-curator-search-results'),
        createResultElement = function (item) {
            if (item.cachedThumbnailUrl !== '14e5c228503ec8e7e004a13d48919768') {
                fullResultSet[item.id] = item;
                resultDiv.append(tmpl('cat-curator-result-template', item));
            } else {
                var element = $('#cat-curator-result-count'),
                    currentValue = parseInt(element.html(), 10);
                element.html(currentValue - 1);
            }
        },
        buildSelectionDiv = function () {
            selectionDiv.empty();
            for (var key in window.selectedResults) {
                if (window.selectedResults.hasOwnProperty(key)) {
                    var currentItem = window.selectedResults[key];
                    selectionDiv.append(tmpl('cat-curator-selection-template', currentItem));
                }
            }
        },
        loadMyAlbums = function () {
            $.ajax({
                type : 'POST',
                url : loadAlbumsURL,
                data: {
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success : function(response) {
                    var targetDiv = $('#cat-curator-my-albums'),
                        responseLength = response.length;
                    targetDiv.empty();
                    $('#cat-curator-my-albums-size').html(responseLength);
                    for (var i = 0; i < responseLength; i += 1) {
                        targetDiv.append(tmpl('cat-curator-my-album-template', response[i]));
                    }
                }
            });
        },
        loadSelectableAlbums = function () {
            $.ajax({
                type: 'POST',
                url: loadAlbumsURL,
                data: {
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success: function (response) {
                    var targetDiv = $('#cat-curator-album-select');
                    targetDiv.empty();
                    targetDiv.append(
                        tmpl(
                            'cat-curator-my-album-select-option',
                            {id: -1, name: gettext('Not selected')}
                        )
                    );
                    for (var i = 0, l = response.length; i < l; i += 1) {
                        targetDiv.append(tmpl('cat-curator-my-album-select-option', response[i]));
                    }
                }
            });
        },
        escapeRegExp = function(string) {
            return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
        },
        replaceAll = function(string, find, replace) {
            return string.replace(new RegExp(escapeRegExp(find), 'g'), replace);
        };
    window.selectedResults = {};
    window.formatId = function (id) {
        id = replaceAll(id, ':', '');
        id = replaceAll(id, '.', '');
        return id;
    };
    window.imageLoaded = function (id) {
        var targetContainer = $('#cat-curator-selection-item-' + window.formatId(id)),
            targetImage = targetContainer.find('img')[0];
        if (targetImage) {
            targetContainer.find('.cat-curator-selection-image-size').html(targetImage.naturalWidth + 'x' + targetImage.naturalHeight);
        }
    };
    $(document).ready(function () {
        loadMyAlbums();
    });
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var href = $(e.target).attr('href');
        if (href === '#cat-curator-selection-tab') {
            buildSelectionDiv();
            $('#cat-curator-my-albums').hide();
            $('#cat-curator-search-results').hide();
            $('#cat-curator-selection').show();
        } else if (href === '#cat-curator-results-tab') {
            $('#cat-curator-my-albums').hide();
            $('#cat-curator-search-results').show();
            $('#cat-curator-selection').hide();
        } else if (href === '#cat-curator-my-albums-tab') {
            $('#cat-curator-my-albums').show();
            $('#cat-curator-search-results').hide();
            $('#cat-curator-selection').hide();
        }
    });
    $('#cat-curator-full-search').on('keypress', function (e) {
        if (parseInt(e.keyCode, 10) === 13) {
            $('#cat-curator-search-button').click();
        }
    });
    $('.cat-curator-load-more').click(function () {
        $('#cat-loading-overlay').show();
        var slice = resultIds.slice(start, start + 200),
            filterValue = $('#cat-curator-search-filter-existing').prop('checked');
        start += 200;
        $.ajax({
            type : 'POST',
            url : searchURL,
            data: {
                ids: slice,
                filterExisting: filterValue,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            },
            success : function(msg) {
                if (resultCount > start) {
                    $('.cat-curator-load-more').show();
                    $('#cat-curator-load-more-row').show();
                } else {
                    $('.cat-curator-load-more').hide();
                    $('#cat-curator-load-more-row').hide();
                }
                for (var i = 0, l = msg.result.length; i < l; i += 1) {
                    msg.result[i].idx = start - 200 + i;
                    createResultElement(msg.result[i]);
                }
                $('#cat-loading-overlay').hide();
            },
            error: function () {
                $('#cat-loading-overlay').hide();
            }
        });
    });
    $('#cat-curator-search-button').click(function () {
        $('#cat-loading-overlay').show();
        $('.cat-curator-feedback-alert').hide();
        $('#cat-curator-search-results').empty();
        var filterValue = $('#cat-curator-search-filter-existing').prop('checked');
        $.ajax({
            type : 'POST',
            url : searchURL,
            data: {
                fullSearch: $('#cat-curator-full-search').val(),
                filterExisting: filterValue,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            },
            success : function(msg) {
                $('#cat-loading-overlay').hide();
                resultIds = msg.result.ids;
                resultCount = resultIds.length;
                $('#cat-curator-result-count').html(resultCount);
                if (resultCount > 200) {
                    $('.cat-curator-load-more').show();
                    $('#cat-curator-load-more-row').show();
                } else {
                    $('.cat-curator-load-more').hide();
                    $('#cat-curator-load-more-row').hide();
                }
                for (var i = 0, l = msg.result.firstRecordViews.length; i < l; i += 1) {
                    msg.result.firstRecordViews[i].idx = i;
                    createResultElement(msg.result.firstRecordViews[i]);
                }
            },
            error: function () {
                $('#cat-loading-overlay').hide();
            }
        });
    });
    $(document).on('click', '.cat-result-item', function () {
        var $this = $(this),
            target = fullResultSet[$this.data('id')];
        if (window.selectedResults[$this.data('id')]) {
            delete window.selectedResults[$this.data('id')];
            $this.removeClass('cat-curator-selected-image');
            $('#cat-curator-selection-size').html(Object.keys(window.selectedResults).length);
        } else {
            window.selectedResults[$this.data('id')] = target;
            $this.addClass('cat-curator-selected-image');
            $('#cat-curator-selection-size').html(Object.keys(window.selectedResults).length);
        }
    });
    $('#cat-curator-clear-selection').click(function () {
        window.selectedResults = {};
        buildSelectionDiv();
        $('#cat-curator-selection-size').html(Object.keys(window.selectedResults).length);
        $('.cat-result-item').removeClass('cat-curator-selected-image');
    });
    $(document).on('click', '.cat-curator-invert-colors-button', function() {
        var $this = $(this),
            targetSelector = '#cat-curator-selection-item-' + window.formatId($this[0].dataset.id),
            target = $($(targetSelector).find('img')[0]);
        $this.toggleClass('active');
        if (target.hasClass('cat-photo-inverted')) {
            target.removeClass('cat-photo-inverted');
            window.selectedResults[$this[0].dataset.id].invert = false;
        } else {
            target.addClass('cat-photo-inverted');
            window.selectedResults[$this[0].dataset.id].invert = true;
        }
    });
    $(document).on('click', '.cat-curator-flip-button', function() {
        var $this = $(this),
            targetSelector = '#cat-curator-selection-item-' + window.formatId($this[0].dataset.id),
            target = $($(targetSelector).find('img')[0]);
        $this.toggleClass('active');
        if (target.hasClass('cat-photo-flipped')) {
            target.removeClass('cat-photo-flipped');
            if (target.hasClass('rotate90-flipped')) {
                target.removeClass('rotate90-flipped').addClass('rotate90');
            } else if (target.hasClass('rotate180-flipped')) {
                target.removeClass('rotate180-flipped').addClass('rotate180');
            } else if (target.hasClass('rotate270-flipped')) {
                target.removeClass('rotate270-flipped').addClass('rotate270');
            }
            window.selectedResults[$this[0].dataset.id].flip = false;
        } else {
            target.addClass('cat-photo-flipped');
            if (target.hasClass('rotate90')) {
                target.removeClass('rotate90').addClass('rotate90-flipped');
            } else if (target.hasClass('rotate180')) {
                target.removeClass('rotate180').addClass('rotate180-flipped');
            } else if (target.hasClass('rotate270')) {
                target.removeClass('rotate270').addClass('rotate270-flipped');
            }
            window.selectedResults[$this[0].dataset.id].flip = true;
        }
    });
    $(document).on('click', '.cat-curator-stereo-button', function() {
        var $this = $(this);
        window.selectedResults[$this[0].dataset.id].stereo = !$this.hasClass('active');
        $this.toggleClass('active');
    });
    $(document).on('click', '.cat-curator-rotate-button', function() {
        var $this = $(this),
            targetSelectionItem = $('#cat-curator-selection-item-' + window.formatId($this[0].dataset.id)),
            targetImage = targetSelectionItem.find('img'),
            arrayItem = window.selectedResults[$this[0].dataset.id];
        if (!arrayItem.rotated) {
            arrayItem.rotated = 90;
            if (arrayItem.flip) {
                targetImage.addClass('rotate90-flipped');
            } else {
                targetImage.addClass('rotate90');
            }
        } else {
            arrayItem.rotated += 90;
            var classToAdd = null;
            if (parseInt(arrayItem.rotated, 10) === 360) {
                arrayItem.rotated = 0;
            } else {
                classToAdd = 'rotate' + arrayItem.rotated;
                if (arrayItem.flip) {
                    classToAdd += '-flipped';
                }
            }
            targetImage.removeClass('rotate90').removeClass('rotate180')
                    .removeClass('rotate270').removeClass('rotate90-flipped').removeClass('rotate180-flipped').removeClass('rotate270-flipped');
            if (classToAdd) {
                targetImage.addClass(classToAdd);
            }
        }
    });
    $(document).on('click', '.cat-curator-delete-button', function() {
        var targetId = $(this)[0].dataset.id,
            targetResultItem = $('#cat-result-item-' + window.formatId(targetId)),
            targetSelectionItem = $('#cat-curator-selection-item-' + window.formatId(targetId));
        if (window.selectedResults[targetId]) {
            delete window.selectedResults[targetId];
            targetSelectionItem.remove();
            targetResultItem.removeClass('cat-curator-selected-image');
            $('#cat-curator-selection-size').html(Object.keys(window.selectedResults).length);
        } else {
            window.selectedResults[$(this)[0].dataset.id] = targetId;
            targetResultItem.addClass('cat-curator-selected-image');
            $('#cat-curator-selection-size').html(Object.keys(window.selectedResults).length);
        }
    });
    $('#cat-curator-gallery-switch').click(function () {
        $('.cat-curator-selection-controls').hide();
        $('.cat-curator-selection-item').removeClass('row').addClass('thumbnail').addClass('col-xs-2');
        $('.cat-curator-selection-image').removeClass('col-xs-6').addClass('cat-curator-selection-image-min-max');
    });
    $('#cat-curator-list-switch').click(function () {
        $('.cat-curator-selection-controls').show();
        $('.cat-curator-selection-item').addClass('row').removeClass('thumbnail').removeClass('col-xs-2');
        $('.cat-curator-selection-image').addClass('col-xs-6').removeClass('cat-curator-selection-image-min-max');
    });
    $('#cat-curator-submit-selection').click(function () {
        $('#cat-curator-upload-error').hide();
        $('#cat-choose-albums-modal').modal('show').on('hidden.bs.modal', function () {
            $('#cat-curator-album-filter').empty();
        });
        loadSelectableAlbums();
    });
    $('#cat-curator-create-new-album-checkbox').change(function () {
        var $this = $(this),
            creationFields = $('.cat-curator-new-album-creation-field'),
            existingFields = $('.cat-curator-add-to-existing-album-field');
        if ($this.is(':checked')) {
            creationFields.show();
            existingFields.hide();
        } else {
            creationFields.hide();
            existingFields.show();
        }
    });
    $('#cat-curator-select-all').click(function () {
        var start = parseInt($('#cat-curator-selection-start-index').val(), 10),
            step = parseInt($('#cat-curator-selection-step').val(), 10),
            targets = $('img.cat-result-item:not(.cat-curator-selected-image)');
        if (start && step) {
            for (var i = start, l = targets.length; i < l; i += step) {
                targets[i].click();
            }
        } else {
            targets.click();
        }
    });
    $(document).on('click', '.cat-curator-edit-album-button', function () {
        var targetId = $(this)[0].dataset.id;
        $.ajax({
            type : 'POST',
            url : albumInfoURL,
            data: {
                album: targetId,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            },
            success : function(response) {
                console.log(response);
                $('#cat-curator-change-album-name').val(response.title);
                $('#cat-curator-change-album-description').val(response.subtitle);
                $('#cat-curator-change-album-id').val(response.id);
                $('#cat-curator-edit-my-album-modal').modal('show');
            }
        });
    });
    $(document).on('click', '#cat-curator-confirm-album-edit-button', function () {
        var targetId = $('#cat-curator-change-album-id').val();
        $('#cat-curator-edit-album-error').hide();
        $.ajax({
            type : 'POST',
            url : albumEditURL,
            data: {
                albumId: targetId,
                name: $('#cat-curator-change-album-name').val(),
                description: $('#cat-curator-change-album-description').val(),
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            },
            success : function() {
                $('#cat-curator-edit-album-error').hide();
                $('#cat-curator-edit-my-album-modal').modal('hide');
                loadMyAlbums();
            }
        });
    });
    $('#cat-curator-confirm-album-selection-button').click(function () {
        var confirm = false,
            album = $('#cat-curator-album-select').val();
        if (Object.keys(window.selectedResults).length < 5 && !album) {
            confirm = window.confirm(gettext('Are you sure you want to create an album with less than 5 photos? We recommend to create albums with at least 10 or more pictures.'));
        } else {
            confirm = true;
        }
        var selection = JSON.stringify(window.selectedResults);
        if (confirm) {
            $('#cat-loading-overlay').show();
            $.ajax({
                type: 'POST',
                url: selectionUploadURL,
                data: {
                    selection: selection,
                    album: album,
                    title: $('#cat-curator-add-album-name').val(),
                    subtitle: $('#cat-curator-add-album-description').val(),
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success: function (response) {
                    $('#cat-loading-overlay').hide();
                    if (response.error) {
                        $('#cat-curator-upload-error').show();
                        $('#cat-curator-upload-error-message').html(response.error);
                    } else {
                        $('#cat-curator-upload-error').hide();
                        $('#cat-curator-upload-error-message').html(window.gettext('System error'));
                        $('#cat-choose-albums-modal').modal('hide');
                        $('#cat-curator-add-album-name').val(null);
                        $('#cat-curator-add-album-description').val(null);
                        $('#cat-curator-create-new-album-checkbox').val(false);
                        for (var key in response.photos) {
                            if (response.photos.hasOwnProperty(key)) {
                                var targetDiv = $($('#cat-curator-selection-item-' + window.formatId(key)).find('.cat-curator-selection-feedback-row')[0]),
                                        item = response.photos[key];
                                if (item.error) {
                                    $(targetDiv.find('.alert-danger')[0]).html(item.error).show();
                                } else {
                                    $(targetDiv.find('.alert-success')[0]).html(item.message).show();
                                }
                            }
                        }
                    }
                    loadMyAlbums();
                    loadSelectableAlbums();
                },
                error: function () {
                    $('#cat-loading-overlay').hide();
                    $('#cat-curator-upload-error').show();
                }
            });
        }
    });
});