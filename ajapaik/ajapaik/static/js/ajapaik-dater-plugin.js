(function ($) {
    'use strict';
    /*global gettext*/
    /*global moment*/
    /*global submitDatingURL*/
    /*global stopDater*/
    /*global docCookies*/
    /*global interpolate*/
    /*global currentLocale*/
    /*global docCookies*/
    /*global userIsSocialConnected*/
    var AjapaikDater = function (node, options) {
        var that = this;
        this.node = node;
        this.options = $.extend({
            // Currently unused
        }, options);
        this.typingTimer = null;
        this.userInput = null;
        this.from = null;
        this.to = null;
        this.fromApproximate = false;
        this.toApproximate = false;
        this.fromLocalizationFormat = null;
        this.toLocalizationFormat = null;
        this.isRange = false;
        this.invalid = false;
        this.UI = $([
            "<div class='col-lg-6 col-md-8 col-sm-12 card' id='ajp-dater-panel'>",
            "   <div class='card-body'>",
            "       <div class='card pb-3' id='ajp-dater-previous-datings-card'>",
            "       </div>",
            "       <div class='card' id='ajp-dater-tutorial-card'>",
            "           <span></span>",
            "           <button id='ajp-dater-close-tutorial-button'><i class='material-icons notranslate'>close</i></button>",
            "       </div>",
            "       <div class='card d-none' id='ajp-dater-anonymous-user-card'>",
            "           <i class='material-icons notranslate'>account_circle</i><span></span>",
            "       </div>",
            "       <button id='ajp-dater-open-tutorial-button'><i class='material-icons notranslate'>info</i></button>",
            "       <div class='card' id='ajp-dater-feedback-card'></div>",
            "       <form class='form' id='ajp-dater-form'>",
            "           <div class='form-inline'>",
            "               <div class='form-group'>",
            "                   <input id='ajp-dater-input' type='text' class='form-control' placeholder=''>",
            "                   <div class='btn' id='ajp-dater-toggle-comment-button'><i class='material-icons notranslate'>comment</i></div>",
            "               </div>",
            "           </div>",
            "           <div id='ajp-dater-feedback'></div>",
            "           <input class='form-control d-none' placeholder='' type='text' id='ajp-dater-comment'>",
            "           <div class='btn-group w-100' role='group'>",
            "               <button type='button' id='ajp-dater-cancel-button' class='btn btn-danger w-50'><i class='material-icons notranslate'>close</i></button>",
            "               <button type='submit' id='ajp-dater-submit-button' class='btn btn-success w-50'><i class='material-icons notranslate'>check</i></button>",
            "           </div>",
            "       </form>",
            "   </div>",
            "</div>"
        ].join('\n'));
        this.extractUserInput = function (input) {
            var idx,
                separator,
                parts,
                output = {
                    raw: input
                };
            that.userInput = input;
            if (input.indexOf('-') > -1) {
                idx = input.indexOf('-');
                separator = '-';
            } else if (input.indexOf('..') > -1) {
                idx = input.indexOf('..');
                separator = '..';
            }
            if (idx > -1) {
                parts = input.split(separator);
                output.from = parts[0];
                output.to = parts[1];
                output.isRange = true;
            } else {
                output.from = input;
                output.to = null;
                output.isRange = false;
            }
            return output;
        };
        this.hasGoodDashesOrDots = function (input) {
            var dashCount = (input.raw.match(/-/g) || []).length,
                dotDotCount = (input.raw.match(/\.\./g) || []).length;
            if (dashCount > 1 || dotDotCount > 1) {
                return false;
            }
            return !(dashCount > 0 && dotDotCount > 0);
        };
        this.extractApproximates = function (input) {
            if (input.from && input.from.indexOf('(') > -1 && input.from.indexOf(')') > -1) {
                input.fromApproximate = true;
                input.from = input.from.replace('(', '');
                input.from = input.from.replace(')', '');
            } else {
                input.fromApproximate = false;
            }
            if (input.to && input.to.indexOf('(') > -1 && input.to.indexOf(')') > -1) {
                input.toApproximate = true;
                input.to = input.to.replace('(', '');
                input.to = input.to.replace(')', '');
            } else {
                input.toApproximate = false;
            }
            return input;
        };
        this.calculateDateFormats = function (input) {
            if (input.from) {
                if (input.from.length === 4) {
                    input.fromLocalizationFormat = 'L';
                } else if (input.from.length === 7) {
                    input.fromLocalizationFormat = 'LL';
                } else if (input.from.length === 10) {
                    input.fromLocalizationFormat = 'LLL';
                }
            }
            if (input.to) {
                if (input.to.length === 4) {
                    input.toLocalizationFormat = 'L';
                } else if (input.to.length === 7) {
                    input.toLocalizationFormat = 'LL';
                } else if (input.to.length === 10) {
                    input.toLocalizationFormat = 'LLL';
                }
            }
            return input;
        };
        this.hasAtLeastOneDate = function (input) {
            return input.from || input.to;
        };
        this.endIsGreaterThanStart = function (input) {
            if (input.to && input.from) {
                return input.to > input.from;
            }
            return true;
        };
        this.getValidDates = function (input) {
            var from_ok = true,
                to_ok = true;
            if (input.from && input.from.length > 0) {
                input.from = moment(input.from, 'YYYY.MM.DD');
                from_ok = input.from.isValid();
            }
            if (input.to && input.to.length > 0) {
                input.to = moment(input.to, 'YYYY.MM.DD');
                to_ok = input.to.isValid();
            }
            input.ok = from_ok && to_ok;
            return input;
        };
        this.cleanAndValidate = function () {
            var userInput = that.extractUserInput(that.$UI.find('input').val().replace(/ /g, ''));
            that.invalid = false;
            if (that.hasGoodDashesOrDots(userInput)) {
                userInput = that.extractApproximates(userInput);
                userInput = that.calculateDateFormats(userInput);
                if (userInput.toLocalizationFormat || userInput.fromLocalizationFormat) {
                    userInput = that.getValidDates(userInput);
                    if (!userInput.ok) {
                        that.invalid = true;
                    }
                    if (!that.hasAtLeastOneDate(userInput)) {
                        that.invalid = true;
                    }
                    if (!that.endIsGreaterThanStart(userInput)) {
                        that.invalid = true;
                    }
                } else {
                    that.invalid = true;
                }
            } else {
                that.invalid = true;
            }
            if (!that.invalid) {
                that.to = userInput.to;
                that.from = userInput.from;
                that.toApproximate = userInput.toApproximate;
                that.fromApproximate = userInput.fromApproximate;
                that.isRange = userInput.isRange;
                that.fromLocalizationFormat = userInput.fromLocalizationFormat;
                that.toLocalizationFormat = userInput.toLocalizationFormat;
            }
        };
        this.generateDateString = function (data) {
            var fmt,
                feedbackStr;
            if (data.isRange) {
                if (data.from && data.to) {
                    if (data.fromApproximate && data.toApproximate) {
                        fmt = gettext('Between approximately %(from)s and approximately %(to)s');
                        feedbackStr = interpolate(fmt, {
                            from: data.from.locale(currentLocale).format(data.fromLocalizationFormat),
                            to: data.to.locale(currentLocale).format(data.toLocalizationFormat)
                        }, true);
                    } else if (data.fromApproximate) {
                        fmt = gettext('Between approximately %(from)s and %(to)s');
                        feedbackStr = interpolate(fmt, {
                            from: data.from.locale(currentLocale).format(data.fromLocalizationFormat),
                            to: data.to.locale(currentLocale).format(data.toLocalizationFormat)
                        }, true);
                    } else if (data.toApproximate) {
                        fmt = gettext('Between %(from)s and approximately %(to)s');
                        feedbackStr = interpolate(fmt, {
                            from: data.from.locale(currentLocale).format(data.fromLocalizationFormat),
                            to: data.to.locale(currentLocale).format(data.toLocalizationFormat)
                        }, true);
                    } else {
                        fmt = gettext('Between %(from)s and %(to)s');
                        feedbackStr = interpolate(fmt, {
                            from: data.from.locale(currentLocale).format(data.fromLocalizationFormat),
                            to: data.to.locale(currentLocale).format(data.toLocalizationFormat)
                        }, true);
                    }
                } else if (data.from) {
                    if (data.fromApproximate) {
                        fmt = gettext('After approximately %(from)s');
                        feedbackStr = interpolate(fmt, {
                            from: data.from.locale(currentLocale).format(data.fromLocalizationFormat)
                        }, true);
                    } else {
                        fmt = gettext('After %(from)s');
                        feedbackStr = interpolate(fmt, {
                            from: data.from.locale(currentLocale).format(data.fromLocalizationFormat)
                        }, true);
                    }
                } else if (data.to) {
                    if (data.toApproximate) {
                        fmt = gettext('Before approximately %(to)s');
                        feedbackStr = interpolate(fmt, {
                            to: data.to.locale(currentLocale).format(data.toLocalizationFormat)
                        }, true);
                    } else {
                        fmt = gettext('Before %(to)s');
                        feedbackStr = interpolate(fmt, {
                            to: data.to.locale(currentLocale).format(data.toLocalizationFormat)
                        }, true);
                    }
                }
            } else {
                if (data.from) {
                    if (data.fromApproximate) {
                        fmt = gettext('Approximately %(date)s');
                        feedbackStr = interpolate(fmt, {date: data.from.locale(currentLocale).format(data.fromLocalizationFormat)}, true);
                    } else {
                        feedbackStr = data.from.locale(currentLocale).format(data.fromLocalizationFormat).toString();
                    }
                }
            }
            return feedbackStr;
        };
        this.giveFeedback = function () {
            that.cleanAndValidate();
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
        this.getAccuracyID = function (payload) {
            if (that.fromLocalizationFormat === 'LLL') {
                payload.start_accuracy = 0;
            } else if (that.fromLocalizationFormat === 'LL') {
                payload.start_accuracy = 1;
            } else if (that.fromLocalizationFormat === 'L') {
                payload.start_accuracy = 2;
            }
            if (that.toLocalizationFormat === 'LLL') {
                payload.end_accuracy = 0;
            } else if (that.toLocalizationFormat === 'LL') {
                payload.end_accuracy = 1;
            } else if (that.toLocalizationFormat === 'L') {
                payload.end_accuracy = 2;
            }
            return payload;
        };
        this.submitConfirmation = function (id) {
            if (typeof window.reportDaterConfirmSubmit === 'function') {
                window.reportDaterConfirmSubmit();
            }
            $.ajax({
                type: 'POST',
                url: submitDatingURL,
                data: {
                    id: id,
                    csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                },
                success: function () {
                    if (typeof window.updateDatings === 'function') {
                        window.updateDatings();
                    }
                    that.giveDatingSubmittedFeedback(true);
                    that.$UI.find('#ajp-dater-feedback').hide();
                    that.disableFeedback = true;
                },
                error: function () {
                    that.$UI.find('#ajp-dater-feedback-card').hide();
                    $('#ajp-dater-feedback').html(gettext('Server received invalid data.'));
                }
            });
        };
        this.submit = function () {
            that.giveFeedback();
            if (!that.invalid) {
                var payload = {
                        photo: that.photo,
                        raw: that.userInput,
                        start_approximate: that.fromApproximate,
                        end_approximate: that.toApproximate,
                        csrfmiddlewaretoken: docCookies.getItem('csrftoken')
                    },
                    comment = that.$UI.find('#ajp-dater-comment').val();
                if (comment) {
                    payload.comment = comment;
                }
                payload = that.getAccuracyID(payload);
                if (that.from) {
                    payload.start = that.from.format('YYYY-MM-DD');
                }
                if (that.to) {
                    payload.end = that.to.format('YYYY-MM-DD');
                }
                if (payload.comment && typeof window.reportDaterSubmitWithComment === 'function') {
                    window.reportDaterSubmitWithComment();
                } else if (typeof window.reportDaterSubmit === 'function') {
                    window.reportDaterSubmit();
                }
                if (payload.start || payload.end) {
                    $.ajax({
                        type: 'POST',
                        url: submitDatingURL,
                        data: payload,
                        success: function () {
                            if (typeof window.updateDatings === 'function') {
                                window.updateDatings();
                            }
                            that.giveDatingSubmittedFeedback();
                            that.$UI.find('#ajp-dater-feedback').hide();
                            that.$UI.find('#ajp-dater-submit-button').hide();
                            that.$UI.find('#ajp-dater-comment').hide();
                            that.$UI.find('#ajp-dater-input').hide();
                            that.$UI.find('#ajp-dater-toggle-comment-button').hide();
                            that.$UI.find('#ajp-dater-previous-datings-card').show();
                            that.disableFeedback = true;
                        },
                        error: function () {
                            that.$UI.find('#ajp-dater-feedback-card').hide();
                            $('#ajp-dater-feedback').html(gettext('Server received invalid data.'));
                        }
                    });
                }
            }
        };
        this.buildPreviousDatingsDiv = function (datings) {
            var userStr,
                commentStr,
                reparsedInput,
                previousDatings = that.$UI.find('#ajp-dater-previous-datings-card'),
                addClass;
            previousDatings.empty();
            $.each(datings, function (k, v) {
                userStr = '';
                commentStr = '';
                if (v.this_user_has_confirmed) {
                    addClass = ' done';
                } else {
                    addClass = '';
                }
                if (v.comment) {
                    commentStr = '<i>\"' + v.comment + '\"</i>';
                }
                if (v.fb_name) {
                    userStr = v.fb_name;
                } else if (v.google_plus_name) {
                    userStr = v.google_plus_name;
                } else if (v.full_name) {
                    userStr = v.full_name;
                } else {
                    userStr = gettext('Anonymous user');
                }
                reparsedInput = that.getValidDates(that.calculateDateFormats(that.extractApproximates(that.extractUserInput(v.raw))));
                previousDatings.append('<div><b>' + userStr + '</b>: ' + that.generateDateString(reparsedInput) + ' ' + commentStr + '<span class="badge" style="left:0px;">' + v.confirmation_count + '</span><i onclick="window.confirmDating(' + v.id + ')" class="material-icons notranslate ajp-dater-confirm-button' + addClass + '" data-id="' + v.id + '" title="' + gettext("Confirm dating") + '">thumb_up</i></div>');
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
            that.$UI.find('#ajp-dater-feedback-card')
                .html('<h1>' + gettext('Thanks!') + '</h1><p>' + feedbackStr + '</p>').show();
        };
        this.$UI = $(this.node);
        this.$UI.html(this.UI);
        this.initializeDater();
    };
    AjapaikDater.prototype = {
        constructor: AjapaikDater,
        initializeDater: function () {
            var that = this;
            that.$UI.find('input').attr('placeholder', gettext('YYYY.MM.DD')).on('change textInput input', function () {
                that.disableFeedback = false;
                that.$UI.find('#ajp-dater-feedback').show();
                clearTimeout(that.typingTimer);
                that.typingTimer = setTimeout(that.giveFeedback, 1000);
            }).on('focus', function () {
                window.datingFocused = true;
            }).on('blur', function () {
                window.datingFocused = false;
            });
            that.$UI.find('#ajp-dater-cancel-button').attr('title', gettext('Cancel')).click(function (e) {
                e.preventDefault();
                if (typeof window.stopDater === 'function') {
                    window.stopDater();
                    if (typeof window.reportCloseDater === 'function') {
                        window.reportCloseDater();
                    }
                }
            });
            that.$UI.find('#ajp-dater-submit-button').attr('title', gettext('Submit')).click(function (e) {
                e.preventDefault();
                that.submit();
            });
            that.$UI.find('#ajp-dater-comment').on('focus', function () {
                window.datingFocused = true;
            }).on('blur', function () {
                window.datingFocused = false;
            }).attr('placeholder', gettext('Comment your dating'));
            that.$UI.find('#ajp-dater-toggle-comment-button').click(function (e) {
                e.preventDefault();
                var target = that.$UI.find('#ajp-dater-comment');
                target.toggleClass('d-none');
                if (!target.hasClass('d-none') && typeof window.reportDaterOpenComment === 'function') {
                    window.reportDaterOpenComment();
                }
            });
            that.$UI.find('#ajp-dater-tutorial-card span').html('<ul><li>' + gettext('Use YYYY.MM.DD format (MM.DD not obligatory)') + ':<br/><span class="ajp-italic">' + gettext('1878 | 1902.02') + '</span></li><li>' + gettext('Mark date ranges or before/after with either "-" or ".."') + ':<br/><span class="ajp-italic">' + gettext('1910-1920 | 1978.05.20..1978.06.27 | -1920 | 1935..') + '</span></li><li>' + gettext('Approximate date in brackets') + ':<br/><span class="ajp-italic">' + gettext('(1944) | (1940.05)..1941.08.21)') + '</span></li></ul>');
            if (docCookies.getItem('ajapaik_closed_dater_instructions') === 'true') {
                that.$UI.find('#ajp-dater-tutorial-card').hide();
                that.$UI.find('#ajp-dater-open-tutorial-button').show();
            }
            that.$UI.find('#ajp-dater-close-tutorial-button').click(function () {
                that.$UI.find('#ajp-dater-tutorial-card').hide();
                that.$UI.find('#ajp-dater-open-tutorial-button').show();
                docCookies.setItem('ajapaik_closed_dater_instructions', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
            });
            that.$UI.find('#ajp-dater-anonymous-user-card').find('span').html(gettext('You\'re anonymous'));
            that.$UI.find('#ajp-dater-anonymous-user-card').find('i').click(function () {
                window.openPhotoUploadModal();
            });
            that.$UI.find('#ajp-dater-open-tutorial-button').click(function () {
                that.$UI.find('#ajp-dater-tutorial-card').show();
                that.$UI.find('#ajp-dater-open-tutorial-button').hide();
                if (typeof window.reportDaterOpenTutorial === 'function') {
                    window.reportDaterOpenTutorial();
                }
                docCookies.setItem('ajapaik_closed_dater_instructions', false, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
            });
            window.confirmDating = function (id) {
                if (typeof window.reportDaterConfirmSubmit === 'function') {
                    window.reportDaterConfirmSubmit();
                }
                that.submitConfirmation(id);
            };
            // TODO: More generic implementation
            moment.locale('et', {
                longDateFormat: {
                    LLL: 'D. MMMM YYYY',
                    LL: 'MMMM YYYY',
                    L: 'YYYY'
                }
            });
            moment.locale('fi', {
                longDateFormat: {
                    LLL: 'Do MMMM[ta] YYYY',
                    LL: 'MMMM[ta] YYYY',
                    L: 'YYYY'
                }
            });
            moment.locale('en', {
                longDateFormat: {
                    LLL: 'D MMMM YYYY',
                    LL: 'MMMM YYYY',
                    L: 'YYYY'
                }
            });
        },
        initializeDaterState: function (state) {
            var that = this,
                loginDiv = that.$UI.find('#ajp-dater-anonymous-user-card'),
                previousDatings = that.$UI.find('#ajp-dater-previous-datings-card');
            this.photo = state.photoId;
            that.$UI.find('#ajp-dater-submit-button').show();
            that.$UI.find('#ajp-dater-input').show();
            that.$UI.find('#ajp-dater-toggle-comment-button').show();
            that.$UI.find('#ajp-dater-feedback-card').hide();
            if (userIsSocialConnected) {
                loginDiv.addClass('d-none');
            } else {
                loginDiv.removeClass('d-none');
            }
            if (state.previousDatings.length > 0) {
                that.buildPreviousDatingsDiv(state.previousDatings);
                previousDatings.show();
            } else {
                previousDatings.hide();
            }
            setTimeout(function () {
                that.$UI.find('#ajp-dater-input').focus();
            }, 0);
        }
    };
    $.fn.AjapaikDater = function (options) {
        return this.each(function () {
            $(this).data('AjapaikDater', new AjapaikDater(this, options));
        });
    };
}(jQuery));