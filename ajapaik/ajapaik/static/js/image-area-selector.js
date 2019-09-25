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

    var imageAreaReferenceForExternalReference = null;

    function resetValues() {
        imageArea = null;
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

        imageArea.append(selectionOverlay);
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
        var rectangle = imageArea[0].getBoundingClientRect();

        imageAreaLeft = rectangle.left;
        imageAreaTop = rectangle.top;

        initialClickX = event.clientX - imageAreaLeft;
        initialClickY = event.clientY - imageAreaTop;
    }

    function performCleanup() {
        isSelecting = false;

        $('#' + constants.elements.IMAGE_SELECTION_AREA_ID).remove();
        $('#' + constants.elements.IMAGE_SELECTION_OVERLAY_ID).remove();

        imageArea.off('click', clickListener);
        imageArea.off('mousemove', mouseMoveListener);
        imageArea.css({cursor: ''});
        $(window).off('keydown', cancelListenerOnAreaSelect);

        resetValues();
    }

    function getClickListener(imageAreaId, onSelect) {
        return function (event) {
            isSelecting = !isSelecting;

            if (isSelecting) {
                markStartingSizesAndPositions(event);
                createRectangle();
            } else {
                onSelect(
                    document.getElementById(imageAreaId),
                    getFinishedSelectionArea()
                );

                performCleanup();
            }
        };
    }

    function getMousePositionTrackingEventListener() {
        return function (event) {
            if (isSelecting) {
                currentMouseX = event.pageX - imageAreaLeft;
                currentMouseY = event.pageY - imageAreaTop;

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
            return imageAreaReferenceForExternalReference;
        },
        startImageAreaSelection: function (imageAreaId, onSelect, onCancel) {
            imageArea = $('#' + imageAreaId).css({cursor: 'crosshair'});
            imageAreaReferenceForExternalReference = imageArea;

            createOverlay();
            listenForSelectionCancel(onCancel);

            clickListener = getClickListener(imageAreaId, onSelect);
            mouseMoveListener = getMousePositionTrackingEventListener();

            imageArea.click(clickListener);
            imageArea.mousemove(mouseMoveListener);
        }
    };
})();
