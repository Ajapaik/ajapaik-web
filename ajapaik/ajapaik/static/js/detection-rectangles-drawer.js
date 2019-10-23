'use strict';

function getDetectedFaceRectangle(popoverId, annotation, configuration) {
    return createSavedFaceDetectionRectangle(
        popoverId,
        annotation,
        configuration
    );
}

function getDetectedObjectRectangle(popoverId, annotation, configuration) {
    return createSavedObjectDetectionRectangle(
        popoverId,
        annotation,
        configuration
    );
}

function getDetectedObjectModifyRectangle(rectangleId, savedRectangle, configuration) {
    return createSavedObjectModifyDetectionRectangle(
        rectangleId,
        savedRectangle,
        configuration
    );
}

function getDetectedFaceModifyRectangle(rectangleId, savedRectangle, configuration) {
    return createFaceAnnotationEditRectangle(
        rectangleId,
        savedRectangle,
        configuration
    );
}

function getSavedDetectionRectangle(scaledRectangle, annotation) {
    var leftEdgeDistance = scaledRectangle.x1;
    var topEdgeDistance = scaledRectangle.y1;

    var width = (scaledRectangle.x2 - scaledRectangle.x1);
    var height = (scaledRectangle.y2 - scaledRectangle.y1);

    var configuration = {
        placementFromLeftEdge: leftEdgeDistance,
        placementFromTopEdge: topEdgeDistance,
        width: width,
        height: height,
        annotation: annotation
    };

    if (annotation.wikiDataId) {
        if (annotation.isDeletable) {
            return getDetectedObjectModifyRectangle(
                'ajapaik-object-modify-rectangle-' + annotation.id,
                annotation,
                configuration
            );
        }

        return getDetectedObjectRectangle(
            'ajapaik-object-rectangle-' + annotation.id,
            annotation,
            configuration
        );
    } else {
        if (annotation.isDeletable) {
            return getDetectedFaceModifyRectangle(
                'ajapaik-face-modify-rectangle-' + annotation.id,
                annotation,
                configuration
            );
        }
        return getDetectedFaceRectangle(
            'ajapaik-face-rectangle-' + annotation.id,
            annotation,
            configuration
        );
    }
}

function removeExistingDetectionRectangles() {
    $('[data-is-detection-rectangle]').each(function() {
        var rectangle = $(this);

        var popoverSelector = '.popover';

        $(popoverSelector).remove();
        rectangle.remove();
    });
}

function drawDetectionRectangles(detections, imageArea) {
    $('.popover').remove();

    setTimeout(function() {
        removeExistingDetectionRectangles();

        var scaledImageDimensions = getImageScaledDimensions(imageArea.getBoundingClientRect());

        var currentImageAreaDimensions = scaledImageDimensions.currentImageAreaDimensions;

        var scaledPhotoWidthWithoutPadding = scaledImageDimensions.scaledPhotoWidthWithoutPadding;
        var blackPaddingSizeOnOneSide = scaledImageDimensions.blackPaddingSizeOnOneSide;

        var widthScale = window.currentPhotoOriginalWidth / scaledPhotoWidthWithoutPadding;
        var heightScale = window.currentPhotoOriginalHeight / currentImageAreaDimensions.height;

        detections.forEach(function(savedRectangle) {
            var scaledRectangle = {
                x1: blackPaddingSizeOnOneSide + savedRectangle.x1 / widthScale,
                y1: savedRectangle.y1 / heightScale,
                x2: blackPaddingSizeOnOneSide + savedRectangle.x2 / widthScale,
                y2: savedRectangle.y2 / heightScale
            };

            var detectionRectangle = getSavedDetectionRectangle(scaledRectangle, savedRectangle);
            detectionRectangle.appendTo(imageArea);
        });
    }, 200);
}

function refreshAnnotations() {
    getAllAnnotations(ObjectTagger.handleSavedRectanglesDrawn);
}

function getImageScaledDimensions(imageAreaCurrentSize) {
    var originalPhotoWidthToHeightRelation = window.currentPhotoOriginalWidth / window.currentPhotoOriginalHeight;

    var currentImageAreaDimensions = {
        width: parseInt(imageAreaCurrentSize.width),
        height: parseInt(imageAreaCurrentSize.height)
    };

    var scaledPhotoWidthWithoutPadding = currentImageAreaDimensions.height * originalPhotoWidthToHeightRelation;
    var blackPaddingSizeOnOneSide = (currentImageAreaDimensions.width - scaledPhotoWidthWithoutPadding) / 2;

    return {
        scaledPhotoWidthWithoutPadding: scaledPhotoWidthWithoutPadding,
        blackPaddingSizeOnOneSide: blackPaddingSizeOnOneSide,
        currentImageAreaDimensions: currentImageAreaDimensions
    };
}

function drawNewAnnotationRectangle(img, areaSelection) {
    var imgRealSize = img.getBoundingClientRect();

    var rectangle = {
        x1: areaSelection.x1,
        y1: areaSelection.y1,
        x2: areaSelection.x2,
        y2: areaSelection.y2
    };

    var photoDimensions = {
        width: parseInt(imgRealSize.width),
        height: parseInt(imgRealSize.height)
    };

    var widthScale = window.currentPhotoOriginalWidth / photoDimensions.width;
    var heightScale = window.currentPhotoOriginalHeight / photoDimensions.height;

    var scaledRectangle = {
        photoId: ObjectTagger.getPhotoId(),
        x1: areaSelection.x1 * widthScale,
        y1: areaSelection.y1 * heightScale,
        x2: areaSelection.x2 * widthScale,
        y2: areaSelection.y2 * heightScale
    };

    return getDetectionRectangle(rectangle, scaledRectangle);
}