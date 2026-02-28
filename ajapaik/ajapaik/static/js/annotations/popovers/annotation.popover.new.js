'use strict';

function toggleNewObjectFieldError(isDisplayingError) {
  var objectField = $('#' + constants.elements.SELECT_OBJECT_CLASS_WRAPPER_ID);
  var objectFieldError = $(
    '#' +
      constants.elements.NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID +
      ' .invalid-feedback'
  );
  toggleSlimSelectError(objectField, objectFieldError, isDisplayingError);
}

function getRectangleSubmitFunction(popoverId) {
  return function (event) {
    event.preventDefault();

    var form = $(event.target);

    var isObjectSelected = form.data('selected') === 'object';

    var selectedObjectId = form
      .find('#' + constants.elements.OBJECT_CLASS_SELECT_ID)
      .val();
    var personId = form
      .find('#' + constants.elements.SUBJECT_AUTOCOMPLETE_ID)
      .val();

    let gender = constants.fieldValues.common.UNSURE;
    let ageGroup = constants.fieldValues.common.UNSURE;

    let genderSuggestionId =
      '#' + constants.elements.SUBJECT_GENDER_SUGGESTION_COMPONENT_ID;
    let ageGroupSuggestionId =
      '#' + constants.elements.SUBJECT_AGE_GROUP_SUGGESTION_COMPONENT_ID;

    let pressedGenderButton = form.find(
      genderSuggestionId + ' button.btn-outline-primary'
    );
    let pressedAgeGroupButton = form.find(
      ageGroupSuggestionId + ' button.btn-outline-primary'
    );

    if (pressedGenderButton.length == 1) {
      gender = pressedGenderButton[0].dataset.value;
    }

    if (pressedAgeGroupButton.length == 1) {
      ageGroup = pressedAgeGroupButton[0].dataset.value;
    }

    if (isObjectSelected) {
      toggleNewObjectFieldError(!selectedObjectId);

      if (!selectedObjectId) {
        return;
      }
    }

    var scaledRectangle = getAnnotationScaledForOriginalImageSize(
      popoverId,
      ImageAreaSelector.getImageAreaDimensions()
    );
    togglePopover(popoverId);

    var payload = {
      isSavingObject: isObjectSelected,
      wikiDataLabelId: isObjectSelected ? selectedObjectId : null,
      subjectId: !isObjectSelected ? personId : null,
      photoId: scaledRectangle.photoId,
      gender: gender,
      ageGroup: ageGroup,
      x1: scaledRectangle.x1,
      x2: scaledRectangle.x2,
      y1: scaledRectangle.y1,
      y2: scaledRectangle.y2,
    };

    addNewDetectionAnnotation(payload, function () {
      refreshAnnotations();
      if (window.refreshActivityLog) {
        window.refreshActivityLog('all');
      }
    });
  };
}

function toggleFaceDetection() {
  $('#' + constants.elements.NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID).hide();
  $('#' + constants.elements.ADD_NEW_FACE_FIELDS_WRAPPER_ID).show();
  $('#' + constants.elements.NEW_ANNOTATION_FORM_ID).data('selected', 'face');
}

function toggleObjectDetection() {
  $('#' + constants.elements.NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID).show();
  $('#' + constants.elements.ADD_NEW_FACE_FIELDS_WRAPPER_ID).hide();
  $('#' + constants.elements.NEW_ANNOTATION_FORM_ID).data('selected', 'object');

  document
    .getElementById(constants.elements.OBJECT_CLASS_SELECT_ID)
    .slim.open();
}

