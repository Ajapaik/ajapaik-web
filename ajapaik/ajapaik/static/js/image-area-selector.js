'use strict';

var ImageAreaSelector = (function () {
    var imageArea = null;
    var initialClickX = null;
    var initialClickY = null;
    var currentMouseX = null;
    var currentMouseY = null;
    var imageAreaLeft = null;
    var imageAreaTop = null;
    var isSelecting = false;

    var clickListener = null;
    var mouseMoveListener = null;
    var cancelListenerOnAreaSelect = null;

    function getCurrentImageArea() {
        if (window.fullscreenEnabled) {
            return $('#' + constants.elements.ANNOTATION_CONTAINER_ID_ON_IMAGE);
        }

        return imageArea;
    }

    function resetValues() {
        initialClickX = null;
        initialClickY = null;
        currentMouseX = null;
        currentMouseY = null;
        imageAreaLeft = null;
        imageAreaTop = null;
        isSelecting = false;

        clickListener = null;
        mouseMoveListener = null;
    }

    function resizeBox(leftPosition, topPosition, boxWidth, boxHeight) {
        var imageSelectionArea = $('#' + constants.elements.IMAGE_SELECTION_AREA_ID);

        imageSelectionArea.css({
            left: leftPosition + 'px',
            top: topPosition + 'px',
            width: Math.abs(boxWidth) + 'px',
            height: Math.abs(boxHeight) + 'px'
        });
    }

    function getRectangleHeightAndWidth() {
        return {
            width: currentMouseX - initialClickX,
            height: currentMouseY - initialClickY
        };
    }

    function resizeRectangle() {
        var rectangleDimensions = getRectangleHeightAndWidth();

        var leftPosition = initialClickX;
        var topPosition = initialClickY;

        var width = rectangleDimensions.width;
        var height = rectangleDimensions.height;

        if (rectangleDimensions.width < 0 && rectangleDimensions.height < 0) {
            resizeBox(currentMouseX, currentMouseY, width, height);
        } else if (rectangleDimensions.width < 0) {
            resizeBox(currentMouseX, topPosition, width, height);
        } else if (rectangleDimensions.height < 0) {
            resizeBox(leftPosition, currentMouseY, width, height);
        } else {
            resizeBox(leftPosition, topPosition, width, height);
        }
    }

    function createOverlay() {
        var selectionOverlay = $('<div>', {
            id: constants.elements.IMAGE_SELECTION_OVERLAY_ID,
            class: 'image-area-selector__overlay'
        });

        getCurrentImageArea().append(selectionOverlay);
    }

    function createRectangle() {
        var overlay = $('#' + constants.elements.IMAGE_SELECTION_OVERLAY_ID);
        var dimensions = getRectangleHeightAndWidth();

        var leftPosition = initialClickX + 'px';
        var topPosition = initialClickY + 'px';

        var left = 'left: ' + leftPosition + ';';
        var top = 'top: ' + topPosition + ';';

        var width = 'width: ' + dimensions.width + 'px;';
        var height = 'height: ' + dimensions.height + 'px';

        var imageSelectionElement = $('<div>', {
            id: constants.elements.IMAGE_SELECTION_AREA_ID,
            class: 'image-area-selector__selection',
            style: left + top + width + height
        });

        overlay.append(imageSelectionElement);
    }

    function getFinishedSelectionArea() {
        var x1 = initialClickX < currentMouseX ? initialClickX : currentMouseX;
        var x2 = initialClickX < currentMouseX ? currentMouseX : initialClickX;

        var y1 = initialClickY < currentMouseY ? initialClickY : currentMouseY;
        var y2 = initialClickY < currentMouseY ? currentMouseY : initialClickY;

        return {
            height: x2 - x1,
            width: y2 - y1,
            x1: x1,
            x2: x2,
            y1: y1,
            y2: y2
        };
    }

    function markStartingSizesAndPositions(event) {
        var rectangle = getCurrentImageArea()[0].getBoundingClientRect();

        imageAreaLeft = rectangle.left;
        imageAreaTop = rectangle.top;

        initialClickX = event.clientX - imageAreaLeft;
        initialClickY = event.clientY - imageAreaTop;
    }

    function performCleanup() {
        isSelecting = false;

        $('#' + constants.elements.IMAGE_SELECTION_AREA_ID).remove();
        $('#' + constants.elements.IMAGE_SELECTION_OVERLAY_ID).remove();

        getCurrentImageArea().off('click', clickListener);
        getCurrentImageArea().off('mousemove', mouseMoveListener);
        getCurrentImageArea().css({cursor: ''});
        $(window).off('keydown', cancelListenerOnAreaSelect);

        resetValues();

        window.isAnnotating = false;
    }

    function getClickListener(onSelect) {
        return function (event) {
            event.stopPropagation();
            isSelecting = !isSelecting;

            if (isSelecting) {
                hideDetectionRectanglesWithoutOpenPopover();
                markStartingSizesAndPositions(event);
                createRectangle();
            } else {
                onSelect(getFinishedSelectionArea());

                showDetectionRectangles();
                showControlsOnImage();
                performCleanup();
            }
        };
    }

    function getMousePositionTrackingEventListener() {
        return function (event) {
            if (isSelecting) {
                currentMouseX = event.clientX - imageAreaLeft;
                currentMouseY = event.clientY - imageAreaTop;

                if (initialClickX || initialClickY) {
                    resizeRectangle();
                }
            }
        };
    }

    function listenForSelectionCancel(onCancel) {
        cancelListenerOnAreaSelect = function(event) {
            if (event.keyCode === constants.keyCodes.ESCAPE) {
                if (onCancel) {
                    onCancel();
                }

                performCleanup();
            }
        };

        $(window).keydown(cancelListenerOnAreaSelect);
    }

    return {
        getImageArea: function() {
            if (window.fullscreenEnabled) {
                return $('#' + constants.elements.ANNOTATION_CONTAINER_ID_ON_IMAGE);
            }

            var dimensions = imageArea[0].getBoundingClientRect();
            var imageAreaId = imageArea.attr('id');

            if (!dimensions.width && !dimensions.height) {
                this.setImageArea(imageAreaId);
            }

            return imageArea;
        },
        getImageAreaDimensions: function() {
            return this.getImageArea()[0].getBoundingClientRect();
        },
        setImageArea: function(imageAreaId) {
            imageArea = $('#' + imageAreaId);
        },
        startImageAreaSelection: function (onSelect, onCancel) {
            getCurrentImageArea().css({cursor: 'crosshair'});
            window.isAnnotating = true;

            hideControlsOnImage();

            createOverlay();
            listenForSelectionCancel(onCancel);

            clickListener = getClickListener(onSelect);
            mouseMoveListener = getMousePositionTrackingEventListener();

            getCurrentImageArea().click(clickListener);
            getCurrentImageArea().mousemove(mouseMoveListener);
        }
    };
})();

function copyAnnotateButtonToFullScreenView() {
    var fullScreenContainer = $('#ajapaik-fullscreen-image-container');

    var isButtonAlreadyPresent = fullScreenContainer.find('#mark-object-button').length > 0;
    if (isButtonAlreadyPresent) {
        return;
    }

    var markObjectClone = $('#mark-object-button').clone();
    markObjectClone.css('z-index', 1);

    markObjectClone.find('i').removeClass('ajapaik-text-gray');
    markObjectClone.addClass('annotation-button__fullscreen');

    markObjectClone.on('click', function(event) {
        event.stopPropagation();
        ObjectTagger.toggleCropping(true);
    });

    fullScreenContainer.append(markObjectClone);
}