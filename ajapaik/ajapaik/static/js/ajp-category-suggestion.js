function submitCategorySuggestion(photoIds, isMultiSelect) {
  sendCategorySuggestionToAI(photoIds, scene, viewpointElevation)
  $('#ajp-loading-overlay').show();
  return fetch(photoSceneUrl, {
    method: 'POST',
    beforeSend: function (xhr) {
      xhr.setRequestHeader(
        'X-CSRFTOKEN',
        window.docCookies.getItem('csrftoken')
      );
    },
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      photoIds,
      scene,
      viewpointElevation,
    }),
  })
    .then(window.handleErrors)
    .then(function (data) {
      if (!isMultiSelect) {
        const categorizeSceneButton = $('#ajp-categorize-scene');
        categorizeSceneButton.not(this).popover('hide');
        categorizeSceneButton.popover('dispose');
        updatePhotoSuggestions();
      } else {
        $('#ajp-photo-selection-categorize-scenes-button')
          .not(this)
          .popover('hide');
      }
      $.notify(data.message, { type: 'success' });
      $('#ajp-loading-overlay').hide();
    })
    .catch((error) => {
      $('#ajp-loading-overlay').hide();
      $.notify(error, { type: 'danger' });
    });
}

function clickViewpointElevationCategoryButton(buttonId) {
  $('#send-suggestion-button').prop('disabled', false);

  let otherButtonIds = [];

  if (buttonId === 'aerial-button') {
    viewpointElevation = 'Aerial';
  } else if (buttonId === 'raised-button') {
    viewpointElevation = 'Raised';
  } else if (buttonId === 'ground-button') {
    viewpointElevation = 'Ground';
  }

  if (viewpointElevation === 'Aerial') {
    otherButtonIds = ['#ground-button', '#raised-button'];
  } else if (viewpointElevation === 'Raised') {
    otherButtonIds = ['#ground-button', '#aerial-button'];
  } else if (viewpointElevation === 'Ground') {
    otherButtonIds = ['#raised-button', '#aerial-button'];
  }

  otherButtonIds.forEach(function (id) {
    if (!$(id).hasClass('btn-outline-primary')) {
      $(id).addClass('btn-light');
    }
    if ($(id).hasClass('btn-outline-primary')) {
      $(id).removeClass('btn-outline-primary');
    }
    if ($(id).hasClass('btn-outline-dark')) {
      $(id).removeClass('btn-outline-dark');
    }
  });

  $('#' + buttonId).addClass('btn-outline-primary');
  $('#' + buttonId).removeClass('btn-outline-dark');
  $('#' + buttonId).removeClass('btn-light');
}

function clickSceneCategoryButton(buttonId) {
  $('#send-suggestion-button').prop('disabled', false);

  scene = buttonId === 'interior-button' ? 'Interior' : 'Exterior';
  let otherButtonId =
    scene === 'Interior' ? '#exterior-button' : '#interior-button';

  if (!$(otherButtonId).hasClass('btn-light')) {
    $(otherButtonId).addClass('btn-light');
  }

  if ($(otherButtonId).hasClass('btn-outline-primary')) {
    $(otherButtonId).removeClass('btn-outline-primary');
  }

  if ($(otherButtonId).hasClass('btn-outline-dark')) {
    $(otherButtonId).removeClass('btn-outline-dark');
  }

  $('#' + buttonId).addClass('btn-outline-primary');
  $('#' + buttonId).removeClass('btn-outline-dark');
  $('#' + buttonId).removeClass('btn-light');
}

function getImageCategory(photoId, callback) {
  let onSuccess = function (response) {
    callback(determinePictureCategory(response.data));
  };
  getRequest(
      '/object-categorization/get-latest-category/' + photoId + '/',
      null,
      null,
      constants.translations.queries.GET_CATEGORY_FAILED,
      onSuccess
  );
}

function determinePictureCategory(responseData) {
  let responseDict = {};
  for (let data of responseData) {
    let fields = data["fields"];
    if ("scene" in fields) {
      if (fields["scene"] === 0) {
        responseDict["scene"] = "interior";
      } else {
        responseDict["scene"] = "exterior";
      }
    }
    if ("viewpoint_elevation" in fields) {
      if (fields["viewpoint_elevation"] === 0) {
        responseDict["viewpoint_elevation"] = "ground";
      } else if (fields["viewpoint_elevation"] === 1) {
        responseDict["viewpoint_elevation"] = "raised";
      } else if (fields["viewpoint_elevation"] === 2) {
        responseDict["viewpoint_elevation"] = "areal";
      }
    }
  }
  return responseDict;
}

function sendCategorySuggestionToAI(photoIds, scene, viewpointElevation) {
  let sceneVerdict = scene.toLowerCase();
  let viewpointElevationVerdict = viewpointElevation.toLowerCase();

  let payload = {
    "photo_id": photoIds[0]
  };

  if (sceneVerdict === "interior") {
    payload["scene_to_alternate"] = 0
  }
  if (sceneVerdict === "exterior") {
    payload["scene_to_alternate"] = 1
  }
  if (viewpointElevationVerdict === "ground") {
    payload["viewpoint_elevation_to_alternate"] = 0
  }
  if (viewpointElevationVerdict === "raised") {
    payload["viewpoint_elevation_to_alternate"] = 1
  }
  if (viewpointElevationVerdict === "raised") {
    payload["viewpoint_elevation_to_alternate"] = 2
  }

  postRequest(
      '/object-categorization/confirm-latest-category',
      payload,
      constants.translations.queries.POST_CATEGORY_CONFIRMATION_SUCCESS,
      constants.translations.queries.POST_CATEGORY_CONFIRMATION_FAILED,
      function () {
      }
  );
}
