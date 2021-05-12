'use strict';

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
