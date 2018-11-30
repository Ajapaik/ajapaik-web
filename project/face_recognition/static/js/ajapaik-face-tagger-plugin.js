(function ($) {
    'use strict';
    /*global window*/
    /*global console*/
    /*global document*/
    /*global gettext*/
    /*global submitFaceRectangleURL*/
    /*global submitFaceRectangleFeedbackURL*/
    /*global submitFaceGuessURL*/
    /*global docCookies*/
    var AjapaikFaceTagger = function (node, options) {
        var that = this;
        this.node = node;
        this.options = $.extend({
            // Currently unused
        }, options);
        this.currentlyDrawnFaceRectangles = [];
        this.currentlyDrawnFaceRectangleRemoveButtons = [];
        this.imageContainer = null;
        this.imageElement = null;
        // TODO: Update tutorial text as to what the user must do next
        // TODO: Notify users they must be logged in to do any of this
        this.UI = $([
            "<div class='panel panel-default' id='ajp-face-tagger-panel'>",
            "   <div class='panel-body'>",
            "       <div class='well' id='ajp-face-tagger-tutorial-well'>",
            "           <span></span>",
            "           <button id='ajp-face-tagger-close-tutorial-button'><i class='material-icons notranslate'>close</i></button>",
            "       </div>",
            "       <div class='well hidden' id='ajp-face-tagger-anonymous-user-well'>",
            "           <i class='material-icons notranslate'>account_circle</i><span></span>",
            "       </div>",
            "       <button id='ajp-face-tagger-open-tutorial-button'><i class='material-icons notranslate'>info</i></button>",
            "       <div class='well' id='ajp-face-tagger-feedback-well'></div>",
            "       <form class='form' id='ajp-face-tagger-form'>",
            "           <div class='form-inline'>",
            "               <div class='form-group'>",
            "                   <input id='ajp-face-tagger-x1-input' type='text' class='form-control' placeholder=''>",
            "                   <input id='ajp-face-tagger-x2-input' type='text' class='form-control' placeholder=''>",
            "                   <input id='ajp-face-tagger-y1-input' type='text' class='form-control' placeholder=''>",
            "                   <input id='ajp-face-tagger-y2-input' type='text' class='form-control' placeholder=''>",
            "                   <input id='ajp-face-tagger-photo-real-width' type='text' class='form-control' placeholder=''>",
            "                   <input id='ajp-face-tagger-photo-real-height' type='text' class='form-control' placeholder=''>",
            "               </div>",
            "           </div>",
            "           <div id='ajp-face-tagger-feedback'></div>",
            "           <div class='btn-group' role='group'>",
            "               <button type='button' id='ajp-face-tagger-cancel-button' class='btn btn-default'><i class='material-icons notranslate'>close</i></button>",
            "               <button type='submit' id='ajp-face-tagger-submit-button' class='btn btn-default'><i class='material-icons notranslate'>check</i></button>",
            "           </div>",
            "       </form>",
            "   </div>",
            "</div>"
        ].join('\n'));
        this.giveFeedback = function () {
            var formGroup = that.$UI.find('.form-group'),
                feedbackDiv = that.$UI.find('#ajp-dater-feedback'),
                submitButton = that.$UI.find('#ajp-dater-submit-button'),
                feedbackStr;
            if (!that.disableFeedback) {
                if (that.invalid) {
                    formGroup.addClass('has-error');
                    submitButton.removeClass('btn-success');
                } else {
                    formGroup.removeClass('has-error');
                    submitButton.addClass('btn-success');
                }
                if (that.invalid) {
                    feedbackDiv.html(gettext('Invalid input, see help text.'));
                } else {
                    feedbackStr = that.generateDateString(that);
                }
                feedbackDiv.html(feedbackStr);
            }
        };
        this.submitRectangle = function () {
            //that.giveFeedback();
            var payload = {
                photo: that.photo,
                x1: that.$UI.find('#ajp-face-tagger-x1-input').val(),
                y1: that.$UI.find('#ajp-face-tagger-y1-input').val(),
                x2: that.$UI.find('#ajp-face-tagger-x2-input').val(),
                y2: that.$UI.find('#ajp-face-tagger-y2-input').val(),
                seen_width: that.$UI.find('#ajp-face-tagger-photo-real-width').val(),
                seen_height: that.$UI.find('#ajp-face-tagger-photo-real-height').val(),
                csrfmiddlewaretoken: docCookies.getItem('csrftoken')
            };
            $.ajax({
                type: 'POST',
                url: submitFaceRectangleURL,
                data: payload,
                success: function () {
                    // if (typeof window.updateDatings === 'function') {
                    //     window.updateDatings();
                    // }
                    //that.giveDatingSubmittedFeedback();
                    //that.$UI.find('#ajp-face-tagger-feedback').hide();
                    //that.$UI.find('#ajp-face-tagger-submit-button').hide();
                    //that.$UI.find('#ajp-face-tagger-input').hide();
                    //that.disableFeedback = true;
                    // TODO: This is easy for now, let's implement proper feedback-giving later
                    document.location.reload();
                },
                error: function () {
                    that.$UI.find('#ajp-face-tagger-feedback-well').hide();
                    $('#ajp-dater-feedback').html(gettext('Something went wrong sending your data.'));
                }
            });
        };
        this.loadRectangles = function () {
            $.ajax({
                type: 'GET',
                // FIXME: Assuming module is installed
                url: '/face-recognition/get-rectangles/' + that.photo,
                success: function (response) {
                    // if (typeof window.updateDatings === 'function') {
                    //     window.updateDatings();
                    // }
                    //that.giveDatingSubmittedFeedback();
                    //that.$UI.find('#ajp-face-tagger-feedback').hide();
                    //that.$UI.find('#ajp-face-tagger-submit-button').hide();
                    //that.$UI.find('#ajp-face-tagger-input').hide();
                    //that.disableFeedback = true;
                    // TODO: This is easy for now, let's implement proper feedback-giving later
                    document.location.reload();
                },
                error: function () {
                    that.$UI.find('#ajp-face-tagger-feedback-well').hide();
                    $('#ajp-dater-feedback').html(gettext('Something went wrong sending your data.'));
                }
            });
        };
        this.removeFaceRectangles = function () {
            var that = this;
            that.currentlyDrawnFaceRectangles.forEach(function ($each) {
                $each.remove();
            });
            that.currentlyDrawnFaceRectangleRemoveButtons.forEach(function ($each) {
                $each.remove();
            });
        };
            this.drawFaceRectangles = function () {
                var that = this;
                window.currentPhotoDetectedFaces.forEach(function (face) {
                    // (top, right, bottom, left)
                    var currentPhotoActualDimensions = mainPhotoContainer.get(0).getBoundingClientRect(),
                        // Do scaling
                        widthScale = currentPhotoActualDimensions.width / window.currentPhotoOriginalWidth,
                        heightScale = currentPhotoActualDimensions.height / window.currentPhotoOriginalHeight,
                        leftTop = [face.coordinates[3] * widthScale, face.coordinates[0] * heightScale],
                        width = (face.coordinates[1] - face.coordinates[3]) * widthScale,
                        height = (face.coordinates[2] - face.coordinates[0]) * heightScale,
                        $faceRectangle = $('<div>', {
                            class: 'ajapaik-photoview-detected-face',
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
                            title: gettext('Click to tell us who this is.')
                        }),
                        $faceRectangleRemoveButton = $('<div>', {
                            class: 'ajapaik-photoview-remove-detected-face',
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
                    window.currentlyDrawnFaceRectangles.push($faceRectangle);
                    window.currentlyDrawnFaceRectangleRemoveButtons.push($faceRectangleRemoveButton);
                    $faceRectangle.appendTo(mainPhotoContainer);
                    $faceRectangleRemoveButton.appendTo(mainPhotoContainer);
                });
            };
        this.giveDatingSubmittedFeedback = function (confirmation) {
            var fmt,
                feedbackStr;
            if (confirmation) {
                fmt = gettext('Confirming a dating earned you %(points)s points.');
                feedbackStr = interpolate(fmt, {
                    points: window.datingConfirmationPointsSetting
                }, true);
            } else {
                fmt = gettext('Submitting a dating earned you %(points)s points.');
                feedbackStr = interpolate(fmt, {
                    points: window.datingPointsSetting
                }, true);
            }
            that.$UI.find('#ajp-dater-feedback-well')
                .html('<h1>' + gettext('Thanks!') + '</h1><p>' + feedbackStr + '</p>').show();
        };
        this.$UI = $(this.node);
        this.$UI.html(this.UI);
        this.initializeTagger();
    };
    AjapaikFaceTagger.prototype = {
        constructor: AjapaikFaceTagger,
        initializeTagger: function () {
            var that = this;
            that.$UI.find('#ajp-face-tagger-cancel-button').attr('title', gettext('Cancel')).click(function (e) {
                e.preventDefault();
                if (typeof window.stopFaceTagger === 'function') {
                    window.stopFaceTagger();
                    if (typeof window.reportCloseFaceTagger === 'function') {
                        window.reportCloseFaceTagger();
                    }
                }
            });
            that.$UI.find('#ajp-face-tagger-submit-button').attr('title', gettext('Submit')).click(function (e) {
                e.preventDefault();
                that.submit();
            });
            that.$UI.find('#ajp-face-tagger-tutorial-well span').html('<ul><li>' + gettext('Drag a rectangle on the photo where you want a new face to be tagged. Please mark only the face, try not to include fancy hats, haircuts or necklines as this will confuse automatic detection later.') + '</li></ul>');
            if (docCookies.getItem('ajapaik_closed_face_tagger_instructions') === 'true') {
                that.$UI.find('#ajp-face-tagger-tutorial-well').hide();
                that.$UI.find('#ajp-face-tagger-open-tutorial-button').show();
            }
            that.$UI.find('#ajp-face-tagger-close-tutorial-button').click(function () {
                that.$UI.find('#ajp-face-tagger-tutorial-well').hide();
                that.$UI.find('#ajp-face-tagger-open-tutorial-button').show();
                docCookies.setItem('ajapaik_closed_face_tagger_instructions', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
            });
            that.$UI.find('#ajp-face-tagger-anonymous-user-well').find('span').html(gettext('You\'re anonymous'));
            that.$UI.find('#ajp-face-tagger-anonymous-user-well').find('i').click(function () {
                $('#ajapaik-header-profile-button').click();
            });
            that.$UI.find('#ajp-face-tagger-open-tutorial-button').click(function () {
                that.$UI.find('#ajp-face-tagger-tutorial-well').show();
                that.$UI.find('#ajp-face-tagger-open-tutorial-button').hide();
                if (typeof window.reportFaceTaggerOpenTutorial === 'function') {
                    window.reportFaceTaggerOpenTutorial();
                }
                docCookies.setItem('ajapaik_closed_face_tagger_instructions', false, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
            });
            $(document).on('click', '.imgareaselect-selection', function () {
                // As per requirements, the area is sent to the backend and name tagging activates when the user clicks
                // on their own specified rectangle (means they're okay with it)
                console.log('click');
                that.submitRectangle();
                that.loadRectangles();
                // TODO: trigger click on the rectangle the user just added
            });
        },
        handleFaceCoordinatesChanged: function (img, selection) {
            var that = window.faceTaggerReference,
                imgRealSize = img.getBoundingClientRect();
            that.$UI.find('#ajp-face-tagger-x1-input').val(selection.x1);
            that.$UI.find('#ajp-face-tagger-y1-input').val(selection.y1);
            that.$UI.find('#ajp-face-tagger-x2-input').val(selection.x2);
            that.$UI.find('#ajp-face-tagger-y2-input').val(selection.y2);
            that.$UI.find('#ajp-face-tagger-photo-real-width').val(imgRealSize.width);
            that.$UI.find('#ajp-face-tagger-photo-real-height').val(imgRealSize.height);
        },
        initializeFaceTaggerState: function (state, target) {
            var that = this,
                loginDiv = that.$UI.find('#ajp-face-tagger-anonymous-user-well');
            // In case some handler or the like overrides our 'this'
            window.faceTaggerReference = that;
            this.photo = state.photoId;
            setTimeout(function () {
                target.imgAreaSelect({
                    handles: true,
                    onSelectEnd: that.handleFaceCoordinatesChanged
                });
            }, 0);

            that.$UI.find('#ajp-face-tagger-submit-button').show();
            //that.$UI.find('#ajp-dater-input').show();
            that.$UI.find('#ajp-face-tagger-feedback-well').hide();
            if (userIsSocialConnected) {
                loginDiv.addClass('hidden');
            } else {
                loginDiv.removeClass('hidden');
            }
            // setTimeout(function () {
            //     that.$UI.find('#ajp-dater-input').focus();
            // }, 0);
        },
        stopTagging: function (target) {
            target.imgAreaSelect({
                disable: true
            });
        },
        // TODO: Move to constructor?
        reportBadRectangle: function (id) {
            var that = this;
            $.ajax({
                type: 'POST',
                url: submitFaceRectangleFeedbackURL,
                data: {
                    rectangle: id,
                    is_correct: false
                },
                success: function () {
                    document.location.reload();
                },
                error: function () {
                    that.$UI.find('#ajp-face-tagger-feedback-well').hide();
                    $('#ajp-face-tagger-feedback').html(gettext('Something went wrong sending your data.'));
                }
            });
        },
        guessSubject: function (rectangleId, subjectId) {
            var that = this;
            $.ajax({
                type: 'POST',
                url: submitFaceGuessURL,
                data: {
                    rectangle: rectangleId,
                    subject: subjectId,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success: function () {
                    // TODO: Don't reload, do updates to components async
                    document.location.reload();
                },
                error: function () {
                    //that.$UI.find('#ajp-face-tagger-feedback-well').hide();
                    $('#ajp-face-tagger-feedback').html(gettext('Something went wrong sending your data.'));
                }
            });
        }
    };
    $.fn.AjapaikFaceTagger = function (options) {
        return this.each(function () {
            $(this).data('AjapaikFaceTagger', new AjapaikFaceTagger(this, options));
        });
    };
}(jQuery));