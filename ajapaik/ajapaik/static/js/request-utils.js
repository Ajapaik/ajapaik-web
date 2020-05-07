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

function getRequest(uri, data, successText, failureText, onSuccess, onFailure, additionalConfig) {
    var config = additionalConfig ? additionalConfig : {};

    config.type = 'GET';
    config.url = uri;
    config.data = data;
    config.success = getSuccessHandler(successText, onSuccess);
    config.error = getFailureHandler(failureText, onFailure);

    $.ajax(config);
}

function postRequest(uri, payload, successText, failureText, onSuccess, onFailure) {
    $.ajax({
        type: 'POST',
        beforeSend : function(xhr) {
            xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
        },
        url: uri,
        data: payload,
        success: getSuccessHandler(successText, onSuccess),
        error: getFailureHandler(failureText, onFailure)
    });
}

function putRequest(uri, payload, successText, failureText, onSuccess, onFailure) {
    $.ajax({
        type: 'PUT',
        beforeSend : function(xhr) {
            xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
        },
        url: uri,
        data: payload,
        success: getSuccessHandler(successText, onSuccess),
        error: getFailureHandler(failureText, onFailure)
    });
}

function deleteRequest(uri, successText, failureText, onSuccess, onFailure) {
    $.ajax({
        type: 'DELETE',
        beforeSend : function(xhr) {
            xhr.setRequestHeader("X-CSRFTOKEN", window.docCookies.getItem('csrftoken'));
        },
        url: uri,
        success: getSuccessHandler(successText, onSuccess),
        error: getFailureHandler(failureText, onFailure)
    });
}
