'use strict';

/*global gettext*/
/*globals $:false */

function getEventHandler(textToDisplayOnEvent, eventType, onEvent) {
    return function(response) {
        if (textToDisplayOnEvent) {
            $.notify(gettext(textToDisplayOnEvent), {type: eventType});
        }

        if (onEvent) {
            onEvent(response);
        }
    };
}

function getSuccessHandler(successText, onSuccess) {
    return getEventHandler(successText, 'success', onSuccess);
}

function getFailureHandler(failureText, onFailure) {
    return getEventHandler(failureText, 'danger', onFailure);
}

function getRequest(uri, successText, failureText, onSuccess, onFailure) {
    $.ajax({
        type: 'GET',
        url: uri,
        success: getSuccessHandler(successText, onSuccess),
        error: getFailureHandler(failureText, onFailure)
    });
}

function postRequest(uri, payload, successText, failureText, onSuccess, onFailure) {
    $.ajax({
        type: 'POST',
        url: uri,
        data: payload,
        success: getSuccessHandler(successText, onSuccess),
        error: getFailureHandler(failureText, onFailure)
    });
}
