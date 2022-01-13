'use strict';

function getRemoveAnnotationFunction(annotationId, popoverId) {
  var onSuccess = function () {
    togglePopover(popoverId);
    refreshAnnotations();
  };

  return function () {
    removeFaceAnnotation(annotationId, onSuccess);
  };
}

function getModifySubmitFunction(annotationId, popoverId) {
  var onSuccess = function () {
    togglePopover(popoverId);
    refreshAnnotations();
  };

  return function (event) {
    event.preventDefault();

    var form = $(event.target);

    var newSubjectId = form
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

    var payload = {
      annotationId: annotationId,
      newSubjectId: newSubjectId,
      gender: gender,
      ageGroup: ageGroup,
    };

    editFaceAnnotation(payload, onSuccess);
  };
}

function getDefaultValue(annotation) {
  if (annotation.subjectId) {
    return {
      label: annotation.subjectName,
      id: annotation.subjectId,
    };
  }
}

function createDetectedFaceModifyPopoverContent(annotation, popoverId) {
  var defaultValue = getDefaultValue(annotation);
  var faceLabel = constants.translations.popover.labels.CHANGE_PERSON_NAME;
  var changeExistingFaceLabel = faceLabel + ':';

  var autocomplete = getPersonAutoComplete(
    true,
    'width: 320px;;',
    defaultValue,
    changeExistingFaceLabel
  );
  var buttons = [getSubmitButton('margin-top: 10px;')];

  buttons.push(
    getDeleteButton(getRemoveAnnotationFunction(annotation.id, popoverId))
  );

  buttons.push(getCancelButton(popoverId));

  var buttonGroup = getButtonGroup(buttons);

  var form = $('<form/>', {
    id: 'modify-detected-object-annotation',
  }).on('submit', getModifySubmitFunction(annotation.id, popoverId));

  let ageGroupSuggestionId =
    constants.elements.SUBJECT_AGE_GROUP_SUGGESTION_COMPONENT_ID;
  let ageGroupSuggestionComponent = $('<div>', {
    id: ageGroupSuggestionId,
    class: 'd-block text-center',
  });

  let ageGroupSuggestionComponentLabel = $('<div>', {
    text: gettext('Change age group'),
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
    text: gettext('Change gender'),
    class: 'my-2',
  });

  Object.keys(constants.fieldValues.genders).forEach((x) =>
    genderSuggestionComponent.append(
      $('<button>', {
        class: 'mx-1 btn btn-light suggestion-button human-' + x.toLowerCase(),
        type: 'button',
        text: gettext(x[0].toUpperCase() + x.slice(1).toLowerCase()),
        click: function (event) {
          if (!$(event.target).hasClass('ajp-button-disabled')) {
            $('#' + genderSuggestionId + ' > button')
              .removeClass('btn-outline-primary')
              .removeClass('btn-outline-dark');
            $(event.target).addClass('btn-outline-primary');
          }
        },
      }).attr('data-value', x)
    )
  );

  form
    .append(autocomplete)
    .append(ageGroupSuggestionComponentLabel)
    .append(ageGroupSuggestionComponent)
    .append(genderSuggestionComponentLabel)
    .append(genderSuggestionComponent);

  return form.append(buttonGroup);
}

function createFaceAnnotationEditRectangle(
  popoverId,
  annotation,
  configuration
) {
  var hasInitializedSelects = false;

  var onAnnotationRectangleShow = function () {
    if (hasInitializedSelects) {
      return;
    }
    setTimeout(function () {
      if (annotation && annotation.gender) {
        let selectedGender = annotation.gender;

        if (
          annotation.subjectId &&
          annotation.gender !== constants.fieldValues.common.UNSURE
        ) {
          $(
            '#' +
              constants.elements.SUBJECT_GENDER_SUGGESTION_COMPONENT_ID +
              ' *'
          ).addClass('ajp-button-disabled');
        }
        $(
          '#' +
            constants.elements.SUBJECT_GENDER_SUGGESTION_COMPONENT_ID +
            ' [data-value=' +
            selectedGender +
            ']'
        ).addClass('btn-outline-primary');
      }

      if (annotation && annotation.age) {
        let selectedAgeGroup = annotation.age;

        $(
          '#' +
            constants.elements.SUBJECT_AGE_GROUP_SUGGESTION_COMPONENT_ID +
            ' [data-value=' +
            selectedAgeGroup +
            ']'
        ).addClass('btn-outline-primary');
      }
      initializePersonAutocomplete(constants.elements.SUBJECT_AUTOCOMPLETE_ID);

      hasInitializedSelects = true;
    }, 100);
  };

  var popoverTitle = constants.translations.popover.titles.EDIT_FACE_ANNOTATION;

  var popoverContent = createDetectedFaceModifyPopoverContent(
    annotation,
    popoverId
  );

  return createAnnotationRectangleWithPopover(
    popoverId,
    popoverTitle,
    popoverContent,
    configuration,
    onAnnotationRectangleShow
  );
}
