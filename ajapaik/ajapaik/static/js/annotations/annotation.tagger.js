'use strict';

var ObjectTagger = {
    isInCropMode: false,
    imageArea: null,
    imageAreaId: null,
    photoId: null,
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

        $(this.imageArea).imgAreaSelect({
            disable: true,
            hide: true
        });

        enableMovingBetweenPictures();
    },
    handleSavedRectanglesDrawn: function(detections) {
        if (detections) {
            drawDetectionRectangles(detections, ObjectTagger.getImageArea());
            window.onresize = function() {
                drawDetectionRectangles(detections, ObjectTagger.getImageArea());
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

        var ref = this;

        ref.isInCropMode = true;

        setTimeout(function () {
            $(ref.imageArea).imgAreaSelect({
                onSelectEnd: ref.handleNewRectangleDrawn.bind(ref)
            });
        }, 0);

        disableMovingBetweenPictures();
    },
    toggleCropping: function () {
        $('#ajapaik-full-screen-link').css('cursor', 'crosshair');

        if (this.isInCropMode) {
            this.stopCropping();
        } else {
            this.startCropping();
        }
    }
};
