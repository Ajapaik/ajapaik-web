(function ($) {
    'use strict';
    /*jslint nomen: true*/
    /*jslint browser: true*/
    $(document).ready(function () {
        $(document).on('keydown', function (e) {
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
                    if (window.locationToolsOpen) {
                        if (window.guessResponseReceived) {
                            $('.ajapaik-game-feedback-next-button')[0].click();
                        } else {
                            if (!window.streetPanorama.getVisible()) {
                                // No saving in Street View
                                $('.ajapaik-save-location-button')[0].click();
                            }
                        }
                    }
                } else if (e.keyCode === 27) {
                    // escape
                    if (window.locationToolsOpen) {
                        // Skipping photo on close Street View would be confusing
                        if (!window.streetPanorama.getVisible()) {
                            $('.ajapaik-game-next-photo-button')[0].click();
                        } else {
                            window.streetPanorama.setVisible(false);
                        }
                    } else {
                        $('#ajapaik-game-close-game-modal').click();
                    }
                } else if (e.keyCode === 38) {
                    // up arrow
                    window.showDescriptions();
                    window.hideDescriptionButtons();
                } else if (e.keyCode === 70) {
                    // f
                    $('#ajapaik-game-flip-photo-button').click();
                } else if (e.keyCode === 83) {
                    // s
                    var input = $('#pac-input');
                    if (!input.is(':focus')) {
                        input.focus();
                        setTimeout(function () {
                            input.val('');
                        }, 0);
                    }
                }
            }
        });
    });
}(jQuery));