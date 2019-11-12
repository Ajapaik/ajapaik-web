'use strict';

/* jshint browser: true */
/* globals $:false */

var DraggableArea = (function () {
    var isDragging = false;
    var hasDragged = false;

    var dragStartX = null;
    var dragStartY = null;

    var initialWidth = null;
    var initialHeight = null;
    var initialTop = null;
    var initialLeft = null;

    function getCurrentDrawingAreaDimensions() {
        if (window.fullscreenEnabled) {
            return document.getElementById(constants.elements.ANNOTATION_CONTAINER_ID_ON_IMAGE).getBoundingClientRect();
        }

        return ImageAreaSelector.getImageAreaDimensions();
    }

    function getAllowedLocationDimensions() {
        var currentImageAreaDimensions = getCurrentDrawingAreaDimensions();

        return {
            maximumAllowedWidthLocation: currentImageAreaDimensions.width,
            maximumAllowedHeightLocation: currentImageAreaDimensions.height,
            minimalAllowedLeftPosition: 0,
            minimumHeight: 5,
            minimumWidth: 5
        };
    }

    function addTopResizeBorder(annotationRectangle) {
        var resizeDiagonalTopLeftWidth = $('<span>', {
            class: 'resizable-box__vertical-corner',
            data: {
                'is-detection-controls': true
            },
            css: {
                cursor: 'nw-resize'
            }
        });
        addDragFunctions(resizeDiagonalTopLeftWidth, annotationRectangle, dragTopLeft);

        var resizeTop = $('<span>', {
            class: 'resizable-box__vertical-center',
            data: {
                'is-detection-controls': true
            },
            css: {
                cursor: 'n-resize'
            }
        });
        addDragFunctions(resizeTop, annotationRectangle, dragTop);

        var resizeDiagonalTopRight = $('<span>', {
            class: 'resizable-box__vertical-corner',
            data: {
                'is-detection-controls': true
            },
            css: {
                cursor: 'ne-resize'
            }
        });
        addDragFunctions(resizeDiagonalTopRight, annotationRectangle, dragTopRight);

        var topContainer = $('<span class="resizable-box__top">');

        annotationRectangle
            .append(topContainer
                .append(resizeDiagonalTopLeftWidth)
                .append(resizeTop)
                .append(resizeDiagonalTopRight)
            );
    }

    function addBottomResizeBorder(annotationRectangle) {
        var resizeDiagonalBottomLeftWidth = $('<span>', {
            class: 'resizable-box__vertical-corner',
            data: {
                'is-detection-controls': true
            },
            css: {
                cursor: 'sw-resize'
            }
        });
        addDragFunctions(resizeDiagonalBottomLeftWidth, annotationRectangle, dragBottomLeft);

        var resizeBottom = $('<span>', {
            class: 'resizable-box__vertical-center',
            data: {
                'is-detection-controls': true
            },
            css: {
                cursor: 's-resize'
            }
        });
        addDragFunctions(resizeBottom, annotationRectangle, dragBottom);

        var resizeDiagonalBottomRight = $('<span>', {
            class: 'resizable-box__vertical-corner',
            data: {
                'is-detection-controls': true
            },
            css: {
                cursor: 'se-resize'
            }
        });
        addDragFunctions(resizeDiagonalBottomRight, annotationRectangle, dragBottomRight);

        var bottomContainer = $('<span class="resizable-box__bottom">');

        annotationRectangle
            .append(bottomContainer
                .append(resizeDiagonalBottomLeftWidth)
                .append(resizeBottom)
                .append(resizeDiagonalBottomRight)
            );
    }

    function addLeftResizeBorder(annotationRectangle) {
        var resizeLeft = $('<span>', {
            class: 'resizable-box__horizontal',
            data: {
                'is-detection-controls': true
            },
            css: {
                cursor: 'w-resize'
            }
        });

        var leftContainer = $('<span class="resizable-box__left">');

        addDragFunctions(leftContainer, annotationRectangle, dragLeft);

        annotationRectangle
            .append(leftContainer
                .append(resizeLeft)
            );

    }

    function addRightResizeBorder(annotationRectangle) {
        var resizeRight = $('<span>', {
            class: 'resizable-box__horizontal',
            data: {
                'is-detection-controls': true
            },
            css: {
                cursor: 'e-resize'
            }
        });

        var rightContainer = $('<span class="resizable-box__right">');

        addDragFunctions(rightContainer, annotationRectangle, dragRight);

        annotationRectangle
            .append(rightContainer
                .append(resizeRight)
            );
    }

    function getEventForClickOrTouch(event) {
        var isRegularClickEvent = !!event.clientX;

        if (isRegularClickEvent) {
            return event;
        }

        var isJQueryTouchEvent = !!event.originalEvent;

        if (isJQueryTouchEvent) {
            return event.originalEvent.touches[0];
        }

        return event.touches[0];
    }

    function dragArea(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;
            var yDifference = dragStartY - clickEvent.clientY;

            var newTop = initialTop - yDifference;
            var newLeft = initialLeft - xDifference;

            var rectangleWidth = annotationRectangle[0].getBoundingClientRect().width;
            var rectangleHeight = annotationRectangle[0].getBoundingClientRect().height;

            var allowedDimensions = getAllowedLocationDimensions();

            var css = {};

            if (newLeft > allowedDimensions.minimalAllowedLeftPosition && newLeft + rectangleWidth < allowedDimensions.maximumAllowedWidthLocation) {
                css.left = newLeft + 'px';
            }

            if (newTop > 0 && newTop + rectangleHeight < allowedDimensions.maximumAllowedHeightLocation) {
                css.top = newTop + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function addMoveArea(annotationRectangle) {
        var moveArea = $('<span class="resizable-box__move-area" data-is-detection-controls="true">');
        addDragFunctions(moveArea, annotationRectangle, dragArea);
        annotationRectangle.append(moveArea);
    }

    function addResizeIndicatorIcon(iconSpecificClass, annotationRectangle, directionSpecificFunction) {
        var icon = $('<i class="material-icons notranslate resizable-box__arrow">height</i>');

        icon.addClass(iconSpecificClass);
        icon.data({'is-detection-controls': true});

        addDragFunctions(icon, annotationRectangle, directionSpecificFunction);

        annotationRectangle.append(icon);
    }

    function addResizeIndicator(annotationRectangle) {
        addResizeIndicatorIcon('resizable-box__arrow--top-left', annotationRectangle, dragTopLeft);
        addResizeIndicatorIcon('resizable-box__arrow--top-right', annotationRectangle, dragTopRight);
        addResizeIndicatorIcon('resizable-box__arrow--bottom-left', annotationRectangle, dragBottomLeft);
        addResizeIndicatorIcon('resizable-box__arrow--bottom-right', annotationRectangle, dragBottomRight);

        addResizeIndicatorIcon('resizable-box__arrow--top', annotationRectangle, dragTop);
        addResizeIndicatorIcon('resizable-box__arrow--left', annotationRectangle, dragLeft);
        addResizeIndicatorIcon('resizable-box__arrow--bottom', annotationRectangle, dragBottom);
        addResizeIndicatorIcon('resizable-box__arrow--right', annotationRectangle, dragRight);
    }

    function startDrag(event, annotationRectangle) {
        var clickEvent = getEventForClickOrTouch(event);

        isDragging = true;
        hasDragged = false;

        initialWidth = annotationRectangle[0].getBoundingClientRect().width;
        initialHeight = annotationRectangle[0].getBoundingClientRect().height;

        initialTop = parseFloat(annotationRectangle.css('top').replace('px', ''));
        initialLeft = parseFloat(annotationRectangle.css('left').replace('px', ''));

        dragStartX = clickEvent.clientX;
        dragStartY = clickEvent.clientY;

        $('body').addClass('disable-select');
    }

    function dragTopLeft(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;
            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight + yDifference;
            var newWidth = initialWidth + xDifference;

            var newTop = initialTop - yDifference;
            var newLeft = initialLeft - xDifference;

            var newRight = newLeft + newWidth;
            var allowedDimensions = getAllowedLocationDimensions();

            var css = {};

            if (newWidth > allowedDimensions.minimumWidth &&
                newLeft > allowedDimensions.minimalAllowedLeftPosition &&
                newRight < allowedDimensions.maximumAllowedWidthLocation
            ) {
                css.left = newLeft + 'px';
                css.width = newWidth + 'px';
            }

            if (newTop > 0) {
                css.height = newHeight + 'px';
            }

            if (newHeight > allowedDimensions.minimumHeight && newTop > 0) {
                css.top = newTop + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function dragTop(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight + yDifference;

            var newTop = initialTop - yDifference;

            var newBottom = initialTop + newHeight;

            var allowedDimensions = getAllowedLocationDimensions();

            if (
                newTop > 0 &&
                newHeight > allowedDimensions.minimumHeight &&
                newBottom < allowedDimensions.maximumAllowedHeightLocation
            ) {
                annotationRectangle.css({
                    top: newTop + 'px',
                    height: newHeight + 'px'
                });
            }
        }
    }

    function dragLeft(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;

            var newWidth = initialWidth + xDifference;

            var newLeft = initialLeft - xDifference;

            var allowedDimensions = getAllowedLocationDimensions();

            if (newWidth > allowedDimensions.minimumWidth && newLeft > allowedDimensions.minimalAllowedLeftPosition) {
                annotationRectangle.css({
                    left: newLeft + 'px',
                    width: newWidth + 'px'
                });
            }
        }
    }

    function dragBottomRight(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;
            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight - yDifference;
            var newWidth = initialWidth - xDifference;

            var newRight = initialLeft + newWidth;
            var newBottom = initialTop + newHeight;

            var allowedDimensions = getAllowedLocationDimensions();

            var css = {};

            if (newRight < allowedDimensions.maximumAllowedWidthLocation) {
                css.width = newWidth + 'px';
            }

            if (newBottom < allowedDimensions.maximumAllowedHeightLocation) {
                css.height = newHeight + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function dragBottomLeft(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;
            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight - yDifference;
            var newWidth = initialWidth + xDifference;

            var newLeft = initialLeft - xDifference;

            var newBottom = initialTop + newHeight;

            var allowedDimensions = getAllowedLocationDimensions();

            var css = {};

            if (newWidth > allowedDimensions.minimumWidth && newLeft > allowedDimensions.minimalAllowedLeftPosition) {
                css.width = newWidth + 'px';
                css.left = newLeft + 'px';
            }

            if (newBottom < allowedDimensions.maximumAllowedHeightLocation) {
                css.height = newHeight + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function dragBottom(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight - yDifference;

            var newBottom = initialTop + newHeight;

            var allowedDimensions = getAllowedLocationDimensions();

            if (newBottom < allowedDimensions.maximumAllowedHeightLocation) {
                annotationRectangle.css({
                    height: newHeight + 'px'
                });
            }
        }
    }

    function dragTopRight(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;
            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight + yDifference;
            var newWidth = initialWidth - xDifference;

            var newTop = initialTop - yDifference;

            var newRight = initialLeft + newWidth;
            var allowedDimensions = getAllowedLocationDimensions();

            var css = {};

            if (newRight < allowedDimensions.maximumAllowedWidthLocation) {
                css.width = newWidth + 'px';
            }

            if (newHeight > allowedDimensions.minimumHeight && newTop > 0) {
                css.top = newTop + 'px';
                css.height = newHeight + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function dragRight(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;

            var newWidth = initialWidth - xDifference;

            var newRight = initialLeft + newWidth;
            var allowedDimensions = getAllowedLocationDimensions();

            if (newWidth > allowedDimensions.minimumWidth && newRight < allowedDimensions.maximumAllowedWidthLocation) {
                annotationRectangle.css({
                    width: newWidth + 'px'
                });
            }
        }
    }

    function endDrag() {
        isDragging = false;
        $('body').removeClass('disable-select');
    }

    function getTouchDragEndFunction(dragEndFunction) {
        return function (e) {
            var isDetectionControls = $(e.target).data('is-detection-controls');

            if (isDetectionControls) {
                e.preventDefault(); // Needed to avoid dragging the page instead of dragging the element on touch
                dragEndFunction(e);
            }
        };
    }

    function getTouchDragFunction(dragFunction) {
        return function (e) {
            var isDetectionControls = $(e.target).data('is-detection-controls');

            if (isDetectionControls) {
                e.preventDefault();
                dragFunction(e);
            }
        };
    }

    function addDragAndEndDragEndForTouch(dragFunction, endFunction) {
        document.body.addEventListener('touchmove', dragFunction, {passive: false});
        document.body.addEventListener('touchend', endFunction, {passive: false});
    }

    function convertAnnotationPixelValuesToPercentages(annotationRectangle) {
        var imageAreaDimensions = getCurrentDrawingAreaDimensions();

        var distanceFromTop = parseFloat(annotationRectangle.css('top').replace('px', '')) / imageAreaDimensions.height;
        var distanceFromLeft = parseFloat(annotationRectangle.css('left').replace('px', '')) / imageAreaDimensions.width;
        var width = annotationRectangle[0].getBoundingClientRect().width / imageAreaDimensions.width;
        var height = annotationRectangle[0].getBoundingClientRect().height / imageAreaDimensions.height;

        annotationRectangle.css({
            top: distanceFromTop * 100 + '%',
            left: distanceFromLeft * 100 + '%',
            width: width * 100 + '%',
            height: height * 100 + '%'
        });
    }

    function addDragFunctions(element, annotationRectangle, elementSpecificDragFunction) {
        var elementSpecificDrag = function (event) {
            hasDragged = true;
            annotationRectangle.popover('hide');
            elementSpecificDragFunction(event, annotationRectangle);
        };

        var touchDragFunction = getTouchDragFunction(elementSpecificDrag);
        var touchDragEndFunction;

        var dragEnd = function () {
            endDrag();

            $(document).off('mousemove', elementSpecificDrag);
            $(document).off('mouseup', dragEnd);

            document.body.removeEventListener('touchmove', touchDragFunction);
            document.body.removeEventListener('touchend', touchDragEndFunction);

            convertAnnotationPixelValuesToPercentages(annotationRectangle);
        };

        touchDragEndFunction = getTouchDragEndFunction(dragEnd);

        var onDownEvent = function (event) {
            startDrag(event, annotationRectangle);

            $(document).on('mousemove', elementSpecificDrag);
            $(document).on('mouseup', dragEnd);

            addDragAndEndDragEndForTouch(touchDragFunction, touchDragEndFunction);
        };

        element.on('mousedown', onDownEvent);
        element.on('touchstart', onDownEvent);

        element.on('click', function (event) {
            event.stopPropagation();

            if (!hasDragged) {
                annotationRectangle.click();
            }
        });

        element.on('touchend', function () {
            if (!hasDragged) {
                if (window.fullscreenEnabled) {
                    setTimeout(function() {
                        $('.full-box div').click();
                    });
                } else {
                    annotationRectangle.click();
                }
            }
        });
    }

    function addResizeAndMoveControls(annotationRectangle) {
        addTopResizeBorder(annotationRectangle);
        addBottomResizeBorder(annotationRectangle);
        addLeftResizeBorder(annotationRectangle);
        addRightResizeBorder(annotationRectangle);

        addMoveArea(annotationRectangle);
        addResizeIndicator(annotationRectangle);
    }

    return {
        addResizeAndMoveControls: addResizeAndMoveControls
    };
})();
