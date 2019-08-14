'use strict';

var ObjectTagger = {
    isInCropMode: false,
    imageArea: null,

    setImageArea: function() {
        var self = this;

        this.imageArea = this.getImageArea();
        $(this.imageArea).on("remove", function () {
            self.imageArea = null;
        });
    },
    getImageArea: function() {
        if (this.imageArea) {
            return this.imageArea;
        }

        return $('#ajapaik-modal-photo-container').get()[0];
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