function createObjectAssigningPopoverContent(popoverId) {
  var faceLabel = constants.translations.popover.labels.FACE_ANNOTATION;
  var objectLabel = constants.translations.popover.labels.OBJECT_ANNOTATION;

  var objectAutocomplete = getObjectsSelect();
  var controlButtons = getSubmitAndCancelButtons(popoverId, true);
  var detectionTypeToggle = getToggleButton(
    faceLabel,
    objectLabel,
    toggleFaceDetection,
    toggleObjectDetection
  );
  var autocomplete = getPersonAutoComplete(true);

  var formWrapper = $('<div></div>');

  var form = $('<form>', {
    id: constants.elements.NEW_ANNOTATION_FORM_ID,
    submit: getRectangleSubmitFunction(popoverId),
    'data-selected': 'face',
  });

  var wrapper = $('<div style="padding-top: 5px;"></div>');
  var subjectFieldsWrapper = $('<div>', {
    id: constants.elements.ADD_NEW_FACE_FIELDS_WRAPPER_ID,
  });
  var objectSelectWrapper = $('<div>', {
    id: constants.elements.NEW_OBJECT_SELECT_FIELDS_GROUP_WRAPPER_ID,
    style: 'padding-bottom: 15px; display: none;',
  });
  var errorMessage = $('<div class="invalid-feedback">').append(
    constants.translations.errors.OBJECT_REQUIRED
  );

  let ageGroupSuggestionId =
    constants.elements.SUBJECT_AGE_GROUP_SUGGESTION_COMPONENT_ID;
  let ageGroupSuggestionComponent = $('<div>', {
    id: ageGroupSuggestionId,
    class: 'd-block text-center',
  });

  let ageGroupSuggestionComponentLabel = $('<div>', {
    text: gettext('Select age group (optional)'),
    class: 'my-2',
  });

  Object.keys(constants.fieldValues.ageGroups).forEach((x) =>
    ageGroupSuggestionComponent.append(
      $('<button>', {
        class: 'mx-1 btn btn-light suggestion-button human-' + x.toLowerCase(),
        type: 'button',
        text: gettext(x[0].toUpperCase() + x.slice(1).toLowerCase()),
        click: function (event) {
          $('#' + ageGroupSuggestionId + ' > button')
            .removeClass('btn-outline-primary')
            .removeClass('btn-outline-dark');
          $(event.target).addClass('btn-outline-primary');
        },
      }).attr('data-value', x)
    )
  );

  let genderSuggestionId =
    constants.elements.SUBJECT_GENDER_SUGGESTION_COMPONENT_ID;
  let genderSuggestionComponent = $('<div>', {
    id: genderSuggestionId,
    class: 'd-block text-center',
  });

  let genderSuggestionComponentLabel = $('<div>', {
    text: gettext('Select gender (optional)'),
    class: 'my-2',
  });

  Object.keys(constants.fieldValues.genders).forEach((x) =>
    genderSuggestionComponent.append(
      $('<button>', {
        class: 'mx-1 btn btn-light suggestion-button human-' + x.toLowerCase(),
        type: 'button',
        text: gettext(x[0].toUpperCase() + x.slice(1).toLowerCase()),
        click: function (event) {
          if (!$(event.target).hasClass('ajp-button-disabled ')) {
            $('#' + genderSuggestionId + ' > button')
              .removeClass('btn-outline-primary')
              .removeClass('btn-outline-dark');
            $(event.target).addClass('btn-outline-primary');
          }
        },
      }).attr('data-value', x)
    )
  );

  return formWrapper.append(
    form
      .append(
        wrapper
          .append(detectionTypeToggle)
          .append(
            subjectFieldsWrapper
              .append(autocomplete)
              .append(ageGroupSuggestionComponentLabel)
              .append(ageGroupSuggestionComponent)
              .append(genderSuggestionComponentLabel)
              .append(genderSuggestionComponent)
          )
      )
      .append(
        objectSelectWrapper.append(objectAutocomplete).append(errorMessage)
      )
      .append(controlButtons)
  );
}

function validateRequiredNewObjectFieldOrFocusSubmit(selectedOption) {
  toggleNewObjectFieldError(!selectedOption.value);

  if (selectedOption.value) {
    $(
      '#' + constants.elements.NEW_ANNOTATION_FORM_ID + ' [type="submit"]'
    ).focus();
  }
}

function createNewAnnotation(popoverId, configuration) {
  var hasInitializedSelects = false;

  var onAnnotationRectangleShow = function () {
    if (!hasInitializedSelects) {
      setTimeout(function () {
        initializePersonAutocomplete(
          constants.elements.SUBJECT_AUTOCOMPLETE_ID
        );

        initializeObjectAutocomplete(
          constants.elements.OBJECT_CLASS_SELECT_ID,
          true,
          validateRequiredNewObjectFieldOrFocusSubmit
        );

        hasInitializedSelects = true;
      }, 100);
    }
  };

  var popoverTitle = constants.translations.popover.titles.NEW_ANNOTATION + '?';
  var popoverContent = createObjectAssigningPopoverContent(popoverId);

  configuration.annotation = {};
  configuration.isAnnotationAreaModifiable = true;

  return createAnnotationRectangleWithPopover(
    popoverId,
    popoverTitle,
    popoverContent,
    configuration,
    onAnnotationRectangleShow,
    'dashed'
  );
}
