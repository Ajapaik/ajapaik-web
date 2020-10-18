'use strict';

var ObjectTagger = {
    isInCropMode: false,
    photoId: null,
    detectionRectangleContainer: 'body',

    setDetectionRectangleContainer: function(container) {
        this.detectionRectangleContainer = container;
    },
    getDetectionRectangleContainer: function () {
        return this.detectionRectangleContainer;
    },
    setPhotoId: function(photoId) {
        this.photoId = photoId;
    },
    getPhotoId: function () {
        return this.photoId;
    },
    stopCropping: function () {
        this.isInCropMode = false;

        $('#ajp-full-screen-link').css('cursor', 'zoom-in');

        enableMovingBetweenPictures();
        ImageAreaSelector.performCleanup();
    },
    handleSavedRectanglesDrawn: function(detections) {
        if (detections) {
            setTimeout(function () {
                drawDetectionRectangles(detections, ImageAreaSelector.getImageAreaDimensions());
            }, 200);
        }
    },
    handleNewRectangleDrawn: function (selection, isNotOpeningPopoverOnDrawEnd) {
        this.stopCropping();

        var detectionRectangle = drawNewAnnotationRectangle(selection);
        detectionRectangle.rectangle.appendTo(ImageAreaSelector.getImageArea());

        if (!window.isMobile && !isNotOpeningPopoverOnDrawEnd) {
            togglePopover(detectionRectangle.id);
        }
    },
    drawBoxForMobileSelection: function(onSelectionEnd) {
        var imageAreaDimensions = ImageAreaSelector.getImageAreaDimensions();

        var overallImageAreaHeight = imageAreaDimensions.height;
        var overallImageAreaWidth = imageAreaDimensions.width;

        var boxToBeDrawnHeight = overallImageAreaHeight * 0.2;
        var boxToBeDrawnWidth = overallImageAreaWidth * 0.2;

        var imageCenterWidth = overallImageAreaWidth / 2;
        var imageCenterHeight = overallImageAreaHeight / 2;

        var halfOfBoxHeight = boxToBeDrawnHeight / 2;
        var halfOfBoxWidth = boxToBeDrawnWidth / 2;

        onSelectionEnd(
            {
                x1: imageCenterWidth - halfOfBoxWidth,
                x2: imageCenterWidth + halfOfBoxWidth,
                y1: imageCenterHeight - halfOfBoxHeight,
                y2: imageCenterHeight + halfOfBoxHeight
            }
        );
    },
    startCropping: function (isNotOpeningPopoverOnDrawEnd) {
        if (isAnnotatingDisabled()) {
            return;
        }

        var handleNewRectangleDrawn = this.handleNewRectangleDrawn.bind(this);
        var onSelectionEnd = function (selection) {
            handleNewRectangleDrawn(selection, isNotOpeningPopoverOnDrawEnd);
        };

        if (window.isMobile) {
            this.drawBoxForMobileSelection(onSelectionEnd);
            return;
        }

        disableImageSubmitControls();

        this.isInCropMode = true;

        var onSelectionCancel = this.stopCropping.bind(this);

        ImageAreaSelector.startImageAreaSelection(onSelectionEnd, onSelectionCancel);

        disableMovingBetweenPictures();
    },
    toggleCropping: function (isNotOpeningPopoverOnDrawEnd) {
        if (this.isInCropMode) {
            this.stopCropping();
        } else {
            this.startCropping(isNotOpeningPopoverOnDrawEnd);
        }
    }
};
