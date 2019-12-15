'use strict';

function toggleNewObjectFieldError(isDisplayingError) {
    var objectField = $('#' + constants.elements.SELECT_OBJECT_CLASS_WRAPPER_ID);
    var objectFieldError = $('#' + constants.elements.NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID + ' .invalid-feedback');
    toggleSlimSelectError(objectField, objectFieldError, isDisplayingError);
}

function getRectangleSubmitFunction(popoverId) {
    return function(event) {
        event.preventDefault();

        var form = $(event.target);

        var isObjectSelected = form.data('selected') === 'object';

        var selectedObjectId = form.find("#" + constants.elements.OBJECT_CLASS_SELECT_ID).val();
        var personId = form.find('#' + constants.elements.SUBJECT_AUTOCOMPLETE_ID).val();
        var gender = form.find('#' + constants.elements.SUBJECT_GENDER_SELECT_ID).val();
        var ageGroup = form.find('#' + constants.elements.SUBJECT_AGE_GROUP_SELECT_ID).val();

        if (isObjectSelected) {
            toggleNewObjectFieldError(!selectedObjectId);

            if (!selectedObjectId) {
                return;
            }
        }

        var scaledRectangle = getDetectionRectangleScaledForOriginalImageSize(
            popoverId,
            ImageAreaSelector.getImageAreaDimensions()
        );
        togglePopover(popoverId);

        var payload = {
            isSavingObject: isObjectSelected,
            wikiDataLabelId: isObjectSelected ? selectedObjectId : null,
            subjectId: !isObjectSelected ? personId : null,
            photoId: scaledRectangle.photoId,
            gender: gender,
            ageGroup: ageGroup,
            x1: scaledRectangle.x1,
            x2: scaledRectangle.x2,
            y1: scaledRectangle.y1,
            y2: scaledRectangle.y2
        };

        addNewDetectionAnnotation(payload, refreshAnnotations);
    };
}

function toggleFaceDetection() {
    $('#' + constants.elements.NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID).hide();
    $('#' + constants.elements.ADD_NEW_FACE_FIELDS_WRAPPER_ID).show();
    $('#' + constants.elements.NEW_ANNOTATION_FORM_ID).data('selected', 'face');
}

function toggleObjectDetection() {
    $('#' + constants.elements.NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID).show();
    $('#' + constants.elements.ADD_NEW_FACE_FIELDS_WRAPPER_ID).hide();
    $('#' + constants.elements.NEW_ANNOTATION_FORM_ID).data('selected', 'object');

    document.getElementById(constants.elements.OBJECT_CLASS_SELECT_ID).slim.open();
}

function createObjectAssigningPopoverContent(popoverId) {
    var faceLabel = constants.translations.popover.labels.FACE_ANNOTATION;
    var objectLabel = constants.translations.popover.labels.OBJECT_ANNOTATION;

    var objectAutocomplete = getObjectsSelect();
    var controlButtons = getSubmitAndCancelButtons(popoverId, true);
    var detectionTypeToggle = getToggleButton(objectLabel, faceLabel, toggleObjectDetection, toggleFaceDetection);
    var autocomplete = getPersonAutoComplete(true);
    var ageGroupSelect = getAgeGroupSelect();
    var genderSelect = getGenderGroupSelect();

    var formWrapper = $('<div></div>');

    var form = $('<form>', {
        id: constants.elements.NEW_ANNOTATION_FORM_ID,
        submit: getRectangleSubmitFunction(popoverId),
        'data-selected': 'object'
    });

    var wrapper = $('<div style="padding-top: 5px;"></div>');
    var subjectFieldsWrapper = $('<div>', {
        id: constants.elements.ADD_NEW_FACE_FIELDS_WRAPPER_ID,
        style: 'display: none'
    });
    var objectSelectWrapper = $('<div>', {
        id: constants.elements.NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID,
        style: 'padding-bottom: 15px;'
    });
    var errorMessage = $('<div class="invalid-feedback">')
        .append(constants.translations.errors.OBJECT_REQUIRED);

    return formWrapper.append(
        form
            .append(wrapper
                .append(detectionTypeToggle)
                .append(subjectFieldsWrapper
                    .append(autocomplete)
                    .append(ageGroupSelect)
                    .append(genderSelect)
                )

            )
            .append(objectSelectWrapper
                .append(objectAutocomplete)
                .append(errorMessage)
            )
            .append(controlButtons)
    );
}

function validateRequiredNewObjectField(selectedOption) {
    toggleNewObjectFieldError(!selectedOption.value);
}

function createNewDetectionRectangle(popoverId, configuration) {
    var hasInitializedSelects = false;

    var onAnnotationRectangleShow = function() {
        if (!hasInitializedSelects) {
            setTimeout(function() {
                initializePersonAutocomplete(constants.elements.SUBJECT_AUTOCOMPLETE_ID);
                initializeAgeGroupSelect();
                initializeGenderGroupSelect();

                initializeObjectAutocomplete(constants.elements.OBJECT_CLASS_SELECT_ID, true, validateRequiredNewObjectField);

                hasInitializedSelects = true;
            }, 100);
        }
    };

    var popoverTitle = constants.translations.popover.titles.NEW_ANNOTATION + '?';
    var popoverContent = createObjectAssigningPopoverContent(popoverId);

    configuration.annotation = {};
    configuration.isAnnotationAreaModifiable = true;

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleShow, 'dashed');
}