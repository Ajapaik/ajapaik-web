'use strict';

var ImageAreaSelector = (function () {
  var imageArea = null;
  let initialClickX = null;
  let initialClickY = null;
  let currentMouseX = null;
  let currentMouseY = null;
  let imageAreaLeft = null;
  let imageAreaTop = null;
  let isSelecting = false;

  let clickListener = null;
  let mouseMoveListener = null;
  let cancelListenerOnAreaSelect = null;

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
    const imageSelectionArea = $(
      '#' + constants.elements.IMAGE_SELECTION_AREA_ID
    );

    imageSelectionArea.css({
      left: leftPosition + 'px',
      top: topPosition + 'px',
      width: Math.abs(boxWidth) + 'px',
      height: Math.abs(boxHeight) + 'px',
    });
  }

  function getRectangleHeightAndWidth() {
    return {
      width: currentMouseX - initialClickX,
      height: currentMouseY - initialClickY,
    };
  }

  function resizeRectangle() {
    const rectangleDimensions = getRectangleHeightAndWidth();

    const leftPosition = initialClickX;
    const topPosition = initialClickY;

    const width = rectangleDimensions.width;
    const height = rectangleDimensions.height;

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
    const selectionOverlay = $('<div>', {
      id: constants.elements.IMAGE_SELECTION_OVERLAY_ID,
      class: 'image-area-selector__overlay annotation__guiding-overlay',
    });

    const informativeTextContainer = $(
      '<span class="annotation__informative-text"/>'
    ).append(constants.translations.annotations.INFORM_HOW_TO_ANNOTATE);

    selectionOverlay.mouseenter(function () {
      $(this).removeClass('annotation__guiding-overlay');
      informativeTextContainer.addClass('hide');
    });

    selectionOverlay.mouseleave(function () {
      $(this).addClass('annotation__guiding-overlay');
      informativeTextContainer.removeClass('hide');
    });

    selectionOverlay.append(informativeTextContainer);

    getCurrentImageArea().append(selectionOverlay);
  }

  function createRectangle() {
    const overlay = $('#' + constants.elements.IMAGE_SELECTION_OVERLAY_ID);
    const dimensions = getRectangleHeightAndWidth();

    const leftPosition = initialClickX + 'px';
    const topPosition = initialClickY + 'px';

    const left = 'left: ' + leftPosition + ';';
    const top = 'top: ' + topPosition + ';';

    const width = 'width: ' + dimensions.width + 'px;';
    const height = 'height: ' + dimensions.height + 'px';

    const imageSelectionElement = $('<div>', {
      id: constants.elements.IMAGE_SELECTION_AREA_ID,
      class: 'image-area-selector__selection',
      style: left + top + width + height,
    });

    overlay.append(imageSelectionElement);
  }

  function getFinishedSelectionArea() {
    const x1 = initialClickX < currentMouseX ? initialClickX : currentMouseX;
    const x2 = initialClickX < currentMouseX ? currentMouseX : initialClickX;

    const y1 = initialClickY < currentMouseY ? initialClickY : currentMouseY;
    const y2 = initialClickY < currentMouseY ? currentMouseY : initialClickY;

    return {
      height: x2 - x1,
      width: y2 - y1,
      x1: x1,
      x2: x2,
      y1: y1,
      y2: y2,
    };
  }

  function markStartingSizesAndPositions(event) {
    const rectangle = getCurrentImageArea()[0].getBoundingClientRect();

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
    getCurrentImageArea().css({ cursor: '' });
    $(window).off('keydown', cancelListenerOnAreaSelect);

    resetValues();

    window.isAnnotating = false;
  }

  function getClickListener(onSelect) {
    return function (event) {
      event.stopPropagation();
      isSelecting = !isSelecting;

      if (isSelecting) {
        hideAnnotationsWithoutOpenPopover();
        markStartingSizesAndPositions(event);
        createRectangle();
      } else {
        onSelect(getFinishedSelectionArea());

        displayAnnotations(true, true);
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
    cancelListenerOnAreaSelect = function (event) {
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
    performCleanup: performCleanup,
    getImageArea: function () {
      if (window.fullscreenEnabled) {
        return $('#' + constants.elements.ANNOTATION_CONTAINER_ID_ON_IMAGE);
      }

      if (!imageArea && !imageArea[0]) {
        return undefined;
      }

      let dimensions = imageArea[0].getBoundingClientRect();
      let imageAreaId = imageArea.attr('id');

      if (!dimensions.width && !dimensions.height) {
        this.setImageArea(imageAreaId);
      }

      return imageArea;
    },
    getImageAreaDimensions: function () {
      return this.getImageArea()[0].getBoundingClientRect();
    },
    setImageArea: function (imageAreaId) {
      imageArea = $('#' + imageAreaId);
    },
    startImageAreaSelection: function (onSelect, onCancel) {
      getCurrentImageArea().css({ cursor: 'crosshair' });
      getCurrentImageArea();
      window.isAnnotating = true;

      hideControlsOnImage();

      createOverlay();
      listenForSelectionCancel(onCancel);

      clickListener = getClickListener(onSelect);
      mouseMoveListener = getMousePositionTrackingEventListener();

      getCurrentImageArea().click(clickListener);
      getCurrentImageArea().mousemove(mouseMoveListener);
    },
  };
})();

function copyAnnotateButtonToFullScreenView() {
  const fullScreenContainer = $('#ajp-fullscreen-image-container');

  const annotateButton = fullScreenContainer.find('#mark-object-button');
  const isButtonAlreadyPresent = annotateButton.length > 0;

  if (window.isAnnotatingDisabled) {
    annotateButton.remove();
    return;
  }

  if (isButtonAlreadyPresent) {
    return;
  }

  const markObjectClone = $('#mark-object-button').clone();
  markObjectClone.css('z-index', 1);

  markObjectClone.find('i').removeClass('ajp-text-gray');
  markObjectClone.addClass('annotation-button__fullscreen');

  markObjectClone.on('click', function (event) {
    event.stopPropagation();
    ObjectTagger.toggleCropping(true);
  });

  fullScreenContainer.append(markObjectClone);
}
