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
                    // FIXME: Conflicts with search box
                    //if (window.locationToolsOpen) {
                    //    if (window.guessResponseReceived) {
                    //        $('.ajapaik-game-feedback-next-button')[0].click();
                    //    } else {
                    //        if (!window.streetPanorama.getVisible()) {
                    //            // No saving in Street View
                    //            $('.ajapaik-save-location-button')[0].click();
                    //        }
                    //    }
                    //}
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
        });
    });
}(jQuery));