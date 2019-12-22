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

function getScaledRectangleConfiguration(scaledRectangle, annotation, imageAreaDimensions) {
    var leftEdgeDistance = scaledRectangle.x1;
    var topEdgeDistance = scaledRectangle.y1;

    var width = (scaledRectangle.x2 - scaledRectangle.x1);
    var height = (scaledRectangle.y2 - scaledRectangle.y1);

    return {
        leftEdgeDistancePercentage: (leftEdgeDistance / imageAreaDimensions.width) * 100,
        topEdgeDistancePercentage: (topEdgeDistance / imageAreaDimensions.height) * 100,
        widthPercentage: (width / imageAreaDimensions.width) * 100,
        heightPercentage: (height / imageAreaDimensions.height) * 100,
        annotation: annotation
    };
}

function getSavedDetectionRectangle(scaledRectangle, annotation, imageAreaDimensions) {
    var configuration = getScaledRectangleConfiguration(scaledRectangle, annotation, imageAreaDimensions);

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

function getCurrentPhotoDimensionScalesInRelationToTheOriginalPhoto(imageAreaDimensions) {
    var widthScale = window.currentPhotoOriginalWidth / imageAreaDimensions.width;
    var heightScale = window.currentPhotoOriginalHeight / imageAreaDimensions.height;

    return {
        widthScale: widthScale,
        heightScale: heightScale
    };
}

function scaleRectangleForCurrentImageSize(scalingParametersForCurrentImageSize, savedRectangle) {
    var widthScale = scalingParametersForCurrentImageSize.widthScale;
    var heightScale = scalingParametersForCurrentImageSize.heightScale;

    return {
        x1: savedRectangle.x1 / widthScale,
        y1: savedRectangle.y1 / heightScale,
        x2: savedRectangle.x2 / widthScale,
        y2: savedRectangle.y2 / heightScale
    };
}

function drawDetectionRectangles(detections, imageAreaDimensions) {
    $('.popover').remove();

    createAnnotationFilters(detections);

    setTimeout(function() {
        removeExistingDetectionRectangles();

        var scalesInRelationToTheOriginalPhoto = getCurrentPhotoDimensionScalesInRelationToTheOriginalPhoto(imageAreaDimensions);

        detections.forEach(function(savedRectangle) {
            var scaledRectangle = scaleRectangleForCurrentImageSize(scalesInRelationToTheOriginalPhoto, savedRectangle);

            var detectionRectangle = getSavedDetectionRectangle(scaledRectangle, savedRectangle, imageAreaDimensions);
            detectionRectangle.appendTo(ImageAreaSelector.getImageArea());
        });

        if (window.photoModalCurrentPhotoFlipped) {
            mirrorDetectionAnnotations();
        }
    }, 200);
}

function refreshAnnotations() {
    getAllAnnotations(ObjectTagger.handleSavedRectanglesDrawn);
}

function getScreenWidthToHeightRelation() {
    return screen.width / screen.height;
}

function isPlacingBlackBordersOnSides() {
    var screenWidthToHeightRelation = getScreenWidthToHeightRelation();

    var imageWidthToHeightRelation = window.currentPhotoOriginalWidth / window.currentPhotoOriginalHeight;

    return imageWidthToHeightRelation - screenWidthToHeightRelation < 0;
}

function centerAnnotationContainerInRegardsToBlackBorders(annotationContainer, imageContainer) {
    var imageWidthToHeightRelation = window.currentPhotoOriginalWidth / window.currentPhotoOriginalHeight;
    var isHeightInFullLength = isPlacingBlackBordersOnSides();

    if (isHeightInFullLength) {
        var scaledWidth = imageContainer.height() * imageWidthToHeightRelation;
        var blackBorderSize = (imageContainer.width() - scaledWidth) / 2;

        annotationContainer.css({
            position: 'absolute',
            left: blackBorderSize + 'px',
            height: '100%',
            width: scaledWidth + 'px'
        });
    } else {
        var scaledHeight = imageContainer.width() / imageWidthToHeightRelation;
        var blackBorderSize = (imageContainer.height() - scaledHeight) / 2;

        annotationContainer.css({
            position: 'absolute',
            top: blackBorderSize + 'px',
            width: '100%',
            height: scaledHeight + 'px'
        });
    }
}

function drawAnnotationContainer(imageContainer, isRedraw) {
    var annotationContainer = $('<div>');

    centerAnnotationContainerInRegardsToBlackBorders(annotationContainer, imageContainer);

    imageContainer.append(annotationContainer);
    moveAnnotationRectanglesElement(annotationContainer, true);

    $('#' + constants.elements.ANNOTATION_CONTAINER_ID_ON_IMAGE).remove();
    annotationContainer.attr('id', constants.elements.ANNOTATION_CONTAINER_ID_ON_IMAGE);

    function onWindowResize() {
        drawAnnotationContainer(imageContainer, true);
    }

    if (!isRedraw) {
        window.addEventListener('resize', onWindowResize);

        addFullScreenExitListener(function() {
            window.removeEventListener('resize', onWindowResize);
            moveAnnotationRectanglesElement(ImageAreaSelector.getImageArea());
        });
    }
}

function drawNewAnnotationRectangle(areaSelection) {
    var imgRealSize = ImageAreaSelector.getImageAreaDimensions();

    var rectangle = {
        x1: areaSelection.x1,
        y1: areaSelection.y1,
        x2: areaSelection.x2,
        y2: areaSelection.y2
    };

    return getDetectionRectangle(rectangle, imgRealSize);
}