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

    var imageAreaTop = null;
    var imageAreaLeft = null;

    var imageAreaBottom = null;
    var imageAreaRight = null;

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

            var newTop = (initialTop - imageAreaTop) - yDifference;
            var newLeft = (initialLeft - imageAreaLeft) - xDifference;

            var rectangleWidth = annotationRectangle.width();
            var rectangleHeight = annotationRectangle.height();

            var isWidthStillWithinImageBounds = imageAreaRight > (newLeft + imageAreaLeft + rectangleWidth + 5);
            var isHeightStillWithinImageBounds = imageAreaBottom > (newTop + imageAreaTop + rectangleHeight + 5);

            var css = {};

            if (newLeft > 0 && isWidthStillWithinImageBounds) {
                css.left = newLeft + 'px';
            }

            if (newTop > 0 && isHeightStillWithinImageBounds) {
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
        var imageAreaBoundingClientRect = ImageAreaSelector.getImageArea()[0].getBoundingClientRect();

        var clickEvent = getEventForClickOrTouch(event);

        isDragging = true;
        hasDragged = false;

        initialWidth = annotationRectangle[0].getBoundingClientRect().width;
        initialHeight = annotationRectangle[0].getBoundingClientRect().height;

        initialTop = annotationRectangle[0].getBoundingClientRect().top;
        initialLeft = annotationRectangle[0].getBoundingClientRect().left;

        imageAreaTop = imageAreaBoundingClientRect.top;
        imageAreaLeft = imageAreaBoundingClientRect.left;

        imageAreaBottom = imageAreaTop + imageAreaBoundingClientRect.height;
        imageAreaRight = imageAreaLeft + imageAreaBoundingClientRect.width;

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

            var newTop = (initialTop - imageAreaTop) - yDifference;
            var newLeft = (initialLeft - imageAreaLeft) - xDifference;

            var css = {
                width: newWidth + 'px',
                height: newHeight + 'px'
            };

            if (newWidth > 0) {
                css.left = newLeft + 'px';
            }

            if (newHeight > 0) {
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

            var newTop = (initialTop - imageAreaTop) - yDifference;

            var css = {
                height: newHeight + 'px'
            };

            if (newHeight > 0) {
                css.top = newTop + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function dragLeft(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;

            var newWidth = initialWidth + xDifference;

            var newLeft = (initialLeft - imageAreaLeft) - xDifference;

            var css = {
                width: newWidth + 'px'
            };

            if (newWidth > 0) {
                css.left = newLeft + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function dragBottomRight(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;
            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight - yDifference;
            var newWidth = initialWidth - xDifference;

            annotationRectangle.css({
                width: newWidth + 'px',
                height: newHeight + 'px'
            });
        }
    }

    function dragBottomLeft(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;
            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight - yDifference;
            var newWidth = initialWidth + xDifference;

            var newLeft = (initialLeft - imageAreaLeft) - xDifference;

            var css = {
                width: newWidth + 'px',
                height: newHeight + 'px'
            };

            if (newWidth > 0) {
                css.left = newLeft + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function dragBottom(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight - yDifference;

            annotationRectangle.css({
                height: newHeight + 'px'
            });
        }
    }

    function dragTopRight(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;
            var yDifference = dragStartY - clickEvent.clientY;

            var newHeight = initialHeight + yDifference;
            var newWidth = initialWidth - xDifference;

            var newTop = (initialTop - imageAreaTop) - yDifference;

            var css = {
                width: newWidth + 'px',
                height: newHeight + 'px'
            };

            if (newHeight > 0) {
                css.top = newTop + 'px';
            }

            annotationRectangle.css(css);
        }
    }

    function dragRight(event, annotationRectangle) {
        if (isDragging) {
            var clickEvent = getEventForClickOrTouch(event);

            var xDifference = dragStartX - clickEvent.clientX;

            var newWidth = initialWidth - xDifference;

            annotationRectangle.css({
                width: newWidth + 'px'
            });
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
                annotationRectangle.click();
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
