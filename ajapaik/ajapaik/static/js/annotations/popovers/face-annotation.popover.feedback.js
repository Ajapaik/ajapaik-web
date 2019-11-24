'use strict';

function isCorrectPersonName(form) {
    var isCorrectPersonNameCheckbox = form.find('#' + constants.elements.IS_CORRECT_PERSON_NAME_CHECKBOX_ID);

    if (isCorrectPersonNameCheckbox.length > 0) {
        return isCorrectPersonNameCheckbox.is(':checked');
    }

    return null;
}

function getSubmitDetectedFaceFeedbackFunction(annotationId, popoverId) {
    var onSuccess = function() {
        togglePopover(popoverId);
        refreshAnnotations();
    };

    return function(event) {
        event.preventDefault();

        var form = $(event.target);

        var isFaceAnnotation = form
            .find('#' + constants.elements.IS_FACE_ANNOTATION_CHECKBOX_ID)
            .is(':checked');

        var isCorrectGender = form
            .find('#' + constants.elements.IS_CORRECT_GENDER_CHECKBOX_ID)
            .is(':checked');

        var isCorrectAge = form
            .find('#' + constants.elements.IS_CORRECT_AGE_CHECKBOX_ID)
            .is(':checked');

        var isCorrectName = isCorrectPersonName(form);

        var newSubjectId = form
            .find('#' + constants.elements.SUBJECT_AUTOCOMPLETE_ID)
            .val();
        var gender = form.find('#' + constants.elements.SUBJECT_GENDER_SELECT_ID).val();
        var ageGroup = form.find('#' + constants.elements.SUBJECT_AGE_GROUP_SELECT_ID).val();

        var payload = {
            alternativeSubjectId: newSubjectId,
            isFaceAnnotation: isFaceAnnotation,
            isCorrectName: isCorrectName,
            isCorrectGender: isCorrectGender,
            alternativeGender: isCorrectGender ? null : gender,
            isCorrectAge: isCorrectAge,
            alternativeAgeGroup: isCorrectAge ? null : ageGroup
        };

        addFaceAnnotationFeedback(annotationId, payload, onSuccess);
    };
}

function toggleElements(isChecked, labelId, inputId) {
    if (!isChecked) {
        $('#' + labelId).css('text-decoration', 'line-through');
        $('#' + inputId).show();
    } else {
        $('#' + labelId).css('text-decoration', '');
        $('#' + inputId).hide();
    }
}

function toggleFieldsOtherThanIsFace(event) {
    var isFaceCheckboxChecked = event.target.checked;

    if (!isFaceCheckboxChecked) {
        $('#' + constants.elements.IS_FACE_CHECKBOX_LABEL_ID).css('text-decoration', 'line-through');
        $('#' + constants.elements.ANNOTATION_MORE_SPECIFIC_FIELDS_WRAPPER_ID).hide();
    } else {
        $('#' + constants.elements.IS_FACE_CHECKBOX_LABEL_ID).css('text-decoration', '');
        $('#' + constants.elements.ANNOTATION_MORE_SPECIFIC_FIELDS_WRAPPER_ID).show();
    }
}

function toggleSubjectAge(event) {
    var isCorrectAge = event.target.checked;
    toggleElements(isCorrectAge, constants.elements.IS_CORRECT_AGE_CHECKBOX_LABEL_ID, constants.elements.SUBJECT_AGE_GROUP_SELECT_WRAPPER_ID);
}

function toggleSubjectGender(event) {
    var isCorrectGender = event.target.checked;
    toggleElements(isCorrectGender, constants.elements.IS_CORRECT_GENDER_CHECKBOX_ID, constants.elements.SUBJECT_GENDER_SELECT_WRAPPER_ID);
}

function getFaceCheckbox() {
    var label = constants.translations.popover.labels.IS_THIS_A_FACE_ANNOTATION + '?';

    return getPopoverCheckbox(
        label,
        '',
        constants.elements.IS_FACE_CHECKBOX_LABEL_ID,
        'isFace',
        constants.elements.IS_FACE_ANNOTATION_CHECKBOX_ID,
        toggleFieldsOtherThanIsFace
    );
}

function getGenderCheckbox(savedGender) {
    if (!savedGender) {
        return;
    }

    var capitalizedGender = gettext(capitalizeFirstLetter(savedGender));
    var label = constants.translations.popover.labels.IS_CORRECT_GENDER_PREFIX + ' ' + capitalizedGender + '?';

    return getPopoverCheckbox(
        label,
        '',
        constants.elements.IS_CORRECT_GENDER_CHECKBOX_LABEL_ID,
        'isCorrectGender',
        constants.elements.IS_CORRECT_GENDER_CHECKBOX_ID,
        toggleSubjectGender
    );
}

function getAgeCheckbox(savedAge) {
    if (!savedAge) {
        return;
    }

    var capitalizedAgeGroup = gettext(capitalizeFirstLetter(savedAge));
    var label = constants.translations.popover.labels.IS_CORRECT_AGE_PREFIX + ' ' + capitalizedAgeGroup + '?';

    return getPopoverCheckbox(
        label,
        '',
        constants.elements.IS_CORRECT_AGE_CHECKBOX_LABEL_ID,
        'isCorrectAge',
        constants.elements.IS_CORRECT_AGE_CHECKBOX_ID,
        toggleSubjectAge
    );
}

function toggleSubjectNameAssigning(event) {
    var isCorrectSubjectName = event.target.checked;

    if (!isCorrectSubjectName) {
        $('#' + constants.elements.IS_CORRECT_SUBJECT_NAME_LABEL_ID).css('text-decoration', 'line-through');
        $('#' + constants.elements.AUTOCOMPLETE_WRAPPER_ID).show();
    } else {
        $('#' + constants.elements.IS_CORRECT_SUBJECT_NAME_LABEL_ID).css('text-decoration', '');
        $('#' + constants.elements.AUTOCOMPLETE_WRAPPER_ID).hide();
    }
}

