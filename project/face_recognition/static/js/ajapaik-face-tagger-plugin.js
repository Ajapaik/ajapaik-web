(function ($) {
    'use strict';
    /*global window*/
    /*global console*/
    /*global document*/
    /*global gettext*/
    /*global confirm*/
    /*global docCookies*/
    /*global setTimeout*/
    var AjapaikFaceTagger = function (node, options) {
        var that = this;
        this.node = node;
        this.options = $.extend({
            // Currently unused
        }, options);
        this.faces = [];
        this.$drawnFaceElements = [];
        this.$drawnFaceRemoveButtonElements = [];
        this.newRectangleX1 = null;
        this.newRectangleX2 = null;
        this.newRectangleY1 = null;
        this.newRectangleY2 = null;
        this.photoRealWidthAtTimeOfDrawing = null;
        this.photoRealHeightAtTimeOfDrawing = null;
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
            // TODO: Correct place for this?
            that.stopTagging();
            var payload = {
                photo: that.photo,
                x1: that.newRectangleX1,
                y1: that.newRectangleY1,
                x2: that.newRectangleX2,
                y2: that.newRectangleY2,
                seen_width: that.photoRealWidthAtTimeOfDrawing,
                seen_height: that.photoRealHeightAtTimeOfDrawing,
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
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
                    is_correct: false
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
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
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
            that.$drawnFaceRemoveButtonElements.forEach(function ($each) {
                $each.remove();
            });
            $('.popover').popover('hide');
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
                    }),
                    $faceRectangleRemoveButton = $('<div>', {
                        class: 'ajapaik-face-rectangle-remove',
                        data: {
                            id: face.id
                        },
                        css: {
                            position: 'absolute',
                            left: leftTop[0] - 10 + 'px',
                            top: leftTop[1] - 10 + 'px',
                            color: 'white',
                            cursor: 'pointer'
                        },
                        title: gettext('This rectangle is wrong, remove it!'),
                        html: '<i class="material-icons notranslate">close</i>'
                    });
                // TODO: Load form into this
                $faceRectangle.popover({
                    html: true,
                    title: gettext('Who is this?'),
                });
                $faceRectangle.on('shown.bs.popover', function () {
                    that.loadGuessFormHtml(face.id, divId);
                });
                that.$drawnFaceElements.push($faceRectangle);
                that.$drawnFaceRemoveButtonElements.push($faceRectangleRemoveButton);
                $faceRectangle.appendTo(node);
                $faceRectangleRemoveButton.appendTo(node);
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
            // FIXME
            //that.stopTagging();
            // Submit it right away, users can delete their rectangle if it's off
            that.submitRectangle();
        };
        this.initializeTagger();
    };
    AjapaikFaceTagger.prototype = {
        constructor: AjapaikFaceTagger,
        initializeTagger: function () {
            var that = this;
            // $(document).on('click', '.ajapaik-face-rectangle', function (e) {
            //     e.stopPropagation();
            //     var $this = $(this),
            //         id = $this.data('id');
            //     //faceRecognitionModal.modal();
            //     //faceRecognitionModal.find('#id_rectangle').val($(this).data('id'));
            // });
            $(document).on('click', '.ajapaik-face-rectangle-remove', function (e) {
                e.stopPropagation();
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
                var $form = $(this).parent(),
                    subject = $form.find('#id_subject').val(),
                    rectangle = $form.find('#id_rectangle').val();
                that.submitGuess(rectangle, subject);
            });
            // TODO: Cancel drawing
            // that.$UI.find('#ajp-face-tagger-cancel-button').attr('title', gettext('Cancel')).click(function (e) {
            //     e.preventDefault();
            //     if (typeof window.stopFaceTagger === 'function') {
            //         window.stopFaceTagger();
            //         if (typeof window.reportCloseFaceTagger === 'function') {
            //             window.reportCloseFaceTagger();
            //         }
            //     }
            // });
            // TODO: Some tutorial and hiding functionality for it?
            // if (docCookies.getItem('ajapaik_closed_face_tagger_instructions') === 'true') {
            //     that.$UI.find('#ajp-face-tagger-tutorial-well').hide();
            //     that.$UI.find('#ajp-face-tagger-open-tutorial-button').show();
            // }
            // that.$UI.find('#ajp-face-tagger-close-tutorial-button').click(function () {
            //     that.$UI.find('#ajp-face-tagger-tutorial-well').hide();
            //     that.$UI.find('#ajp-face-tagger-open-tutorial-button').show();
            //     docCookies.setItem('ajapaik_closed_face_tagger_instructions', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
            // });
            // that.$UI.find('#ajp-face-tagger-open-tutorial-button').click(function () {
            //     that.$UI.find('#ajp-face-tagger-tutorial-well').show();
            //     that.$UI.find('#ajp-face-tagger-open-tutorial-button').hide();
            //     if (typeof window.reportFaceTaggerOpenTutorial === 'function') {
            //         window.reportFaceTaggerOpenTutorial();
            //     }
            //     docCookies.setItem('ajapaik_closed_face_tagger_instructions', false, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
            // });
        },
        initializeFaceTaggerState: function (state) {
            var that = this;
            that.photo = state.photoId;
            // Make sure everything is loaded beforehand


            // $(document).on('click', '#ajapaik-face-recognition-modal-submit-button', function (e) {
            //     e.preventDefault();
            //     var $form = $('#ajapaik-face-recognition-modal').find('form'),
            //         rectangleId = $form.find('#id_rectangle').val(),
            //         subjectId = $form.find('#id_subject').val();
            //     // TODO: Cache this DOM element?
            //     $('#ajp-face-tagger-container').data('AjapaikFaceTagger').guessSubject(rectangleId, subjectId);
            // });
            // setTimeout(function () {
            //     that.$UI.find('#ajp-dater-input').focus();
            // }, 0);
        },
        // TODO: Move also to constructor?
        startTagging: function () {
            var that = this;
            setTimeout(function () {
                $(that.node).imgAreaSelect({
                    onSelectEnd: that.handleNewRectangleDrawn
                });
            }, 0);
        },
        stopTagging: function () {
            var that = this;
            $(that.node).imgAreaSelect({
                disable: true,
                hide: true
            });
        }
    };
    $.fn.AjapaikFaceTagger = function (options) {
        return this.each(function () {
            $(this).data('AjapaikFaceTagger', new AjapaikFaceTagger(this, options));
        });
    };
}(jQuery));