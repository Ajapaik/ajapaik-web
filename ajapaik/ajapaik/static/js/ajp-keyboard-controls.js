(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        $(document).on('keydown', function (e) {
            if ($('input,textarea').is(':focus')) {
                return;
            }
            if (areHotkeysEnabled()) {
                if (window.isGame || window.isFrontpage) {
                    var buttons;
                    if (e.keyCode === constants.keyCodes.ARROW_LEFT) {
                        buttons = $('.ajp-photo-modal-previous-button');
                        if (!window.nextPhotoLoading && buttons.length > 0) {
                            if (!$(buttons[0]).hasClass('disabled')) {
                                buttons[0].click();
                            }
                        }
                    } else if (e.keyCode === constants.keyCodes.ARROW_RIGHT) {
                        buttons = $('.ajp-photo-modal-next-button');
                        if (!window.nextPhotoLoading && buttons.length > 0) {
                            if (!$(buttons[0]).hasClass('disabled')) {
                                buttons[0].click();
                            }
                        }
                    } else if (e.keyCode === constants.keyCodes.D) {
                        // d
                        $('#ajp-start-dating-button').click();
                    }
                    if (e.keyCode === 32 && window.currentlySelectedPhotoId) {
                        // space
                        if (window.fullscreenEnabled) {
                            window.BigScreen.exit();
                            window.fullscreenEnabled = false;
                        }
                        if (!window.locationToolsOpen) {
                            $('#ajp-photo-modal-specify-location').click();
                        }
                    }
                }
                if (window.isGame) {
                    if (e.keyCode === 32) {
                        // space
                        if (window.fullscreenEnabled) {
                            window.BigScreen.exit();
                            window.fullscreenEnabled = false;
                        }
                        if (!window.locationToolsOpen) {
                            $('.ajp-game-specify-location-button')[0].click();
                        }
                    } else if (e.keyCode === 13) {
                        // enter
                        var geotagger = $('#ajp-geotagging-container').data('AjapaikGeotagger');
                        if (geotagger.suggestionStarted) {
                            if (geotagger.feedbackMode) {
                                $('#ajp-geotagger-feedback-next-button').click();
                            } else {
                                if (!geotagger.streetPanorama.getVisible() && geotagger.firstMoveDone) {
                                    // No saving in Street View
                                    $('#ajp-geotagger-save-button').click();
                                }
                            }
                        }
                    } else if (e.keyCode === 27) {
                        // escape
                        if (window.locationToolsOpen) {
                            // Skipping photo on close Street View would be confusing
                            var sp = $('#ajp-geotagging-container').data('AjapaikGeotagger').streetPanorama;
                            if (!sp.getVisible()) {
                                window.stopSuggestionLocation();
                            } else {
                                sp.setVisible(false);
                            }
                        } else {
                            window.stopSuggestionLocation();
                        }
                    } else if (e.keyCode === 38) {
                        // up arrow
                        window.showDescriptions();
                        window.hideDescriptionButtons();
                    } else if (e.keyCode === 70 && !e.ctrlKey && !e.shiftKey && !e.altKey) {
                        // f
                    } else if (e.keyCode === 83) {
                        // s
                        var input = $('#ajp-geotagger-search-box');
                            input.focus();
                            setTimeout(function () {
                                input.val('');
                            }, 0);

                    }
                }
                if (window.isPhotoview && !window.locationToolsOpen && !window.datingFocused && !window.transcriptionFocused) {
                    var targets;
                    if (e.keyCode === 37) {
                        // left
                        targets = $('.ajp-photo-modal-previous-button');
                        if (targets.length > 0) {
                            targets[0].click();
                        }
                    } else if (e.keyCode === 39) {
                        // right
                        targets = $('.ajp-photo-modal-next-button');
                        if (targets.length > 0) {
                            targets[0].click();
                        }
                    } else if (e.keyCode === 68) {
                        // FIXME: Re-enable?
                        // d
                        // $('#ajp-start-dating-button').click();
                    }
                }

                if (window.isCompareView !== undefined && window.isCompareView === true) {
                    var targets;
                    if (e.keyCode === 49) {
                        // not similar
                        targets = $('#not_similar');
                        if (targets.length > 0) {
                            targets[0].click();
                        }
                    } else if (e.keyCode === 50) {
                        // similar
                        targets = $('#similar');
                        if (targets.length > 0) {
                            targets[0].click();
                        }
                    } else if (e.keyCode === 51) {
                        // duplicate
                        targets = $('#duplicate');
                        if (targets.length > 0) {
                            targets[0].click();
                        }
                    }
                }
            }
        });
    });
}(jQuery));