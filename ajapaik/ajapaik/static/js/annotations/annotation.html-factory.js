'use strict';

function getToggleButton(leftLabel, rightLabel, onLeftClick, onRightClick) {
    var wrapper = $('<div>', {class: 'switch switch--horizontal'});

    var objectDetectionInput = $('<input>', {
        id: 'radio-a',
        type: 'radio',
        name: 'first-switch',
        checked: true
    }).on('click', onLeftClick);

    var objectDetectionLabel = $('<label>', {
        for: 'radio-a'
    }).on('click', onLeftClick).append(leftLabel);

    var faceDetectionInput = $('<input>', {
        id: 'radio-b',
        type: 'radio',
        name: 'first-switch'
    }).on('click', onRightClick);

    var faceDetectionLabel = $('<label>', {
        for: 'radio-b'
    }).on('click', onRightClick).append(rightLabel);

    var toggleOutside = $(
        '<span class="toggle-outside">' +
            '<span class="toggle-inside">' +
            '</span>' +
        '</span>'
    );

    return wrapper
        .append(objectDetectionInput)
        .append(objectDetectionLabel)
        .append(faceDetectionInput)
        .append(faceDetectionLabel)
        .append(toggleOutside);
}

function getSelectOption(id, label) {
    var option = new Option(label, id);
    $(option).html(label);

    return option;
}

function getSelect(isValueOptional, options, selectedValue) {
    var selectWrapper = $('<div>', {
        id: constants.elements.SELECT_OBJECT_CLASS_WRAPPER_ID
    });

    var select = $('<select>', {
        id: constants.elements.OBJECT_CLASS_SELECT_ID
    });

    if (selectedValue) {
        select.append(getSelectOption(selectedValue.id, selectedValue.label));
    } else if (isValueOptional) {
        var placeholder = $('<option data-placeholder="true"></option>');
        select.append(placeholder);
    }

    options.forEach(function (option) {
        var displayText = option.label;
        var optionValue = option.id;

        if (!(selectedValue && selectedValue.id === optionValue)) {
            select.append(getSelectOption(optionValue, displayText));
        }
    });

    return selectWrapper
        .append(select);
}

function getObjectsSelect(isValueOptional, selectedOption) {
    return getSelect(isValueOptional, [], selectedOption);
}

function handleCancel(event) {
    var button = $(event.target);
    var popoverId = button.data('popover-id');
    var isUnsavedRectangle = button.data('is-unsaved-rectangle');

    togglePopover(popoverId);

    setTimeout(function () {
        if (isUnsavedRectangle) {
            $('#' + popoverId).remove();
        }
    });
}

function getCancelButton(popoverId, isUnsavedRectangle) {
    var cancelButtonText = constants.translations.button.CANCEL;

    var cancelButton = $('<button>', {
        class: 'btn btn-outline-primary btn-block',
        'data-popover-id': popoverId,
        'data-is-unsaved-rectangle': !!isUnsavedRectangle,
        click: handleCancel,
        type: 'reset'
    });

    return cancelButton
        .append(cancelButtonText);
}

function getDeleteButton(onClick) {
    var deleteButtonText = constants.translations.button.DELETE;

    var deleteButton = $('<button>', {
        class: 'btn btn-danger btn-block',
        type: 'button'
    }).on('click', onClick);

    return deleteButton
        .append(deleteButtonText);

}

function getSubmitButton(style) {
    var submitButtonText = constants.translations.button.SUBMIT;

    var submitButton = $('<button>', {
        class: 'btn btn-primary btn-block',
        type: 'submit',
        style: style
    });

    return submitButton
        .append(submitButtonText);
}

function getSubmitAndCancelButtons(popoverId, isUnsavedRectangle) {
    var submitButton = getSubmitButton();
    var cancelButton = getCancelButton(popoverId, isUnsavedRectangle);

    var wrapper = $('<div style="padding-top: 10px;"></div>');

    return wrapper
        .append(submitButton)
        .append(cancelButton);
}

function getAddNewSubjectLink(addNewSubjectText) {
    var link = $('<a>', {
        href: '/face-recognition/add-subject/?_popup=1',
        id: constants.elements.ADD_NEW_SUBJECT_LINK_ID
    });

    return link.append(addNewSubjectText);
}

function getButtonGroup(buttons) {
    var wrapper = $('<div>', {
        id: constants.elements.POPOVER_CONTROL_BUTTONS_ID
    });

    buttons.forEach(function (button) {
        wrapper.append(button);
    });

    return wrapper;
}

function getPopoverCheckbox(labelText, wrapperId, labelId, checkboxName, checkboxId, onCheckboxClick) {
    if (!labelText) {
        return '';
    }

    var wrapper = $('<div>', {
        class: 'row',
        style: 'width: 180px; margin: 0;',
        id: wrapperId
    });
    var label = $('<label>', {
        id: labelId,
        for: 'isCorrectName',
        style: 'width: 92%;'
    });

    var input = $('<input>', {
        class: 'float-right',
        click: onCheckboxClick,
        type: 'checkbox',
        id: checkboxId,
        name: checkboxName,
        style: 'margin-top:auto; margin-bottom: auto;',
        checked: true
    });

    return wrapper
        .append(label
            .append(labelText)
        )
        .append(input);
}

function getAnnotationIdentifier(annotation) {
    if (!annotation.id) {
        return '';
    }

    if (!annotation.wikiDataId) {
        if (annotation.subjectId) {
            return 'face-' + annotation.subjectId;
        }

        return 'unknown-face-' + annotation.id;
    }

    return 'object-' + annotation.wikiDataId;
}

function createAnnotationRectangleWithPopover(popoverId, popoverTitle, popoverContent, configuration, onAnnotationRectangleShow, customBorder) {
    var border = customBorder ? customBorder : 'solid';

    var annotationRectangle = $('<div>', {
        id: popoverId,
        'data-is-detection-rectangle': true,
        'data-annotation-identifier': getAnnotationIdentifier(configuration.annotation),
        class: 'ajapaik-face-rectangle',
        css: {
            position: 'absolute',
            left: configuration.placementFromLeftEdge + 'px',
            top: configuration.placementFromTopEdge + 'px',
            width: configuration.width + 'px',
            height: configuration.height + 'px',
            border: '3px ' + border + ' white',
            'outline-style': 'solid',
            'outline-width': '1px'
        },
    });


    if (configuration.isAnnotationAreaModifiable) {
        DraggableArea.addResizeAndMoveControls(annotationRectangle, configuration);
    }

    annotationRectangle.on('click', function (event) {
        closePopoversOnRectangleClick(event);
    });

    annotationRectangle.popover({
        container: ObjectTagger.getDetectionRectangleContainer(),
        html: true,
        placement: 'bottom',
        title: popoverTitle,
        trigger: 'click',
        content: function() {
            return popoverContent;
        }
    });

    annotationRectangle.on('show.bs.popover', function () {
        if (onAnnotationRectangleShow) {
            onAnnotationRectangleShow();
        }
    });

    return annotationRectangle;
}
