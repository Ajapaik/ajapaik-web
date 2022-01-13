'use strict';

function initializeClosingPopoverWhenClickingOutsideOfPopover() {
  $('html').on('click', function (e) {
    var hasNotClickedAnnotation =
        typeof $(e.target).data('is-detection-rectangle') === 'undefined',
      hasNotClickedAnnotationControls =
        typeof $(e.target).data('is-detection-controls') === 'undefined',
      hasNotClickedSharePopoverEnablingElement =
        typeof $(e.target).data('is-popover-target') === 'undefined',
      hasNotClickedCategorizationPopoverEnablingElement =
        typeof $(e.target).data('is-categorization-button') === 'undefined' &&
        typeof $(e.target).parent().data('is-categorization-button') ===
          'undefined',
      hasNotClickedEditPopoverEnablingElement =
        typeof $(e.target).data('is-edit-button') === 'undefined' &&
        typeof $(e.target).parent().data('is-edit-button') === 'undefined',
      hasNotClickedAlbumPopoverEnablingElement = !e.target.matches(
        '.ajp-photo-album-link'
      ),
      hasNotClickedPersonAlbumPopoverEnablingElement = !e.target.matches(
        '#' +
          constants.elements.FACE_ANNOTATIONS_ID +
          ', #' +
          constants.elements.FACE_ANNOTATIONS_ID +
          ' [data-toggle="popover"], #' +
          constants.elements.FACE_ANNOTATIONS_ID +
          ' [data-toggle="popover"] *'
      ),
      hasNotClickedObjectPopoverEnablingElement = !e.target.matches(
        '#' +
          constants.elements.OBJECT_ANNOTATIONS_ID +
          ', #' +
          constants.elements.OBJECT_ANNOTATIONS_ID +
          ' [data-toggle="popover"], #' +
          constants.elements.OBJECT_ANNOTATIONS_ID +
          ' [data-toggle="popover"] *'
      );

    if (!$(e.target).parents().is('.popover')) {
      if (hasNotClickedAnnotation && hasNotClickedAnnotationControls) {
        $('[data-is-detection-rectangle]').popover('hide');
      }

      if (hasNotClickedSharePopoverEnablingElement) {
        $('#ajp-sharing-dropdown-button').popover('hide');
      }

      if (hasNotClickedCategorizationPopoverEnablingElement) {
        let id = $('#ajp-categorize-scene').attr('aria-describedby');
        let element = $('#' + id);
        if (id && element.length > 0) {
          element.popover('hide');
          if (typeof updatePhotoSuggestions === 'function') {
            updatePhotoSuggestions();
          }
        }
      }

      if (hasNotClickedEditPopoverEnablingElement) {
        let id = $('#ajp-iiif').attr('aria-describedby');
        let element = $('#' + id);
        if (id && element.length > 0) {
          element.popover('hide');
        }
      }

      if (hasNotClickedEditPopoverEnablingElement) {
        let id = $('#ajp-edit-picture').attr('aria-describedby');
        let fullScreenImage = $('#ajp-fullscreen-image');
        let element = $('#' + id);
        if (id && element.length > 0) {
          element.popover('hide');
          $('#ajp-modal-photo').removeClass();
          $('#ajp-photoview-main-photo').removeClass();
          fullScreenImage.removeClass();
          fullScreenImage.addClass('lasyloaded');
          $('#ajp-fullscreen-image-wrapper').removeClass();
          window.photoModalCurrentPhotoInverted = false;
          window.photoModalCurrentPhotoFlipped = false;
          refreshAnnotations();
          enableAnnotations();
          window.newIsPhotoFlipped =
            window.isPhotoFlipped !== undefined &&
            window.isPhotoFlipped !== 'undefined'
              ? window.isPhotoFlipped
              : window.isPhotoFlippedConsensus;
          window.newIsPhotoInverted =
            window.isPhotoInverted !== undefined &&
            window.isPhotoInverted !== 'undefined'
              ? window.isPhotoInverted
              : window.isPhotoInvertedConsensus;
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
        $('#' + constants.elements.OBJECT_ANNOTATIONS_ID + ' *').popover(
          'hide'
        );
      }
    }
  });
}

$(document).ready(initializeClosingPopoverWhenClickingOutsideOfPopover);
