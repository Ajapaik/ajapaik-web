'use strict';

function getRectangleSubmitFunction(scaledRectangle, popoverId) {
    return function(event) {
        event.preventDefault();

        var form = $(event.target);

        var isObjectSelected = form.data('selected') === 'object';

        var selectedObjectId = form.find("#" + constants.elements.OBJECT_CLASS_SELECT_ID).val();
        var personId = form.find('#' + constants.elements.SUBJECT_AUTOCOMPLETE_ID).val();

        togglePopover(popoverId);

        var payload = {
            wikiDataLabelId: isObjectSelected ? selectedObjectId : null,
            subjectId: !isObjectSelected ? personId : null,
            photoId: scaledRectangle.photoId,
            x1: scaledRectangle.x1,
            x2: scaledRectangle.x2,
            y1: scaledRectangle.y1,
            y2: scaledRectangle.y2
        };

        addNewDetectionAnnotation(payload, refreshAnnotations);
    };
}

function toggleFaceDetection() {
    $('#' + constants.elements.SELECT_OBJECT_CLASS_WRAPPER_ID).hide();
    $('#' + constants.elements.AUTOCOMPLETE_WRAPPER_ID).show();
    $('#' + constants.elements.NEW_ANNOTATION_FORM_ID).data('selected', 'face');
}

function toggleObjectDetection() {
    $('#' + constants.elements.SELECT_OBJECT_CLASS_WRAPPER_ID).show();
    $('#' + constants.elements.AUTOCOMPLETE_WRAPPER_ID).hide();
    $('#' + constants.elements.NEW_ANNOTATION_FORM_ID).data('selected', 'object');
}

function createObjectAssigningPopoverContent(popoverId, scaledRectangle) {
    var faceLabel = constants.translations.popover.labels.FACE_ANNOTATION;
    var objectLabel = constants.translations.popover.labels.OBJECT_ANNOTATION;

    var select = getObjectsSelect();
    var controlButtons = getSubmitAndCancelButtons(popoverId, true);
    var detectionTypeToggle = getToggleButton(objectLabel, faceLabel, toggleObjectDetection, toggleFaceDetection);
    var autocomplete = getPersonAutoComplete();

    var formWrapper = $('<div></div>');

    var form = $('<form>', {
        id: constants.elements.NEW_ANNOTATION_FORM_ID,
        submit: getRectangleSubmitFunction(scaledRectangle, popoverId),
        'data-selected': 'object'
    });

    var wrapper = $('<div style="padding-top: 5px;"></div>');
    var selectWrapper = $('<div style="padding-bottom: 15px;"></div>');

    return formWrapper.append(
        form
            .append(wrapper
                .append(detectionTypeToggle)
                .append(autocomplete)
            )
            .append(selectWrapper
                .append(select)
            )
            .append(controlButtons)
    );
}

function createNewDetectionRectangle(popoverId, scaledRectangle, configuration) {
    var onAnnotationRectangleClick = function() {
        setTimeout(function() {
            initializePersonAutocomplete(constants.elements.SUBJECT_AUTOCOMPLETE_ID);
            initializeObjectAutocomplete(constants.elements.OBJECT_CLASS_SELECT_ID);
        }, 200);
    };

    var popoverTitle = constants.translations.popover.titles.NEW_ANNOTATION + '?';
    var popoverContent = createObjectAssigningPopoverContent(popoverId, scaledRectangle);

    configuration.annotation = {};
    configuration.isAnnotationAreaModifiable = true;

    return createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleClick, 'dashed');
}