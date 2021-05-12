'use strict';

function getDetectedObjectRectangle(popoverId, annotation, configuration) {
    return createSavedObjectAnnotation(
        popoverId,
        annotation,
        configuration
    );
}

function getDetectedObjectModifyRectangle(rectangleId, savedRectangle, configuration) {
    return createSavedObjectModifyAnnotation(
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
    let leftEdgeDistance = scaledRectangle.x1;
    let topEdgeDistance = scaledRectangle.y1;

    let width = (scaledRectangle.x2 - scaledRectangle.x1);
    let height = (scaledRectangle.y2 - scaledRectangle.y1);

    return {
        leftEdgeDistancePercentage: (leftEdgeDistance / imageAreaDimensions.width) * 100,
        topEdgeDistancePercentage: (topEdgeDistance / imageAreaDimensions.height) * 100,
        widthPercentage: (width / imageAreaDimensions.width) * 100,
        heightPercentage: (height / imageAreaDimensions.height) * 100,
        annotation: annotation
    };
}

function getSavedAnnotation(scaledRectangle, annotation, imageAreaDimensions) {
    let configuration = getScaledRectangleConfiguration(scaledRectangle, annotation, imageAreaDimensions);

    if (annotation.wikiDataId) {
        return getDetectedObjectModifyRectangle(
            'ajp-object-modify-rectangle-' + annotation.id,
            annotation,
            configuration
        );
    } else {
        return getDetectedFaceModifyRectangle(
            'ajp-face-modify-rectangle-' + annotation.id,
            annotation,
            configuration
        );
    }
}

function removeExistingAnnotations() {
    $('[data-is-detection-rectangle]').each(function () {
        let rectangle = $(this);

        $('.popover:has(#add-object-class)').remove();
        $('.popover:has(#modify-detected-object)').remove();
        $('.popover:has(#modify-detected-object-annotation)').remove();
        rectangle.remove();
    });
}

function getCurrentPhotoDimensionScalesInRelationToTheOriginalPhoto(imageAreaDimensions) {
    let height = window.currentPhotoOriginalHeight;
    let width = window.currentPhotoOriginalWidth;

    let heightScale = height / imageAreaDimensions.height;
    let widthScale = width / imageAreaDimensions.width;

    return {
        widthScale: widthScale,
        heightScale: heightScale
    };
}

function scaleRectangleForCurrentImageSize(scalingParametersForCurrentImageSize, savedRectangle) {
    let widthScale = scalingParametersForCurrentImageSize.widthScale;
    let heightScale = scalingParametersForCurrentImageSize.heightScale;

    return {
        x1: savedRectangle.x1 / widthScale,
        y1: savedRectangle.y1 / heightScale,
        x2: savedRectangle.x2 / widthScale,
        y2: savedRectangle.y2 / heightScale
    };
}

function drawAnnotations(detections, imageAreaDimensions) {
    $('.popover:has(#add-object-class)').remove();
    $('.popover:has(#modify-detected-object)').remove();
    $('.popover:has(#modify-detected-object-annotation)').remove();

    createAnnotations(detections);

    setTimeout(function () {
        removeExistingAnnotations();

        let scalesInRelationToTheOriginalPhoto = getCurrentPhotoDimensionScalesInRelationToTheOriginalPhoto(imageAreaDimensions);

        detections.forEach(function(savedRectangle) {
            if (savedRectangle.id !== null) {
                let scaledRectangle = scaleRectangleForCurrentImageSize(scalesInRelationToTheOriginalPhoto, savedRectangle);
                let annotation = getSavedAnnotation(scaledRectangle, savedRectangle, imageAreaDimensions);
                if (window.isAnnotatingDisabledByButton) {
                    annotation.css('visibility', 'hidden');
                }
                annotation.appendTo(ImageAreaSelector.getImageArea());
            }
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

function isPlacingBlackBordersOnSides(imageWidthToHeightRelation) {
    let screenWidthToHeightRelation = getScreenWidthToHeightRelation();
    return imageWidthToHeightRelation - screenWidthToHeightRelation < 0;
}

function centerAnnotationContainerInRegardsToBlackBorders(annotationContainer, imageContainer) {
    let imageWidthToHeightRelation = window.currentPhotoOriginalWidth / window.currentPhotoOriginalHeight;
    let isHeightInFullLength = isPlacingBlackBordersOnSides(imageWidthToHeightRelation);

    if (isHeightInFullLength) {
        let scaledWidth = imageContainer.height() * imageWidthToHeightRelation;
        let blackBorderSize = (imageContainer.width() - scaledWidth) / 2;

        annotationContainer.css({
            position: 'absolute',
            left: blackBorderSize + 'px',
            height: '100%',
            width: scaledWidth + 'px'
        });
    } else {
        let scaledHeight = imageContainer.width() / imageWidthToHeightRelation;
        let blackBorderSize = (imageContainer.height() - scaledHeight) / 2;

        annotationContainer.css({
            position: 'absolute',
            top: blackBorderSize + 'px',
            width: '100%',
            height: scaledHeight + 'px'
        });
    }
}

function drawAnnotationContainer(imageContainer, isRedraw) {
    let annotationContainer = $('<div>');

    centerAnnotationContainerInRegardsToBlackBorders(annotationContainer, imageContainer);

    imageContainer.append(annotationContainer);
    moveAnnotations(annotationContainer, true);

    $('#' + constants.elements.ANNOTATION_CONTAINER_ID_ON_IMAGE).remove();
    annotationContainer.attr('id', constants.elements.ANNOTATION_CONTAINER_ID_ON_IMAGE);

    function onWindowResize() {
        drawAnnotationContainer(imageContainer, true);
    }

    if (!isRedraw) {
        window.addEventListener('resize', onWindowResize);

        addFullScreenExitListener(function () {
            window.removeEventListener('resize', onWindowResize);
            moveAnnotations(ImageAreaSelector.getImageArea());
        });
    }
}

function drawNewAnnotationRectangle(areaSelection) {
    let imgRealSize = ImageAreaSelector.getImageAreaDimensions();

    let rectangle = {
        x1: areaSelection.x1,
        y1: areaSelection.y1,
        x2: areaSelection.x2,
        y2: areaSelection.y2
    };

    return getAnnotation(rectangle, imgRealSize);
}