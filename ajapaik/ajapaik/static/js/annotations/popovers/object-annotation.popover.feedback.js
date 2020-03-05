'use strict';

function getSubmitObjectAnnotationFeedbackFunction(popoverId, annotationId) {
    var onSuccess = function() {
        togglePopover(popoverId);
        refreshAnnotations();
    };

    return function(event) {
        event.preventDefault();

        var form = $(event.target);

        var newObjectId = form
            .find('#' + constants.elements.OBJECT_CLASS_SELECT_ID)
            .val();

        var isConfirmed = form
            .find('#' + constants.elements.IS_CORRECT_OBJECT_CHECKBOX_ID)
            .is(':checked');

        var payload = {
            alternativeWikiDataLabelId: newObjectId,
            isConfirmed: isConfirmed
        };

        addObjectAnnotationFeedback(annotationId, payload, onSuccess);
    };
}

function toggleAlternativeObjectSelect(event) {
    var isCorrectObjectType = event.target.checked;

    if (!isCorrectObjectType) {
        $('#' + constants.elements.IS_OBJECT_CHECKBOX_LABEL_ID).css('text-decoration', 'line-through');
        $('#' + constants.elements.ALTERNATIVE_OBJECT_SELECT_WRAPPER_ID).show();
    } else {
        $('#' + constants.elements.IS_OBJECT_CHECKBOX_LABEL_ID).css('text-decoration', '');
        $('#' + constants.elements.ALTERNATIVE_OBJECT_SELECT_WRAPPER_ID).hide();
    }
}

function getObjectClassCheckbox(customLabelText, defaultValue) {
    var isChecked = getDefaultBooleanCheckboxValue(defaultValue);
    var labelText = customLabelText + '?';

    var wrapper = $('<div style="width: 180px;"></div>');
    var label= $('<span>', {
        id: constants.elements.IS_OBJECT_CHECKBOX_LABEL_ID,
        style: isChecked ? '' : 'text-decoration: line-through'
    });

    var input = $('<input>', {
        class: 'float-right',
        type: 'checkbox',
        id: constants.elements.IS_CORRECT_OBJECT_CHECKBOX_ID,
        name: 'isCorrectObject',
        style: 'margin-top:5px;',
        checked: isChecked
    }).on('click', toggleAlternativeObjectSelect);

    return wrapper
        .append(label
            .append(labelText)
        )
        .append(input);
}

function getObjectDefaultValue(annotation) {
    var previousFeedback = annotation.previousFeedback;

    if (previousFeedback && previousFeedback.alternativeObjectId) {
        return {
            id: previousFeedback.alternativeObjectId,
            label: getLanguageSpecificTranslation(previousFeedback.alternativeObjectTranslations)
        };
    }
}

function createUserOwnAnnotationObjectPopoverContent(annotation, cancelButton) {
    var wrapper = $('<div>');

    return wrapper
        .append(createTextRow(
            constants.translations.popover.labels.OWN_ANNOTATION_FIELD_TYPE,
            constants.translations.popover.labels.OBJECT_ANNOTATION
        ))
        .append(createTextRow(
            constants.translations.popover.labels.OWN_ANNOTATION_FIELD_OBJECT,
            getLanguageSpecificTranslation(annotation.translations)
        ))
        .append(cancelButton);
}

function createDetectedObjectPopoverContent(annotation, popoverId) {
    var cancelButton = getCancelButton(popoverId);

        return createUserOwnAnnotationObjectPopoverContent(annotation, cancelButton);
}

function getObjectFeedbackPopoverTitle(annotation) {
    if (annotation.isAddedByCurrentUser) {
        return constants.translations.popover.titles.ANNOTATION_ADDED_BY_YOU;
    }

    if (annotation.hasUserGivenFeedback) {
        return constants.translations.popover.titles.EDIT_FEEDBACK;
    }

    return constants.translations.popover.titles.ADD_FEEDBACK;
}

function createSavedObjectDetectionRectangle(popoverId, annotation, configuration) {
    var hasInitializedSelects = false;

    var onAnnotationRectangleShow = function() {
        if (!hasInitializedSelects) {
            setTimeout(function() {
                initializeObjectAutocomplete(constants.elements.OBJECT_CLASS_SELECT_ID);
                hasInitializedSelects = true;
            }, 150);
        }
    };

    var popoverTitle = getObjectFeedbackPopoverTitle(annotation);

    var popoverContent = createDetectedObjectPopoverContent(annotation, popoverId);

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleShow);
}