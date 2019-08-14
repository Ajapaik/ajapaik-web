'use strict';

/*globals $:false */

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

function getDetectionRectangle(rectangle, scaledRectangle) {
    var leftEdgeDistance = rectangle.x1;
    var topEdgeDistance = rectangle.y1;

    var width = (rectangle.x2 - rectangle.x1);
    var height = (rectangle.y2 - rectangle.y1);

    var rectangleId = 'ajapaik-object-rectangle-new-detection-' + new Date().getMilliseconds();
    var configuration = {
        placementFromLeftEdge: leftEdgeDistance,
        placementFromTopEdge: topEdgeDistance,
        width: width,
        height: height
    };

    return {
        id: rectangleId,
        rectangle: createNewDetectionRectangle(rectangleId, scaledRectangle, configuration)
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
            rectangle.hide();
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
        $(this).show();
    });
}
