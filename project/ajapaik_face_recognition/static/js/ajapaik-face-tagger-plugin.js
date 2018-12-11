(function ($) {
    'use strict';
    /*global window*/
    /*global document*/
    /*global gettext*/
    /*global confirm*/
    /*global setTimeout*/
    var AjapaikFaceTagger = function (node, options) {
        var that = this;
        this.node = node;
        this.options = $.extend({
            // Currently unused
        }, options);
        this.faces = [];
        this.isInCropMode = false;
        this.$drawnFaceElements = [];
        this.newRectangleX1 = null;
        this.newRectangleX2 = null;
        this.newRectangleY1 = null;
        this.newRectangleY2 = null;
        this.photoRealWidthAtTimeOfDrawing = null;
        this.photoRealHeightAtTimeOfDrawing = null;
        this.currentlyOpenRectangleId = null;
        // TODO: Notify users they must be logged in to do any of this
        this.loadRectangles = function () {
            // TODO: Some kind of caching? Seems a bit wasteful to reload on each hover. Good enough for now I guess
            that.removeRectanglesAndButtons();
            $.ajax({
                type: 'GET',
                url: '/face-recognition/get-rectangles/' + that.photo + '/',
                success: function (response) {
                    that.faces = response;
                    that.drawRectangles();
                },
                error: function () {
                    $.notify(gettext('Failed to load faces, sorry.'), {type: 'danger'});
                }
            });
        };
        this.submitRectangle = function () {
            that.stopCropping();
            var payload = {
                photo: that.photo,
                x1: that.newRectangleX1,
                y1: that.newRectangleY1,
                x2: that.newRectangleX2,
                y2: that.newRectangleY2,
                seen_width: that.photoRealWidthAtTimeOfDrawing,
                seen_height: that.photoRealHeightAtTimeOfDrawing,
                csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
            };
            $.ajax({
                type: 'POST',
                url: '/face-recognition/add-rectangle/',
                data: payload,
                success: function (response) {
                    $.notify(gettext('Rectangle added, thanks!'), {type: 'success'});
                    // Attach to window to make sure it's persistent
                    // TODO: Investigate why state gets erased?
                    window.noConfirmRectangleId = response.id;
                    that.loadRectangles();
                },
                error: function () {
                    $.notify(gettext('Failed to record your rectangle, sorry.'), {type: 'danger'});
                }
            });
        };
        this.reportBadRectangle = function (id) {
            $.ajax({
                type: 'POST',
                url: '/face-recognition/add-rectangle-feedback/',
                data: {
                    rectangle: id,
                    is_correct: false,
                    csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
                },
                success: function (response) {
                    if (response.deleted) {
                        $.notify(gettext('Thanks for the feedback! Bad rectangle deleted.'), {type: 'success'});
                    } else {
                        $.notify(gettext('Thanks for the feedback!'), {type: 'success'});
                    }
                    that.loadRectangles();
                },
                error: function () {
                    $.notify(gettext('Failed to send your feedback, sorry.'), {type: 'danger'});
                }
            });
        };
        this.submitGuess = function (rectangleId, subjectId) {
            $.ajax({
                type: 'POST',
                url: '/face-recognition/guess-subject/',
                data: {
                    rectangle: rectangleId,
                    subject: subjectId,
                    csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
                },
                success: function () {
                    $.notify(gettext('Thanks you for your contribution!'), {type: 'success'});
                    that.loadRectangles();
                },
                error: function () {
                    $.notify(gettext('Failed to send your submission, sorry.'), {type: 'danger'});
                }
            });
        };
        this.removeRectanglesAndButtons = function () {
            that.$drawnFaceElements.forEach(function ($each) {
                $each.remove();
            });
            $('.popover').popover('hide');
            that.currentlyOpenRectangleId = null;
        };
        this.loadGuessFormHtml = function (rectangleId, responseDiv) {
            $.ajax({
                type: 'GET',
                url: '/face-recognition/guess-subject-form/' + rectangleId + '/',
                // Should be default but make sure
                cache: true,
                success: function (response) {
                    // TODO: Can this be simpler?
                    setTimeout(function () {
                        $('#' + responseDiv).siblings('.popover').children('.popover-content').html(response);
                    }, 0);
                },
                error: function () {
                    $.notify(gettext('Failed retrieving person tagging form, sorry.'), {type: 'danger'});
                }
            });
        };
        this.drawRectangles = function () {
            that.faces.forEach(function (face) {
                // (top, right, bottom, left)
                var currentPhotoActualDimensions = that.node.getBoundingClientRect(),
                    // Do scaling
                    widthScale = currentPhotoActualDimensions.width / window.currentPhotoOriginalWidth,
                    heightScale = currentPhotoActualDimensions.height / window.currentPhotoOriginalHeight,
                    leftTop = [face.coordinates[3] * widthScale, face.coordinates[0] * heightScale],
                    width = (face.coordinates[1] - face.coordinates[3]) * widthScale,
                    height = (face.coordinates[2] - face.coordinates[0]) * heightScale,
                    divId = 'ajapaik-face-rectangle-' + face.id,
                    $faceRectangle = $('<div>', {
                        id: divId,
                        class: 'ajapaik-face-rectangle',
                        data: {
                            id: face.id
                        },
                        css: {
                            position: 'absolute',
                            left: leftTop[0] + 'px',
                            top: leftTop[1] + 'px',
                            width: width + 'px',
                            height: height + 'px',
                            border: '3px solid white'
                        },
                        // TODO: If we know already, display peoples' names
                    });
                $faceRectangle.popover({
                    html: true,
                    title: gettext('Who is this?'),
                });
                $faceRectangle.on('show.bs.popover', function () {
                    // Hide other popovers from the page
                    $('.popover').popover('hide');
                });
                $faceRectangle.on('shown.bs.popover', function () {
                    that.$drawnFaceElements.forEach(function ($each) {
                        $each.hide();
                    });
                    $faceRectangle.show();
                    that.currentlyOpenRectangleId = face.id;
                    that.loadGuessFormHtml(face.id, divId);
                    setTimeout(function () {
                        $('#id_subject-autocomplete').focus();
                        $('#add_id_subject').show();
                    }, 300);

                });
                $faceRectangle.hover(function () {
                    that.$drawnFaceElements.forEach(function ($each) {
                        $each.hide();
                    });
                    $faceRectangle.show();
                }, function () {
                    that.$drawnFaceElements.forEach(function ($each) {
                        if (!that.currentlyOpenRectangleId) {
                            $each.show();
                        }
                    });
                });
                that.$drawnFaceElements.push($faceRectangle);
                $faceRectangle.appendTo(node);
            });
        };
        this.handleNewRectangleDrawn = function (img, selection) {
            var imgRealSize = img.getBoundingClientRect();
            that.newRectangleX1 = selection.x1;
            that.newRectangleX2 = selection.x2;
            that.newRectangleY1 = selection.y1;
            that.newRectangleY2 = selection.y2;
            that.photoRealWidthAtTimeOfDrawing = imgRealSize.width;
            that.photoRealHeightAtTimeOfDrawing = imgRealSize.height;
            that.submitRectangle();
        };
        this.initializeTagger();
    };
    AjapaikFaceTagger.prototype = {
        constructor: AjapaikFaceTagger,
        initializeTagger: function () {
            var that = this;
            // Avoid duplicate handlers
            $(document).off('click', '.ajapaik-face-recognition-form-remove-rectangle-button');
            $(document).off('click', '.ajapaik-face-recognition-form-submit-button');
            $(document).on('click', '.ajapaik-face-recognition-form-remove-rectangle-button', function (e) {
                e.stopPropagation();
                e.preventDefault();
                var id = $(this).data('id');
                if (window.noConfirmRectangleId == id) {
                    // Don't bother users with confirmations if they're deleting their own rectangle right away
                    that.reportBadRectangle(id);
                } else {
                    if (confirm(gettext('Are you sure you wish to have this face removed?'))) {
                        that.reportBadRectangle(id);
                    }
                }
            });
            $(document).on('click', '.ajapaik-face-recognition-form-submit-button', function (e) {
                e.stopPropagation();
                e.preventDefault();
                var $form = $(this).parent().parent(),
                    subject = $form.find('#id_subject').val(),
                    rectangle = $form.find('#id_rectangle').val();
                that.submitGuess(rectangle, subject);
            });
        },
        initializeFaceTaggerState: function (state) {
            var that = this;
            that.photo = state.photoId;
        },
        // TODO: Move also to constructor?
        startCropping: function () {
            var that = this;
            that.isInCropMode = true;
            setTimeout(function () {
                $(that.node).imgAreaSelect({
                    onSelectEnd: that.handleNewRectangleDrawn
                });
            }, 0);
        },
        stopCropping: function () {
            var that = this;
            that.isInCropMode = false;
            $('#ajapaik-full-screen-link').css('cursor', 'zoom-in');
            $(that.node).imgAreaSelect({
                disable: true,
                hide: true
            });
        },
        toggleCropping: function () {
            var that = this;
            $('#ajapaik-full-screen-link').css('cursor', 'crosshair');
            if (that.isInCropMode) {
                that.stopCropping();
            } else {
                that.startCropping();
            }
        }
    };
    $.fn.AjapaikFaceTagger = function (options) {
        return this.each(function () {
            $(this).data('AjapaikFaceTagger', new AjapaikFaceTagger(this, options));
        });
    };
}(jQuery));