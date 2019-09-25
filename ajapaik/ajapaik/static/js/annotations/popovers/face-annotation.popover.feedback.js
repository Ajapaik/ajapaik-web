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

        var isCorrectName = isCorrectPersonName(form);

        var newSubjectId = form
            .find('#' + constants.elements.SUBJECT_AUTOCOMPLETE_ID)
            .val();

        var payload = {
            alternativeSubjectId: newSubjectId,
            isFaceAnnotation: isFaceAnnotation,
            isCorrectName: isCorrectName
        };

        addFaceAnnotationFeedback(annotationId, payload, onSuccess);
    };
}

function toggleSubjectName(event) {
    var isFace = event.target.checked;

    if (!isFace) {
        $('#' + constants.elements.IS_FACE_CHECKBOX_LABEL_ID).css('text-decoration', 'line-through');
        $('#' + constants.elements.PERSON_NAME_FIELDS_WRAPPER_ID).hide();
    } else {
        $('#' + constants.elements.IS_FACE_CHECKBOX_LABEL_ID).css('text-decoration', '');
        $('#' + constants.elements.PERSON_NAME_FIELDS_WRAPPER_ID).show();
    }
}

function getFaceCheckbox() {
    var label = constants.translations.popover.labels.IS_THIS_A_FACE_ANNOTATION + '?';

    return getPopoverCheckbox(
        label,
        '',
        constants.elements.IS_FACE_CHECKBOX_LABEL_ID,
        'isFace',
        constants.elements.IS_FACE_ANNOTATION_CHECKBOX_ID,
        toggleSubjectName
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

function createDetectedFacePopoverContent(popoverId, annotation) {
    var isAnnotationWithPersonName = !!annotation.subjectName;

    var controlButtons = getSubmitAndCancelButtons(popoverId);
    var autocomplete = getPersonAutoComplete(!isAnnotationWithPersonName, 'width: 180px;');
    var faceCheckbox = getFaceCheckbox();

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

    return form
        .append(inputWrapper
            .append(faceCheckbox)
            .append(nameInputWrapper
                .append(autocomplete)
            )
            .append(controlButtons)
        );
}

function createSavedFaceDetectionRectangle(popoverId, annotation, configuration) {
    var onAnnotationRectangleShow = function() {
      setTimeout(function() {
            initializePersonAutocomplete(constants.elements.SUBJECT_AUTOCOMPLETE_ID);
        }, 100);
    };

    var popoverTitle = annotation.hasUserGivenFeedback
        ? constants.translations.popover.titles.EDIT_FEEDBACK
        : constants.translations.popover.titles.ADD_FEEDBACK;

    var $popoverContent = createDetectedFacePopoverContent(popoverId, annotation);

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, $popoverContent, configuration, onAnnotationRectangleShow);
}