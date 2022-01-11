'use strict';

function toggleSlimSelectError(
  slimSelectField,
  slimSelectErrorMessageField,
  isDisplayingError
) {
  let objectFieldErrorClass = 'slim-select-error';
  let objectFieldErrorMessageClass = 'error-display';

  if (isDisplayingError) {
    slimSelectField.addClass(objectFieldErrorClass);
    slimSelectErrorMessageField.addClass(objectFieldErrorMessageClass);
  } else {
    slimSelectField.removeClass(objectFieldErrorClass);
    slimSelectErrorMessageField.removeClass(objectFieldErrorMessageClass);
  }
}
