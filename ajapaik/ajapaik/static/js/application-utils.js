'use strict';

function debounce(func, delay) {
  var inDebounce;

  return function() {
    var context = this;
    var args = arguments;
    clearTimeout(inDebounce);

    inDebounce = setTimeout(function() {
        func.apply(context, args);
        }, delay);
  };
}

var sanitizeHTML = function (str) {
	var temp = document.createElement('div');
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
    var parsedTranslations = JSON.parse(unparsedTranslations);
    var languageSpecificTranslation = parsedTranslations[window.language];
    return languageSpecificTranslation || parsedTranslations.en;
}

function capitalizeFirstLetter(word) {
    var lowerCase = word.toLowerCase();
    return lowerCase.charAt(0).toUpperCase() + lowerCase.slice(1);
}

function getDefaultBooleanCheckboxValue(val) {
    return isBoolean(val) ? val : true;
}

function isBoolean(val) {
    return typeof val === typeof true;
}
