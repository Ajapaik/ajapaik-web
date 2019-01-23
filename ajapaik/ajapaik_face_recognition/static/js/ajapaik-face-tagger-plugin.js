(function ($) {
    'use strict';
    /*global window*/
    /*global document*/
    /*global gettext*/
    /*global confirm*/
    /*global setTimeout*/
    /*global screen*/
    // TODO: Disable other hotkeys like dating while face tagging
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
        this.loadRectangles = function (idToClickAfterLoading) {
            // TODO: Some kind of caching? Seems a bit wasteful to reload on each hover. Good enough for now I guess
            that.removeRectanglesAndButtons();
            $.ajax({
                type: 'GET',
                url: '/face-recognition/get-rectangles/' + that.photo + '/',
                success: function (response) {
                    that.faces = response;
                    that.drawRectangles(idToClickAfterLoading);
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
                    $.notify(gettext('Annotation added, thanks!'), {type: 'success'});
                    // Attach to window to make sure it's persistent
                    // TODO: Investigate why state gets erased?
                    window.noConfirmRectangleId = response.id;
                    that.loadRectangles(response.id);
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
                        $.notify(gettext('Thank you! Bad rectangle deleted.'), {type: 'success'});
                    } else {
                        $.notify(gettext('Thank you!'), {type: 'success'});
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
                    subject_album: subjectId,
                    csrfmiddlewaretoken: window.docCookies.getItem('csrftoken')
                },
                success: function () {
                    $.notify(gettext('Thank you!'), {type: 'success'});
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
        this.drawRectangles = function (idToClickAfterDrawing) {
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
                    // TODO: How to make this trigger on hover all the while not breaking the hover functionality a few lines down?
                    trigger: 'click'
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
                        $('#add_id_subject_album').show();
                    }, 300);
                });
                // $faceRectangle.on('hidden.bs.popover', function () {
                //     that.currentlyOpenRectangleId = null;
                //     that.$drawnFaceElements.forEach(function ($each) {
                //         if (!that.currentlyOpenRectangleId) {
                //             $each.show();
                //         }
                //     });
                // });
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
            if (idToClickAfterDrawing) {
                setTimeout(function () {
                    $('#ajapaik-face-rectangle-' + idToClickAfterDrawing).click();
                }, 1000);
            }
        };
        this.handleNewRectangleDrawn = function (img, selection) {
            var imgRealSize = img.getBoundingClientRect();
            that.newRectangleX1 = selection.x1;
            that.newRectangleX2 = selection.x2;
            that.newRectangleY1 = selection.y1;
            that.newRectangleY2 = selection.y2;
            that.photoRealWidthAtTimeOfDrawing = parseInt(imgRealSize.width);
            that.photoRealHeightAtTimeOfDrawing = parseInt(imgRealSize.height);
            that.submitRectangle();
        };
        // FIXME: Copied from addanother.js because of how we implemented async popup form loading
        var id_to_windowname = function (text) {
            text = text.replace(/\./g, '__dot__');
            text = text.replace(/\-/g, '__dash__');
            text = text.replace(/\[/g, '__braceleft__');
            text = text.replace(/\]/g, '__braceright__');
            return text;
        };
        this.showAddAnotherPopup = function (triggeringLink) {
            var name = triggeringLink.attr('id').replace(/^add_/, '');
            name = id_to_windowname(name);
            var href = triggeringLink.attr('href');

            if (href.indexOf('?') === -1) {
                href += '?';
            }

            href += '&winName=' + name;

            var height = 500;
            var width = 800;
            var left = (screen.width / 2) - (width / 2);
            var top = (screen.height / 2) - (height / 2);
            var win = window.open(href, name, 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, copyhistory=no, width=' + width + ', height=' + height + ', top=' + top + ', left=' + left)

            function removeOverlay() {
                if (win.closed) {
                    $('#yourlabs_overlay').remove();
                } else {
                    setTimeout(removeOverlay, 500);
                }
            }

            $('body').append('<div id="yourlabs_overlay"></div');
            $('#yourlabs_overlay').click(function () {
                win.close();
                $(this).remove();
            });

            setTimeout(removeOverlay, 1500);

            win.focus();

            return false;
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
                    subject = $form.find('#id_subject_album').val(),
                    rectangle = $form.find('#id_rectangle').val();
                that.submitGuess(rectangle, subject);
            });
            // Had to be copied to be a global trigger from addanother.js
            $(document).on('click', '#add_id_subject_album', function (e) {
                e.preventDefault();
                e.stopPropagation();
                that.showAddAnotherPopup($(this));
            });
            $(document).on('keydown', function (e) {
                if (e.keyCode === 27) {
                    // escape
                    if (that.isInCropMode) {
                        // Whichever is present
                        $('#ajapaik-photoview-face-recognition-add-face-button').click();
                        $('#ajapaik-photo-modal-face-recognition-add-face-button').click();
                    }
                }
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
