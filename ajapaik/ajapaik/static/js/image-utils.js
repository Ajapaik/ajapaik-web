'use strict';

/*globals $:false */

function hideControlsOnImage() {
    if (!window.isMobile) {
        $('.ajp-show-similar-photoview-overlay-button').hide('fade', 250);
        $('.ajp-show-rephotos-photoview-overlay-button').hide('fade', 250);
    }

    $('.ajp-photo-modal-previous-button').hide('fade', 250);
    $('.ajp-photo-modal-next-button').hide('fade', 250);
    $('.ajp-thumbnail-selection-icon').hide('fade', 250);
    $('.ajp-like-photo-overlay-button').hide('fade', 250);
}

function showControlsOnImage() {
    if (!window.isMobile) {
        $('.ajp-show-similar-photoview-overlay-button').show('fade', 250);
        $('.ajp-show-rephotos-photoview-overlay-button').show('fade', 250);
    }

    $('.ajp-photo-modal-previous-button').show('fade', 250);
    $('.ajp-photo-modal-next-button').show('fade', 250);
    $('.ajp-thumbnail-selection-icon').show('fade', 250);
    $('.ajp-like-photo-overlay-button').show('fade', 250);
}

function disableMovingBetweenPictures() {
    $('.ajp-photo-modal-previous-button').css('pointer-events', 'none');
    $('.ajp-photo-modal-next-button').css('pointer-events', 'none');
}

function enableMovingBetweenPictures() {
    $('.ajp-photo-modal-previous-button').css('pointer-events', 'auto');
    $('.ajp-photo-modal-next-button').css('pointer-events', 'auto');
}

function disableImageSubmitControls() {
    $(document).off('click', '.ajp-face-recognition-form-remove-rectangle-button');
    $(document).off('click', '.ajp-face-recognition-form-submit-button');
    $(document).off('click', '.ajp-face-recognition-form-cancel-button');
}

function getAnnotation(rectangle, imageAreaDimensions) {
    var leftEdgeDistance = rectangle.x1;
    var topEdgeDistance = rectangle.y1;

    var width = (rectangle.x2 - rectangle.x1);
    var height = (rectangle.y2 - rectangle.y1);

    var rectangleId = 'ajp-object-rectangle-new-detection-' + new Date().getMilliseconds();
    var configuration = {
        leftEdgeDistancePercentage: (leftEdgeDistance / imageAreaDimensions.width) * 100,
        topEdgeDistancePercentage: (topEdgeDistance / imageAreaDimensions.height) * 100,
        widthPercentage: (width / imageAreaDimensions.width) * 100,
        heightPercentage: (height / imageAreaDimensions.height) * 100,
    };

    return {
        id: rectangleId,
        rectangle: createNewAnnotation(rectangleId, configuration)
    };
}

function togglePopover(popoverId) {
    setTimeout(function() {
        $('#' + popoverId).click();
    });
}

function hideAnnotationsWithoutOpenPopover() {
    if (window.isMobile) {
        return;
    }

    $('[data-is-detection-rectangle]').each(function() {
        let rectangle = $(this);
        if ((!window.openPersonPopoverLabelIds ||
             !window.openPersonPopoverLabelIds.includes(rectangle.attr('data-annotation-identifier'))) &&
            (!window.openObjectPopoverLabelIds ||
             !window.openObjectPopoverLabelIds.includes(rectangle.attr('data-annotation-identifier')))) {

            let popoverSelector = '[data-popover-id="' + rectangle.attr('id') + '"]';
            let isPopoverOpen = $(popoverSelector).length > 0;

            if (!isPopoverOpen) {
                rectangle.css('visibility', 'hidden');
            }
        }
    });
}

