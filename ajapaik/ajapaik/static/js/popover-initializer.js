'use strict';

function initializeClosingPopoverWhenClickingOutsideOfPopover() {
    $('html').on('click', function(e) {
        var hasNotClickedDetectionRectangle = typeof $(e.target).data('is-detection-rectangle') === 'undefined' ;
        var hasNotClickedDetectionRectangleControls = typeof $(e.target).data('is-detection-controls') === 'undefined' ;
        var hasNotClickedSharePopoverEnablingElement = typeof $(e.target).data('is-popover-target') === 'undefined';
        var hasNotClickedCategorizationPopoverEnablingElement = typeof $(e.target).data('is-categorization-button') === 'undefined' && typeof $(e.target).parent().data('is-categorization-button') === 'undefined';
        var hasNotClickedEditPopoverEnablingElement = typeof $(e.target).data('is-edit-button') === 'undefined' && typeof $(e.target).parent().data('is-edit-button') === 'undefined';

        if (!$(e.target).parents().is('.popover')) {
            if (hasNotClickedDetectionRectangle && hasNotClickedDetectionRectangleControls) {
                $('[data-is-detection-rectangle]').popover('hide');
            }

            if (hasNotClickedSharePopoverEnablingElement) {
                $('#ajp-sharing-dropdown-button').popover('hide');
            }

            if (hasNotClickedCategorizationPopoverEnablingElement) {
                let id = $('#ajp-categorize-scene').attr('aria-describedby');
                if (id && $('#' + id).length > 0) {
                    $('#' + id).popover('hide');
                    if(typeof updatePhotoSuggestions === 'function') {
                        updatePhotoSuggestions();
                    }
                }
            }

            if (hasNotClickedEditPopoverEnablingElement) {
                let id = $('#ajp-edit-picture').attr('aria-describedby');
                if (id && $('#' + id).length > 0) {
                    $('#' + id).popover('hide');
                    $('#ajp-modal-photo').removeClass();
                    $('#ajp-photoview-main-photo').removeClass();
                    $('#ajp-photoview-main-photo').removeClass();
                    $('#ajp-fullscreen-image').removeClass();
                    $('#ajp-fullscreen-image').addClass('lasyloaded');
                    $('#ajp-fullscreen-image-wrapper').removeClass();
                    window.photoModalCurrentPhotoInverted = false;
                    window.photoModalCurrentPhotoFlipped = false;
                    refreshAnnotations();
                    enableAnnotations();
                    window.newIsPhotoFlipped = window.isPhotoFlipped !== undefined && window.isPhotoFlipped !== 'undefined' ? window.isPhotoFlipped : window.isPhotoFlippedConsensus;
                    window.newIsPhotoInverted = window.isPhotoInverted !== undefined && window.isPhotoInverted !== 'undefined' ? window.isPhotoInverted : window.isPhotoInvertedConsensus;
                    window.newPhotoRotationDegrees = 'undefined';
                }
            }
        }
    });
}

$(document).ready(initializeClosingPopoverWhenClickingOutsideOfPopover);
