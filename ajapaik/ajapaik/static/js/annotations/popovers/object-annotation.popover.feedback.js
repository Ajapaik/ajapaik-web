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

function getObjectClassCheckbox(customLabelText) {
    var labelText = customLabelText + '?';

    var wrapper = $('<div style="width: 180px;"></div>');
    var label= $('<span>', {
        id: constants.elements.IS_OBJECT_CHECKBOX_LABEL_ID
    });

    var input = $('<input>', {
        class: 'float-right',
        type: 'checkbox',
        id: constants.elements.IS_CORRECT_OBJECT_CHECKBOX_ID,
        name: 'isCorrectObject',
        style: 'margin-top:5px;',
        checked: true
    }).on('click', toggleAlternativeObjectSelect);

    return wrapper
        .append(label
            .append(labelText)
        )
        .append(input);
}

function createDetectedObjectPopoverContent(annotation, popoverId) {
    var selectText = gettext('Specify alternative object (optional)') + ':';

    var buttons = [
        getSubmitButton(),
        getCancelButton(popoverId)
    ];

    var buttonGroup = getButtonGroup(buttons);

    var select = getObjectsSelect(true);

    var form = $('<form>', {
        id: 'feedback-on-detected-object'
    }).on('submit', getSubmitObjectAnnotationFeedbackFunction(popoverId, annotation.id));

    var inputsWrapper = $('<div class="form-group" style="padding-right:5px; padding-left:5px;"></div>');
    var questionPrefix = constants.translations.popover.labels.IS_CORRECT_OBJECT_PREFIX;
    var translatedLabel = JSON.parse(annotation.translations)[window.language];
    var objectClassCheckbox = getObjectClassCheckbox(questionPrefix + ' ' + translatedLabel);

    var alternativeObjectSelectWrapper = $('<div>', {
        id: constants.elements.ALTERNATIVE_OBJECT_SELECT_WRAPPER_ID,
        style: 'display: none; padding-top: 5px; width: 180px;'
    });

    return form
        .append(inputsWrapper
            .append(objectClassCheckbox)
            .append(alternativeObjectSelectWrapper
                .append(selectText)
                .append(select)
            )
        )
        .append(buttonGroup);
}

function createSavedObjectDetectionRectangle(popoverId, annotation,configuration) {
    var onAnnotationRectangleShow = function() {
        setTimeout(function() {
            initializeObjectAutocomplete(constants.elements.OBJECT_CLASS_SELECT_ID);
        }, 100);
    };

    var popoverTitle = annotation.hasUserGivenFeedback
        ? constants.translations.popover.titles.EDIT_FEEDBACK
        : constants.translations.popover.titles.ADD_FEEDBACK;

    var popoverContent = createDetectedObjectPopoverContent(annotation, popoverId);

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleShow);
}