function closePopoversOnAnnotationClick(event) {
    let popoverId = $(event.target).attr('id');
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

function moveAnnotations(element, isDisablingPopover) {
    if (window.isAnnotatingDisabled || window.isAnnotatingDisabledByButton) {
        return;
    }

    $('[data-is-detection-rectangle]').each(function() {
        var rectangle = $(this);
        rectangle.css('visibility', 'initial');

        if (isDisablingPopover) {
            rectangle.popover('disable');
            rectangle.data('open-popover-on-fullscreen-exit', false);
        } else {
            rectangle.popover('enable');
            var isOpeningFullScreenOnExit = rectangle.data('open-popover-on-fullscreen-exit');

            if (isOpeningFullScreenOnExit) {
                rectangle.popover('show');
            }
        }

        element.append(rectangle);
    });
}

function displayAnnotationsOnMouseLeave(event) {
    displayAnnotations(event.data.showPersons, event.data.showObjects);
}

function displayAnnotations(showPersons, showObjects) {
    if (window.isAnnotatingDisabled || window.isAnnotatingDisabledByButton) {
        return;
    }
    $('[data-is-detection-rectangle]').each(function() {
        if (showPersons && $(this).attr('data-annotation-identifier').includes('face')) {
            $(this).css('visibility', 'visible');
        }

        if (showObjects && $(this).attr('data-annotation-identifier').includes('object')) {
            $(this).css('visibility', 'visible');
        }
    });
}

function mirrorDetectionAnnotations() {
    $('[data-is-detection-rectangle]').each(function() {
        let el = $(this);

        let leftPosition = el[0].style.left;
        let rightPosition = el[0].style.right;

        el.css('right', leftPosition);
        el.css('left', rightPosition);
    });
}

function getAnnotationScaledForOriginalImageSize(popoverRectangleId, imageAreaCurrentDimensions) {
    var popoverElement = $('#' + popoverRectangleId);

    var topPosition = parseFloat(popoverElement.css('top'));

    var leftPosition = window.photoModalCurrentPhotoFlipped
        ? parseFloat(popoverElement.css('right'))
        : parseFloat(popoverElement.css('left'));

    var popoverWidth = parseFloat(popoverElement.css('width'));
    var popoverHeight = parseFloat(popoverElement.css('height'));

    var rectangle = {
        x1: leftPosition,
        y1: topPosition,
        x2: leftPosition + popoverWidth,
        y2: topPosition + popoverHeight
    };

    var photoDimensions = {
        width: parseInt(imageAreaCurrentDimensions.width),
        height: parseInt(imageAreaCurrentDimensions.height)
    };

    let height = window.currentPhotoOriginalHeight;
    let width = window.currentPhotoOriginalWidth;

    var heightScale = height / photoDimensions.height;
    var widthScale = width / photoDimensions.width;

    return {
        photoId: ObjectTagger.getPhotoId(),
        x1: rectangle.x1 * widthScale,
        y1: rectangle.y1 * heightScale,
        x2: rectangle.x2 * widthScale,
        y2: rectangle.y2 * heightScale
    };
}

function openMainPhotoToFullScreen(fullScreenContainer) {
    window.fullscreenEnabled = true;

    window.BigScreen.request(
        fullScreenContainer[0],
        function() {
            setTimeout(function() {
                drawAnnotationContainer(fullScreenContainer);
                copyAnnotateButtonToFullScreenView();
            }, 100);
        }
    );
}

function handleChromeJumping() {
    // Chrome jumps up https://code.google.com/p/chromium/issues/detail?id=142427

    if (window.lastScrollPosition) {
        setTimeout(function () {
            $(window).scrollTop(window.lastScrollPosition);
            window.lastScrollPosition = null;
        }, 500);
    }
}

function handleFullScreenClose(additionalFunction) {
    window.fullscreenEnabled = false;
    handleChromeJumping();

    if (additionalFunction) {
        additionalFunction();
    }
}

function addFullScreenExitListener(additionalFunction) {
     window.BigScreen.onexit = function () {
         handleFullScreenClose(additionalFunction);
     };
}

function disableAnnotations() {
    window.isAnnotatingDisabled = true;

    $('#person-annotations').addClass('ajp-button-disabled');
    $('#person-annotations > .ajp-pebble > a').addClass('ajp-button-disabled');
    $('#person-annotations > .ajp-pebble > i').addClass('ajp-button-disabled');
    $('#object-annotations').addClass('ajp-button-disabled');
    $('#object-annotations > .ajp-pebble > a').addClass('ajp-button-disabled');
    $('#object-annotations > .ajp-pebble > i').addClass('ajp-button-disabled');
    $('#add-new-subject-button').addClass('ajp-button-disabled');
    $('#mark-object-button > i').addClass('ajp-button-disabled');

    $('[data-is-detection-rectangle]').each(function() {
        $(this).css('visibility', 'hidden');
    });
}

function enableAnnotations() {
    if (window.isAnnotatingDisabledByButton) {
        return;
    }
    window.isAnnotatingDisabled = false;

    $('#person-annotations').removeClass('ajp-button-disabled');
    $('#person-annotations > .ajp-pebble > a').removeClass('ajp-button-disabled');
    $('#person-annotations > .ajp-pebble > i').removeClass('ajp-button-disabled');
    $('#object-annotations').removeClass('ajp-button-disabled');
    $('#object-annotations > .ajp-pebble > a').removeClass('ajp-button-disabled');
    $('#object-annotations > .ajp-pebble > i').removeClass('ajp-button-disabled');
    $('#add-new-subject-button').removeClass('ajp-button-disabled');
    $('#mark-object-button > i').removeClass('ajp-button-disabled');

    $('[data-is-detection-rectangle]').each(function() {
        $(this).css('visibility', '');
    });
}

