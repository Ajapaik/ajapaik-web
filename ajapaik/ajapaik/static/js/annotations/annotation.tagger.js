'use strict';

var ObjectTagger = {
    isInCropMode: false,
    imageArea: null,
    imageAreaId: null,
    photoId: null,
    previousWindowWidth: null,
    detectionRectangleContainer: 'body',

    setDetectionRectangleContainer: function(container) {
        this.detectionRectangleContainer = container;
    },
    getDetectionRectangleContainer: function() {
        return this.detectionRectangleContainer;
    },
    setPhotoId: function(photoId) {
        this.photoId = photoId;
    },
    getPhotoId: function() {
        return this.photoId;
    },
    setImageArea: function(imageAreaId) {
        var self = this;
        self.imageAreaId = imageAreaId;

        this.imageArea = this.getImageArea(imageAreaId);
        $(this.imageArea).on("remove", function () {
            self.imageArea = null;
        });
    },
    getImageArea: function(imageAreaId) {
        if (this.imageArea) {
            return this.imageArea;
        }

        return $('#' + imageAreaId).get()[0];
    },
    stopCropping: function () {
        this.isInCropMode = false;

        $('#ajapaik-full-screen-link').css('cursor', 'zoom-in');

        enableMovingBetweenPictures();
    },
    handleSavedRectanglesDrawn: function(detections) {
        if (detections) {
            drawDetectionRectangles(detections, ObjectTagger.getImageArea());
            ObjectTagger.previousWindowWidth = window.innerWidth;

            window.onresize = function() {
                if (!window.isMobile || window.isMobile && ObjectTagger.previousWindowWidth !== window.innerWidth) {
                    ObjectTagger.previousWindowWidth = window.innerWidth;
                    drawDetectionRectangles(detections, ObjectTagger.getImageArea());
                }
            };
        }
    },
    handleNewRectangleDrawn: function (img, selection) {
        this.stopCropping();

        var detectionRectangle = drawNewAnnotationRectangle(img, selection);
        detectionRectangle.rectangle.appendTo(this.imageArea);

        togglePopover(detectionRectangle.id);
    },
    startCropping: function () {
        disableImageSubmitControls();

        this.isInCropMode = true;

        var onSelectionEnd = this.handleNewRectangleDrawn.bind(this);
        var onSelectionCancel = this.stopCropping.bind(this);

        ImageAreaSelector.startImageAreaSelection(this.imageAreaId, onSelectionEnd, onSelectionCancel);

        disableMovingBetweenPictures();
    },
    toggleCropping: function () {
        if (this.isInCropMode) {
            this.stopCropping();
        } else {
            this.startCropping();
        }
    }
};
