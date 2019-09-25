'use strict';

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

    function dragArea(event, annotationRectangle) {
        if (isDragging) {

            var xDifference = dragStartX - event.clientX;
            var yDifference = dragStartY - event.clientY;

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

        dragStartX = event.clientX;
        dragStartY = event.clientY;

        $('body').addClass('disable-select');
    }

    function dragTopLeft(event, annotationRectangle) {
        if (isDragging) {

            var xDifference = dragStartX - event.clientX;
            var yDifference = dragStartY - event.clientY;

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
            var yDifference = dragStartY - event.clientY;

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
            var xDifference = dragStartX - event.clientX;

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

            var xDifference = dragStartX - event.clientX;
            var yDifference = dragStartY - event.clientY;

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

            var xDifference = dragStartX - event.clientX;
            var yDifference = dragStartY - event.clientY;

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
            var yDifference = dragStartY - event.clientY;

            var newHeight = initialHeight - yDifference;

            annotationRectangle.css({
                height: newHeight + 'px'
            });
        }
    }

    function dragTopRight(event, annotationRectangle) {
        if (isDragging) {

            var xDifference = dragStartX - event.clientX;
            var yDifference = dragStartY - event.clientY;

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
            var xDifference = dragStartX - event.clientX;

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

    function addDragFunctions(element, annotationRectangle, elementSpecificDragFunction) {
        var elementSpecificDrag = function(event) {
            hasDragged = true;
            annotationRectangle.popover('hide');
            elementSpecificDragFunction(event, annotationRectangle);
        };

        var dragEnd = function() {
            endDrag();

            $(document).off('mousemove', elementSpecificDrag);
            $(document).off('mouseup', dragEnd);
        };

        element.on('mousedown', function(event) {
            startDrag(event, annotationRectangle);

            $(document).on('mousemove', elementSpecificDrag);
            $(document).on('mouseup', dragEnd);
        });

        element.on('click', function(event) {
            event.stopPropagation();

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
