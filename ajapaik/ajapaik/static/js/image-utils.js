'use strict';

/*globals $:false */

function hideControlsOnImage() {
    if (!window.isMobile) {
        $('.ajapaik-flip-photo-overlay-button').hide('fade', 250);
        $('.ajapaik-show-similar-photoview-overlay-button').hide('fade', 250);
        $('.ajapaik-show-rephotos-photoview-overlay-button').hide('fade', 250);
    }

    $('.ajapaik-photo-modal-previous-button').hide('fade', 250);
    $('.ajapaik-photo-modal-next-button').hide('fade', 250);
    $('.ajapaik-thumbnail-selection-icon').hide('fade', 250);
    $('.ajapaik-like-photo-overlay-button').hide('fade', 250);
}

function showControlsOnImage() {
    if (!window.isMobile) {
        $('.ajapaik-flip-photo-overlay-button').show('fade', 250);
        $('.ajapaik-show-similar-photoview-overlay-button').show('fade', 250);
        $('.ajapaik-show-rephotos-photoview-overlay-button').show('fade', 250);
    }

    $('.ajapaik-photo-modal-previous-button').show('fade', 250);
    $('.ajapaik-photo-modal-next-button').show('fade', 250);
    $('.ajapaik-thumbnail-selection-icon').show('fade', 250);
    $('.ajapaik-like-photo-overlay-button').show('fade', 250);
}

function disableMovingBetweenPictures() {
    $('.ajapaik-photo-modal-previous-button').css('pointer-events', 'none');
    $('.ajapaik-photo-modal-next-button').css('pointer-events', 'none');
}

function enableMovingBetweenPictures() {
    $('.ajapaik-photo-modal-previous-button').css('pointer-events', 'auto');
    $('.ajapaik-photo-modal-next-button').css('pointer-events', 'auto');
}

function disableImageSubmitControls() {
    $(document).off('click', '.ajapaik-face-recognition-form-remove-rectangle-button');
    $(document).off('click', '.ajapaik-face-recognition-form-submit-button');
    $(document).off('click', '.ajapaik-face-recognition-form-cancel-button');
}

function getDetectionRectangle(rectangle, imageAreaDimensions) {
    var leftEdgeDistance = rectangle.x1;
    var topEdgeDistance = rectangle.y1;

    var width = (rectangle.x2 - rectangle.x1);
    var height = (rectangle.y2 - rectangle.y1);

    var rectangleId = 'ajapaik-object-rectangle-new-detection-' + new Date().getMilliseconds();
    var configuration = {
        leftEdgeDistancePercentage: (leftEdgeDistance / imageAreaDimensions.width) * 100,
        topEdgeDistancePercentage: (topEdgeDistance / imageAreaDimensions.height) * 100,
        widthPercentage: (width / imageAreaDimensions.width) * 100,
        heightPercentage: (height / imageAreaDimensions.height) * 100,
    };

    return {
        id: rectangleId,
        rectangle: createNewDetectionRectangle(rectangleId, configuration)
    };
}

function togglePopover(popoverId) {
    setTimeout(function() {
        $('#' + popoverId).click();
    });
}

function hideDetectionRectanglesWithoutOpenPopover() {
    $('[data-is-detection-rectangle]').each(function() {
        var rectangle = $(this);

        var popoverSelector = '[data-popover-id="' + rectangle.attr('id') + '"]';
        var isPopoverOpen = $(popoverSelector).length > 0;

        if (!isPopoverOpen) {
            rectangle.css('visibility', 'hidden');
        }
    });
}

function closePopoversOnRectangleClick(event) {
    var popoverId = $(event.target).attr('id');
    closePopovers(popoverId);
}

function closePopovers(currentlyOpeningId) {
    $('[data-is-detection-rectangle=true]').each(function() {
        var rectangle = $(this);
        var rectangleId = rectangle.attr('id');

        if (rectangleId !== currentlyOpeningId) {
            rectangle.popover('hide');
        }
    });
}

function showDetectionRectangles() {
    $('[data-is-detection-rectangle]').each(function() {
        $(this).css('visibility', 'visible');
    });
}

function mirrorDetectionAnnotations() {
    $('[data-is-detection-rectangle]').each(function() {
        var el = $(this);

        var leftPosition = el[0].style.left;
        var rightPosition = el[0].style.right;

        el.css('right', leftPosition);
        el.css('left', rightPosition);
    });
}

function getDetectionRectangleScaledForOriginalImageSize(popoverRectangleId, imageAreaCurrentDimensions) {
    var popoverRectangleDimensions = document.getElementById(popoverRectangleId).getBoundingClientRect();

    var imageScaledDimensions = getImageScaledDimensions(imageAreaCurrentDimensions);

    var y1 = popoverRectangleDimensions.top - imageAreaCurrentDimensions.top;

    var x1 = window.photoModalCurrentPhotoFlipped
        ? imageAreaCurrentDimensions.width - (popoverRectangleDimensions.right - imageAreaCurrentDimensions.left - imageScaledDimensions.blackPaddingSizeOnOneSide)
        : (popoverRectangleDimensions.left - imageAreaCurrentDimensions.left - imageScaledDimensions.blackPaddingSizeOnOneSide);

    var rectangle = {
        x1: x1,
        y1: y1,
        x2: x1 + popoverRectangleDimensions.width,
        y2: y1 + popoverRectangleDimensions.height
    };

    var photoDimensions = {
        width: parseInt(imageAreaCurrentDimensions.width),
        height: parseInt(imageAreaCurrentDimensions.height)
    };

    var widthScale = window.currentPhotoOriginalWidth / imageScaledDimensions.scaledPhotoWidthWithoutPadding;
    var heightScale = window.currentPhotoOriginalHeight / photoDimensions.height;

    return {
        photoId: ObjectTagger.getPhotoId(),
        x1: rectangle.x1 * widthScale,
        y1: rectangle.y1 * heightScale,
        x2: rectangle.x2 * widthScale,
        y2: rectangle.y2 * heightScale
    };
}