function getPersonNameCheckbox(customLabel) {
    if (!customLabel) {
        return '';
    }

    var labelText = customLabel + '?';

    return getPopoverCheckbox(
        labelText,
        'subject-name-line',
        'subject-name',
        'isCorrectName',
        constants.elements.IS_CORRECT_PERSON_NAME_CHECKBOX_ID,
        toggleSubjectNameAssigning
    );
}

function createTextRow(label, value) {
    var wrapper = $('<div>');
    var labelWrapper = $('<span style="font-weight: bold;">')
        .append(label)
        .append(': ');
    var valueWrapper = $('<span>')
        .append(value);

    return wrapper
        .append(labelWrapper)
        .append(valueWrapper);
}

function isAdditionalPropertyPresent(propertyValue) {
    return propertyValue && propertyValue.toUpperCase() !== constants.fieldValues.UNSURE;
}

function createUserOwnAnnotationPopoverContent(annotation, controlButtons) {
    var wrapper = $('<div>')
        .append(createTextRow(
            constants.translations.popover.labels.OWN_ANNOTATION_FIELD_TYPE,
            constants.translations.popover.labels.FACE_ANNOTATION
        ));

    if (annotation.subjectName) {
        wrapper.append(createTextRow(
            constants.translations.popover.labels.OWN_ANNOTATION_FIELD_PERSON,
            annotation.subjectName
        ));
    }

    if (isAdditionalPropertyPresent(annotation.age)) {
        wrapper.append(createTextRow(
            constants.translations.popover.labels.OWN_ANNOTATION_FIELD_AGE,
            gettext(capitalizeFirstLetter(annotation.age))
        ));
    }

    if (isAdditionalPropertyPresent(annotation.gender)) {
        wrapper.append(createTextRow(
            constants.translations.popover.labels.OWN_ANNOTATION_FIELD_GENDER,
            gettext(capitalizeFirstLetter(annotation.gender))
        ));
    }

    return wrapper.append(controlButtons);
}

function createDetectedFacePopoverContent(popoverId, annotation) {
    var controlButtons = getSubmitAndCancelButtons(popoverId, false, annotation.isAddedByCurrentUser);

    if (annotation.isAddedByCurrentUser) {
        return createUserOwnAnnotationPopoverContent(annotation, controlButtons);
    }

    var isAnnotationWithPersonName = !!annotation.subjectName;

    var autocomplete = getPersonAutoComplete(!isAnnotationWithPersonName, 'width: 180px;');
    var faceCheckbox = getFaceCheckbox();
    var ageGroupCheckbox = getAgeCheckbox(annotation.age);
    var ageGroupSelect = getAgeGroupSelect(null, isAdditionalPropertyPresent(annotation.age));
    var genderCheckbox = getGenderCheckbox(annotation.gender);
    var genderSelect = getGenderGroupSelect(null, isAdditionalPropertyPresent(annotation.gender));
    var specificDataFieldsWrapper = $('<div>', {id: constants.elements.ANNOTATION_MORE_SPECIFIC_FIELDS_WRAPPER_ID});

    var form = $('<form>', {
        id: 'feedback-on-detected-face',
        submit: getSubmitDetectedFaceFeedbackFunction(annotation.id, popoverId),
        'data-popover-id': popoverId,
        'data-rectangle-id': annotation.id
    });

    var inputWrapper = $('<div class="form-group" style="padding-right:5px; padding-left:5px;"></div>');
    var nameInputWrapper = $('<div>', {
        id: constants.elements.PERSON_NAME_FIELDS_WRAPPER_ID
    });

    if (isAnnotationWithPersonName) {
        var label = constants.translations.popover.labels.IS_CORRECT_SUBJECT_NAME_PREFIX + ' ' + annotation.subjectName + '?';
        var personNameCheckbox = getPersonNameCheckbox(label);
        nameInputWrapper.append(personNameCheckbox);
    }

    specificDataFieldsWrapper
        .append(nameInputWrapper
            .append(autocomplete)
        );

    if (isAdditionalPropertyPresent(annotation.age)) {
        specificDataFieldsWrapper.append(ageGroupCheckbox);
    }

    specificDataFieldsWrapper.append(ageGroupSelect);

    if (isAdditionalPropertyPresent(annotation.gender)) {
        specificDataFieldsWrapper.append(genderCheckbox);
    }

    specificDataFieldsWrapper.append(genderSelect);

    return form.append(inputWrapper
        .append(faceCheckbox)
        .append(specificDataFieldsWrapper)
        .append(controlButtons)
    );
}

function getFeedbackPopoverTitle(annotation) {
    if (annotation.isAddedByCurrentUser) {
        return constants.translations.popover.titles.ANNOTATION_ADDED_BY_YOU;
    }

    if (annotation.hasUserGivenFeedback) {
        return constants.translations.popover.titles.EDIT_FEEDBACK;
    }

    return constants.translations.popover.titles.ADD_FEEDBACK;
}

function createSavedFaceDetectionRectangle(popoverId, annotation, configuration) {
    var onAnnotationRectangleShow = function() {
      setTimeout(function() {
            if (!annotation.isAddedByCurrentUser) {
                initializePersonAutocomplete(constants.elements.SUBJECT_AUTOCOMPLETE_ID);
                initializeAgeGroupSelect();
                initializeGenderGroupSelect();
            }
        }, 100);
    };

    var popoverTitle = getFeedbackPopoverTitle(annotation);

    var $popoverContent = createDetectedFacePopoverContent(popoverId, annotation);

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, $popoverContent, configuration, onAnnotationRectangleShow);
}