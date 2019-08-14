'use strict';

function getObjectRectangleUpdateSubmitFunction(rectangleId, popoverId) {
    return function(event) {
        event.preventDefault();

        var form = $(event.target);
        var selectedObjectId = form
            .find("#" + constants.elements.OBJECT_CLASS_SELECT_ID)
            .val();

        var payload = {
            rectangleId: rectangleId,
            objectId: selectedObjectId
        };

        var closePopover = function() {
            togglePopover(popoverId);
        };

        updateExistingObjectDetectionAnnotation(payload, closePopover);
    };
}

function getDeleteObjectAnnotationFunction(popoverId, annotationId) {
    var onSuccess = function() {
        togglePopover(popoverId);
        refreshAnnotations();
    };

    return function() {
        deleteSavedObjectAnnotation(annotationId, onSuccess);
    };
}

function createSavedObjectAnnotationModifyPopoverContent(annotation, popoverId) {
    var buttons = [
        getSubmitButton('margin-top: 10px;'),
        getDeleteButton(getDeleteObjectAnnotationFunction(popoverId, annotation.id)),
        getCancelButton(popoverId)
    ];
    var buttonGroup = getButtonGroup(buttons);

    var select = getObjectsSelect(false, {id: annotation.objectId, label: annotation.objectLabel});


    var form = $('<form/>', {
        id: 'modify-detected-object'
    }).on('submit', getObjectRectangleUpdateSubmitFunction(annotation.id, popoverId));

    var label = $('<span></span>');
    var changeObjectClassLabel = gettext(constants.translations.popover.labels.CHANGE_OBJECT_CLASS) + ': ';

    label.append(changeObjectClassLabel);

    return form
        .append(label)
        .append(select)
        .append(buttonGroup);
}

function createSavedObjectModifyDetectionRectangle(popoverId, annotation, configuration) {
    var onAnnotationRectangleClick = function() {
        setTimeout(function() {
            new SlimSelect({
              select: '#' + constants.elements.OBJECT_CLASS_SELECT_ID
            });
        }, 200);
    };

    var popoverTitle = gettext(constants.translations.popover.titles.EDIT_OBJECT_ANNOTATION);

    var popoverContent = createSavedObjectAnnotationModifyPopoverContent(annotation, popoverId);

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleClick);
}