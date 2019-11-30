'use strict';

function toggleEditObjectFieldError(isDisplayingError) {
    var objectField = $('#' + constants.elements.SELECT_OBJECT_CLASS_WRAPPER_ID);
    var objectFieldError = $('.invalid-feedback');
    toggleSlimSelectError(objectField, objectFieldError, isDisplayingError);
}

function getObjectRectangleUpdateSubmitFunction(rectangleId, popoverId, initialValue) {
    return function(event) {
        event.preventDefault();

        var form = $(event.target);
        var selectedObjectId = form
            .find("#" + constants.elements.OBJECT_CLASS_SELECT_ID)
            .val();

        var closePopover = function() {
            togglePopover(popoverId);
        };

        if (initialValue === selectedObjectId) {
            closePopover();
            return;
        }

        toggleEditObjectFieldError(!selectedObjectId);

        if (!selectedObjectId) {
            return;
        }

        var payload = {
            rectangleId: rectangleId,
            wikiDataLabelId: selectedObjectId
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

    var select = getObjectsSelect(false, {
        id: annotation.wikiDataId,
        label: JSON.parse(annotation.translations)[window.language]
    });


    var form = $('<form/>', {
        id: 'modify-detected-object'
    }).on('submit', getObjectRectangleUpdateSubmitFunction(annotation.id, popoverId, annotation.wikiDataId));

    var label = $('<span></span>');
    var changeObjectClassLabel = constants.translations.popover.labels.CHANGE_OBJECT_CLASS + ': ';

    label.append(changeObjectClassLabel);

    return form
        .append(label)
        .append(select)
        .append(buttonGroup);
}

function validateRequiredEditObjectField(selectedOption) {
    toggleEditObjectFieldError(!selectedOption.value);
}

function createSavedObjectModifyDetectionRectangle(popoverId, annotation, configuration) {
    var onAnnotationRectangleShow = function() {
        setTimeout(function() {
            initializeObjectAutocomplete(constants.elements.OBJECT_CLASS_SELECT_ID, false, validateRequiredEditObjectField);
        }, 100);
    };

    var popoverTitle = constants.translations.popover.titles.EDIT_OBJECT_ANNOTATION;

    var popoverContent = createSavedObjectAnnotationModifyPopoverContent(annotation, popoverId);

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleShow);
}