'use strict';

function setDefaultValue(options, defaultValue) {
    if (defaultValue) {
        options.filter(function(option) {
            if (option.value === defaultValue) {
                option.selected = true;
            }
        });
    }
}

function getAgeGroupSelect(customLabel, isDefaultHidden) {
    var specifyAgeGroup = constants.translations.selectAge.label.SPECIFY_AGE;
    var optional = constants.translations.common.OPTIONAL;
    var labelText = customLabel ? customLabel : specifyAgeGroup + ' (' + optional + ')';
    var hidden = isDefaultHidden ? 'display: none;' : '';

    var wrapper = $('<div>', {
        id: constants.elements.SUBJECT_AGE_GROUP_SELECT_WRAPPER_ID,
        style: hidden + 'padding-top: 5px; width: 180px;'
    });

    var label = $('<label>', {
        for: constants.elements.SUBJECT_AGE_GROUP_SELECT_ID
    });

    var select = $('<select>', {
        id: constants.elements.SUBJECT_AGE_GROUP_SELECT_ID,
        style: 'padding-bottom: 5px;'
    });

    return wrapper
        .append(label
            .append(labelText)
        )
        .append(select);
}

function initializeAgeGroupSelect(defaultValue) {
    var options = [
        {
            placeholder: true,
            text: constants.translations.common.UNSURE,
            value: constants.fieldValues.UNSURE
        },
        {
            text: constants.translations.common.CHILD,
            value: constants.fieldValues.CHILD
        },
        {
            text: constants.translations.common.ADULT,
            value: constants.fieldValues.ADULT
        },
        {
            text: constants.translations.common.ELDERLY,
            value: constants.fieldValues.ELDERLY
        }
    ];

    setDefaultValue(options, defaultValue);

    new SlimSelect({
        select: '#' + constants.elements.SUBJECT_AGE_GROUP_SELECT_ID,
        allowDeselect: true,
        data: options
    });
}

function getGenderGroupSelect(customLabel, isDefaultHidden) {
    var specifyAgeGroup = constants.translations.selectGender.label.SPECIFY_GENDER;
    var optional = constants.translations.common.OPTIONAL;
    var labelText = customLabel ? customLabel : specifyAgeGroup + ' (' + optional + ')';
    var hidden = isDefaultHidden ? 'display: none;' : '';

    var wrapper = $('<div>', {
        id: constants.elements.SUBJECT_GENDER_SELECT_WRAPPER_ID,
        style: hidden + 'padding-top: 5px; width: 180px;'
    });

    var label = $('<label>', {
        for: constants.elements.SUBJECT_GENDER_SELECT_ID
    });

    var select = $('<select>', {
        id: constants.elements.SUBJECT_GENDER_SELECT_ID,
        style: 'padding-bottom: 5px;'
    });

    return wrapper
        .append(label
            .append(labelText)
        )
        .append(select);
}

function initializeGenderGroupSelect(defaultValue) {
    var options = [
        {
            placeholder: true,
            text: constants.translations.common.UNSURE,
            value: constants.fieldValues.UNSURE
        },
        {
            text: constants.translations.common.MALE,
            value: constants.fieldValues.MALE
        },
        {
            text: constants.translations.common.FEMALE,
            value: constants.fieldValues.FEMALE
        },
        {
            text: constants.translations.common.UNSURE,
            value: constants.fieldValues.UNSURE
        },
    ];

    setDefaultValue(options, defaultValue);

    return new SlimSelect({
        select: '#' + constants.elements.SUBJECT_GENDER_SELECT_ID,
        allowDeselect: true,
        data: options
    });
}

function toggleSlimSelectError(slimSelectField, slimSelectErrorMessageField, isDisplayingError) {
    var objectFieldErrorClass = 'slim-select-error';
    var objectFieldErrorMessageClass = 'error-display';

    if (isDisplayingError) {
        slimSelectField.addClass(objectFieldErrorClass);
        slimSelectErrorMessageField.addClass(objectFieldErrorMessageClass);
    } else {
        slimSelectField.removeClass(objectFieldErrorClass);
        slimSelectErrorMessageField.removeClass(objectFieldErrorMessageClass);
    }
}
