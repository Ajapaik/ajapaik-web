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
        var gender = form.find('#' + constants.elements.SUBJECT_GENDER_SELECT_ID).val();
        var ageGroup = form.find('#' + constants.elements.SUBJECT_AGE_GROUP_SELECT_ID).val();

        var payload = {
            annotationId: annotationId,
            newSubjectId: newSubjectId,
            gender: gender,
            ageGroup: ageGroup
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
    var ageGroupSelect = getAgeGroupSelect(constants.translations.selectAge.label.CHANGE_AGE);
    var genderGroupSelect = getGenderGroupSelect(constants.translations.selectGender.label.CHANGE_GENDER);
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
        .append(ageGroupSelect)
        .append(genderGroupSelect)
        .append(buttonGroup);
}

function createFaceAnnotationEditRectangle(popoverId, annotation, configuration) {
    var onAnnotationRectangleShow = function() {
      setTimeout(function() {
            initializePersonAutocomplete(constants.elements.SUBJECT_AUTOCOMPLETE_ID);
            initializeGenderGroupSelect(annotation.gender);
            initializeAgeGroupSelect(annotation.age);
        }, 100);
    };

    var popoverTitle = constants.translations.popover.titles.EDIT_FACE_ANNOTATION;

    var popoverContent = createDetectedFaceModifyPopoverContent(annotation, popoverId);

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleShow);
}