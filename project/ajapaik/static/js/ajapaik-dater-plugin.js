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
            "<div class='panel panel-default' id='ajp-dater-panel'>",
                "<div class='panel-body'>",
                    "<div class='well'>",
                        "<span></span>",
                        "<button id='ajp-dater-close-tutorial-button'><i class='material-icons'>close</i></button>",
                    "</div>",
                    "<button id='ajp-dater-open-tutorial-button'><i class='material-icons'>info</i></button>",
                    "<form class='form' id='ajp-dater-form'>",
                    "    <div class='form-group'>",
                    "        <input id='ajp-dater-input' type='text' class='form-control' placeholder=''>",
                    "    </div>",
                    "   <div id='ajp-dater-feedback'></div>",
                    "<div class='btn-group' role='group'>",
                        "<button type='button' id='ajp-dater-cancel-button' class='btn btn-default'><i class='material-icons'>close</i></button>",
                        "<button type='submit' id='ajp-dater-submit-button' class='btn btn-default'><i class='material-icons'>check</i></button>",
                    "</div>",
                "</div>",
            "</div>"
        ].join('\n'));
        this.extractUserInput = function () {
            that.userInput = that.$UI.find('input').val().replace(/ /g,'');
            var idx,
                separator,
                parts;
            if (that.userInput.indexOf('-') > -1) {
                idx = that.userInput.indexOf('-');
                separator = '-';
            } else if (that.userInput.indexOf('..') > -1) {
                idx = that.userInput.indexOf('..');
                separator = '..';
            }
            if (idx > -1) {
                parts = that.userInput.split(separator);
                that.from = parts[0];
                that.to = parts[1];
                that.isRange = true;
            } else {
                that.from = that.userInput;
                that.to = null;
                that.isRange = false;
            }
        };
        this.hasGoodDashesOrDots = function () {
            var dashCount = (that.userInput.match(/-/g) || []).length,
                dotDotCount = (that.userInput.match(/\.\./g) || []).length;
            if (dashCount > 1 || dotDotCount > 1) {
                return false;
            } else if (dashCount > 0 && dotDotCount > 0) {
                return false;
            }
            return true;
        };
        this.extractApproximates = function () {
            if (that.from && that.from.indexOf('(') > -1 && that.from.indexOf(')') > -1) {
                that.fromApproximate = true;
                that.from = that.from.replace('(', '');
                that.from = that.from.replace(')', '');
            } else {
                that.fromApproximate = false;
            }
            if (that.to && that.to.indexOf('(') > -1 && that.to.indexOf(')') > -1) {
                that.toApproximate = true;
                that.to = that.to.replace('(', '');
                that.to = that.to.replace(')', '');
            } else {
                that.toApproximate = false;
            }
        };
        this.checkAndGetStringLengths = function () {
            if (that.from) {
                if (that.from.length === 4) {
                    that.fromLocalizationFormat = 'L';
                } else if (that.from.length === 7) {
                    that.fromLocalizationFormat = 'LL';
                } else if (that.from.length === 10) {
                    that.fromLocalizationFormat = 'LLL';
                } else {
                    return false;
                }
            }
            if (that.to) {
                if (that.to.length === 4) {
                    that.toLocalizationFormat = 'L';
                } else if (that.to.length === 7) {
                    that.toLocalizationFormat = 'LL';
                } else if (that.to.length === 10) {
                    that.toLocalizationFormat = 'LLL';
                } else {
                    return false;
                }
            }
            return true;
        };
        this.hasAtLeastOneDate = function () {
            return that.from || that.to;
        };
        this.endIsGreaterThanStart = function () {
            if (that.to && that.from) {
                return that.to > that.from;
            }
            return true;
        };
        this.checkAndGetValidDates = function () {
            var ok = false;
            if (that.from && that.from.length > 0) {
                that.from = moment(that.from);
                ok = that.from.isValid();
            }
            if (that.to && that.to.length > 0) {
                that.to = moment(that.to);
                ok = that.to.isValid();
            }
            return ok;
        };
        this.cleanAndValidate = function () {
            that.invalid = false;
            that.extractUserInput();
            if (that.hasGoodDashesOrDots()) {
                that.extractApproximates();
                if (that.checkAndGetStringLengths()) {
                    if (!that.checkAndGetValidDates()) {
                        that.invalid = true;
                    }
                    if (!that.hasAtLeastOneDate()) {
                        that.invalid = true;
                    }
                    if (!that.endIsGreaterThanStart()) {
                        that.invalid = true;
                    }
                } else {
                    that.invalid = true;
                }
            } else {
                that.invalid = true;
            }
        };
        this.giveFeedback = function () {
            that.cleanAndValidate();
            var formGroup = that.$UI.find('.form-group'),
                feedbackDiv = that.$UI.find('#ajp-dater-feedback'),
                submitButton = that.$UI.find('#ajp-dater-submit-button'),
                feedbackStr,
                fmt;
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
                if (that.isRange) {
                    if (that.from && that.to) {
                        if (that.fromApproximate && that.toApproximate) {
                            fmt = gettext('Between approximately %(from)s and approximately %(to)s');
                            feedbackStr = interpolate(fmt, {
                                from: that.from.locale(currentLocale).format(that.fromLocalizationFormat),
                                to: that.to.locale(currentLocale).format(that.toLocalizationFormat)
                            }, true);
                        } else if (that.fromApproximate) {
                            fmt = gettext('Between approximately %(from)s and %(to)s');
                            feedbackStr = interpolate(fmt, {
                                from: that.from.locale(currentLocale).format(that.fromLocalizationFormat),
                                to: that.to.locale(currentLocale).format(that.toLocalizationFormat)
                            }, true);
                        } else if (that.toApproximate) {
                            fmt = gettext('Between %(from)s and approximately %(to)s');
                            feedbackStr = interpolate(fmt, {
                                from: that.from.locale(currentLocale).format(that.fromLocalizationFormat),
                                to: that.to.locale(currentLocale).format(that.toLocalizationFormat)
                            }, true);
                        } else {
                            fmt = gettext('Between %(from)s and %(to)s');
                            feedbackStr = interpolate(fmt, {
                                from: that.from.locale(currentLocale).format(that.fromLocalizationFormat),
                                to: that.to.locale(currentLocale).format(that.toLocalizationFormat)
                            }, true);
                        }
                    } else if (that.from) {
                        if (that.fromApproximate) {
                            fmt = gettext('After approximately %(from)s');
                            feedbackStr = interpolate(fmt, {
                                from: that.from.locale(currentLocale).format(that.fromLocalizationFormat)
                            }, true);
                        } else {
                            fmt = gettext('After %(from)s');
                            feedbackStr = interpolate(fmt, {
                                from: that.from.locale(currentLocale).format(that.fromLocalizationFormat)
                            }, true);
                        }
                    } else if (that.to) {
                        if (that.toApproximate) {
                            fmt = gettext('Before approximately %(to)s');
                            feedbackStr = interpolate(fmt, {
                                to: that.to.locale(currentLocale).format(that.toLocalizationFormat)
                            }, true);
                        } else {
                            fmt = gettext('Before %(to)s');
                            feedbackStr = interpolate(fmt, {
                                to: that.to.locale(currentLocale).format(that.toLocalizationFormat)
                            }, true);
                        }
                    }
                } else {
                    if (that.from) {
                        if (that.fromApproximate) {
                            fmt = gettext('Approximately %(date)s');
                            feedbackStr = interpolate(fmt, {date: that.from.locale(currentLocale).format(that.fromLocalizationFormat)}, true);
                        } else {
                            feedbackStr = that.from.locale(currentLocale).format(that.fromLocalizationFormat) + '';
                        }
                    }
                }
            }
            feedbackDiv.html(feedbackStr);
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
                };
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
                if (that.from) {
                    payload.start = that.from.format('YYYY-MM-DD');
                }
                if (that.to) {
                    payload.end = that.to.format('YYYY-MM-DD');
                }
                if (payload.start || payload.end) {
                    $.ajax({
                        type: 'POST',
                        url: submitDatingURL,
                        data: payload,
                        success: function () {
                            if (typeof window.stopDater === 'function') {
                                window.stopDater();
                            }
                        },
                        error: function () {
                            $('#ajp-dater-feedback').html(gettext('Server received invalid data.'));
                        }
                    });
                }
            }
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
                clearTimeout(that.typingTimer);
                if ($(this).val()) {
                    that.typingTimer = setTimeout(that.giveFeedback, 500);
                }
            });
            that.$UI.find('#ajp-dater-cancel-button').attr('title', gettext('Cancel')).click(function (e) {
                e.preventDefault();
                if (typeof window.stopDater === 'function') {
                    window.stopDater();
                }
            });
            that.$UI.find('#ajp-dater-submit-button').attr('title', gettext('Submit')).click(function (e) {
                e.preventDefault();
                that.submit();
            });
            that.$UI.find('.well span').html('<ul><li>' + gettext('Use YYYY.MM.DD format (MM.DD not obligatory): <br/>1878 | 1902.02') + '</li><li>' + gettext('Mark date ranges or before/after with either "-" or "..": <br/>1910-1920 | 1978.05.20..1978.06.27 | -1920 | 1935..') + '</li><li>' + gettext('Approximate date in brackets: <br/>(1944) | (1940.05)..1941.08.21') + '</li></ul>');
            if (docCookies.getItem('ajapaik_closed_dater_instructions') === 'true') {
                that.$UI.find('.well').hide();
                that.$UI.find('#ajp-dater-open-tutorial-button').show();
            }
            that.$UI.find('#ajp-dater-close-tutorial-button').click(function () {
                that.$UI.find('.well').hide();
                that.$UI.find('#ajp-dater-open-tutorial-button').show();
                docCookies.setItem('ajapaik_closed_dater_instructions', true, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
            });
            that.$UI.find('#ajp-dater-open-tutorial-button').click(function () {
                that.$UI.find('.well').show();
                that.$UI.find('#ajp-dater-open-tutorial-button').hide();
                docCookies.setItem('ajapaik_closed_dater_instructions', false, 'Fri, 31 Dec 9999 23:59:59 GMT', '/', document.domain, false);
            });
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
            this.photo = state.photoId;
        }
    };
    $.fn.AjapaikDater = function (options) {
        return this.each(function () {
            $(this).data('AjapaikDater', new AjapaikDater(this, options));
        });
    };
}(jQuery));