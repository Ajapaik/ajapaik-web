(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        $(document).on('keydown', function (e) {
            if (window.hotkeysActive) {
                if (window.isGame || window.isFrontpage) {
                    var buttons;
                    if (e.keyCode === 37) {
                        // left
                        buttons = $('.ajapaik-photo-modal-previous-button');
                        if (!window.nextPhotoLoading && buttons.length > 0) {
                            if (!$(buttons[0]).hasClass('disabled')) {
                                buttons[0].click();
                            }
                        }
                    } else if (e.keyCode === 39) {
                        // right
                        buttons = $('.ajapaik-photo-modal-next-button');
                        if (!window.nextPhotoLoading && buttons.length > 0) {
                            if (!$(buttons[0]).hasClass('disabled')) {
                                buttons[0].click();
                            }
                        }
                    }
                    if (e.keyCode === 32 && window.currentlySelectedPhotoId) {
                        // space
                        if (window.fullscreenEnabled) {
                            window.BigScreen.exit();
                            window.fullscreenEnabled = false;
                        }
                        if (!window.locationToolsOpen) {
                            $('#ajapaik-photo-modal-specify-location').click();
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
                            $('.ajapaik-game-specify-location-button')[0].click();
                        }
                    } else if (e.keyCode === 13) {
                        // enter
                        var geotagger = $('#ajp-geotagging-container').data('AjapaikGeotagger');
                        if (geotagger.guessingStarted) {
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
                                window.stopGuessLocation();
                            } else {
                                sp.setVisible(false);
                            }
                        } else {
                            window.stopGuessLocation();
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
                        if (!input.is(':focus')) {
                            input.focus();
                            setTimeout(function () {
                                input.val('');
                            }, 0);
                        }
                    }
                }
                if (window.isPhotoview && !window.locationToolsOpen && !window.datingFocused) {
                    var targets;
                    if (e.keyCode === 37) {
                        // left
                        targets = $('.ajapaik-photo-modal-previous-button');
                        if (targets.length > 0) {
                            targets[0].click();
                        }
                    } else if (e.keyCode === 39) {
                        // right
                        targets = $('.ajapaik-photo-modal-next-button');
                        if (targets.length > 0) {
                            targets[0].click();
                        }
                    }
                }
            }
        });
    });
}(jQuery));