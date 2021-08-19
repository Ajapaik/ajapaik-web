'use strict';

function initializeClosingPopoverWhenClickingOutsideOfPopover() {
    $('html').on('click', function(e) {
        var hasNotClickedAnnotation = typeof $(e.target).data('is-detection-rectangle') === 'undefined' ;
        var hasNotClickedAnnotationControls = typeof $(e.target).data('is-detection-controls') === 'undefined' ;
        var hasNotClickedSharePopoverEnablingElement = typeof $(e.target).data('is-popover-target') === 'undefined';
        var hasNotClickedCategorizationPopoverEnablingElement = typeof $(e.target).data('is-categorization-button') === 'undefined' && typeof $(e.target).parent().data('is-categorization-button') === 'undefined';
        var hasNotClickedEditPopoverEnablingElement = typeof $(e.target).data('is-edit-button') === 'undefined' && typeof $(e.target).parent().data('is-edit-button') === 'undefined';
        var hasNotClickedAlbumPopoverEnablingElement = !e.target.matches('.ajp-photo-album-link');
        var hasNotClickedPersonAlbumPopoverEnablingElement = !e.target.matches('#' + constants.elements.FACE_ANNOTATIONS_ID + ', #' + constants.elements.FACE_ANNOTATIONS_ID + ' [data-toggle="popover"], #' + constants.elements.FACE_ANNOTATIONS_ID + ' [data-toggle="popover"] *');
        var hasNotClickedObjectPopoverEnablingElement = !e.target.matches('#' + constants.elements.OBJECT_ANNOTATIONS_ID + ', #' + constants.elements.OBJECT_ANNOTATIONS_ID + ' [data-toggle="popover"], #' + constants.elements.OBJECT_ANNOTATIONS_ID + ' [data-toggle="popover"] *');

        if (!$(e.target).parents().is('.popover')) {
            if (hasNotClickedAnnotation && hasNotClickedAnnotationControls) {
                $('[data-is-detection-rectangle]').popover('hide');
            }

            if (hasNotClickedSharePopoverEnablingElement) {
                $('#ajp-sharing-dropdown-button').popover('hide');
            }

            if (hasNotClickedCategorizationPopoverEnablingElement) {
                let id = $('#ajp-categorize-scene').attr('aria-describedby');
                if (id && $('#' + id).length > 0) {
                    $('#' + id).popover('hide');
                    if (typeof updatePhotoSuggestions === 'function') {
                        updatePhotoSuggestions();
                    }
                }
            }

            if (hasNotClickedEditPopoverEnablingElement) {
                let id = $('#ajp-iiif').attr('aria-describedby');
                if (id && $('#' + id).length > 0) {
                     $('#ajp-iiif').popover('hide');
                }
            }

            if (hasNotClickedEditPopoverEnablingElement) {
                let id = $('#ajp-edit-picture').attr('aria-describedby');
                if (id && $('#' + id).length > 0) {
                    $('#' + id).popover('hide');
                    $('#ajp-modal-photo').removeClass();
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

            if (hasNotClickedAlbumPopoverEnablingElement) {
                $('.ajp-photo-album-link').popover('hide');
            }

            if (hasNotClickedPersonAlbumPopoverEnablingElement) {
                $('#' + constants.elements.FACE_ANNOTATIONS_ID + ' *').popover('hide');
                window.openPersonPopoverLabelIds = [];
                hideAnnotationsWithoutOpenPopover();
            }

            if (hasNotClickedObjectPopoverEnablingElement) {
                window.openObjectPopoverLabelIds = [];
                $('#' + constants.elements.OBJECT_ANNOTATIONS_ID + ' *').popover('hide');
            }
        }

    });
}

$(document).ready(initializeClosingPopoverWhenClickingOutsideOfPopover);
