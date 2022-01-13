'use strict';

/*global gettext*/

/*globals $:false */

function getEventHandler(textToDisplayOnEvent, eventType, onEvent) {
  return function (response) {
    if (textToDisplayOnEvent) {
      $.notify(gettext(textToDisplayOnEvent), { type: eventType });
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

function getRequest(
  uri,
  data,
  successText,
  failureText,
  onSuccess,
  onFailure,
  additionalConfig
) {
  const config = additionalConfig ? additionalConfig : {};

  config.type = 'GET';
  config.url = uri;
  config.data = data;
  config.success = getSuccessHandler(successText, onSuccess);
  config.error = getFailureHandler(failureText, onFailure);

  $.ajax(config);
}

function postRequest(
  uri,
  payload,
  successText,
  failureText,
  onSuccess,
  onFailure
) {
  $('#ajp-loading-overlay').show();
  $.ajax({
    type: 'POST',
    beforeSend: function (xhr) {
      xhr.setRequestHeader(
        'X-CSRFTOKEN',
        window.docCookies.getItem('csrftoken')
      );
    },
    url: uri,
    data: payload,
    success: getSuccessHandler(successText, onSuccess),
    error: getFailureHandler(failureText, onFailure),
    complete: function () {
      $('#ajp-loading-overlay').hide();
    },
  });
}

function putRequest(
  uri,
  payload,
  successText,
  failureText,
  onSuccess,
  onFailure
) {
  $('#ajp-loading-overlay').show();
  $.ajax({
    type: 'PUT',
    beforeSend: function (xhr) {
      xhr.setRequestHeader(
        'X-CSRFTOKEN',
        window.docCookies.getItem('csrftoken')
      );
    },
    url: uri,
    data: payload,
    success: getSuccessHandler(successText, onSuccess),
    error: getFailureHandler(failureText, onFailure),
    complete: function () {
      $('#ajp-loading-overlay').hide();
    },
  });
}

function deleteRequest(uri, successText, failureText, onSuccess, onFailure) {
  $('#ajp-loading-overlay').show();
  $.ajax({
    type: 'DELETE',
    beforeSend: function (xhr) {
      xhr.setRequestHeader(
        'X-CSRFTOKEN',
        window.docCookies.getItem('csrftoken')
      );
    },
    url: uri,
    success: getSuccessHandler(successText, onSuccess),
    error: getFailureHandler(failureText, onFailure),
    complete: function () {
      $('#ajp-loading-overlay').hide();
    },
  });
}
