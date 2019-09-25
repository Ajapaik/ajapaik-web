'use strict';

function getRemoveAnnotationFunction(annotationId, popoverId) {
    var onSuccess = function() {
        togglePopover(popoverId);
        refreshAnnotations();
    };

    return function() {
        removeFaceAnnotation(annotationId, onSuccess);
    };
}

function getModifySubmitFunction(annotationId, popoverId) {
    var onSuccess = function() {
        togglePopover(popoverId);
        refreshAnnotations();
    };

    return function(event) {
        event.preventDefault();

        var form = $(event.target);

        var newSubjectId = form
            .find('#' + constants.elements.SUBJECT_AUTOCOMPLETE_ID)
            .val();

        var payload = {
            annotationId: annotationId,
            newSubjectId: newSubjectId
        };

        editFaceAnnotation(annotationId, payload, onSuccess);
    };
}

function getDefaultValue(detectionRectangle) {
    if (detectionRectangle.subjectId) {
        return {
            label: detectionRectangle.subjectName,
            id: detectionRectangle.subjectId
        };
    }
}

function createDetectedFaceModifyPopoverContent(annotation, popoverId) {
    var defaultValue = getDefaultValue(annotation);
    var changeExistingFaceLabel = constants.translations.popover.labels.CHANGE_PERSON_NAME + ':';

    var autocomplete = getPersonAutoComplete(true, 'width: 180px;', defaultValue, changeExistingFaceLabel);
    var buttons = [
        getSubmitButton('margin-top: 10px;'),
        getDeleteButton(getRemoveAnnotationFunction(annotation.id, popoverId)),
        getCancelButton(popoverId)
    ];

    var buttonGroup = getButtonGroup(buttons);

    var form = $('<form/>', {
        id: 'modify-detected-object-annotation'
    }).on('submit', getModifySubmitFunction(annotation.id, popoverId));

    return form
        .append(autocomplete)
        .append(buttonGroup);
}

function createFaceAnnotationEditRectangle(popoverId, annotation, configuration) {
    var onAnnotationRectangleShow = function() {
      setTimeout(function() {
            initializePersonAutocomplete(constants.elements.SUBJECT_AUTOCOMPLETE_ID);
        }, 100);
    };

    var popoverTitle = constants.translations.popover.titles.EDIT_FACE_ANNOTATION;

    var popoverContent = createDetectedFaceModifyPopoverContent(annotation, popoverId);

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleShow);
}