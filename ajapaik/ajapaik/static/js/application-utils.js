'use strict';

function debounce(func, delay) {
  let inDebounce;

  return function () {
    const context = this;
    const args = arguments;
    clearTimeout(inDebounce);

    inDebounce = setTimeout(function () {
      func.apply(context, args);
    }, delay);
  };
}

var sanitizeHTML = function (str) {
  const temp = document.createElement('div');
  temp.textContent = str;
  return temp.innerHTML;
};

function disableHotkeys() {
  window.hotkeysActive = false;
}

function enableHotkeys() {
  window.hotkeysActive = true;
}

function areHotkeysEnabled() {
  return window.hotkeysActive;
}

function getLanguageSpecificTranslation(unparsedTranslations) {
  const parsedTranslations = JSON.parse(unparsedTranslations);
  const languageSpecificTranslation = parsedTranslations[window.language];
  return languageSpecificTranslation || parsedTranslations.en;
}

function capitalizeFirstLetter(word) {
  const lowerCase = word.toLowerCase();
  return lowerCase.charAt(0).toUpperCase() + lowerCase.slice(1);
}
