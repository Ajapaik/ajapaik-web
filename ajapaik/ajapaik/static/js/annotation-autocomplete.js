'use strict';

var SAVED_PERSON_GENDER_MALE = 1;
var SAVED_PERSON_GENDER_FEMALE = 0;

function getDefaultSelectedOption(defaultValue) {
  if (defaultValue) {
    let displayText = defaultValue.label;
    let optionValue = defaultValue.id;

    let option = new Option(displayText, optionValue);
    $(option).html(displayText);

    return option;
  }

  return $('<option data-placeholder="true"></option>');
}

function getPersonAutoComplete(
  isDisplayedOnOpen,
  customStyle,
  defaultValue,
  customLabelText
) {
  const specifyName = constants.translations.autocomplete.label.SPECIFY_NAME;
  const optional = constants.translations.common.OPTIONAL;
  const defaultText = specifyName + ' (' + optional + ')';

  const labelText = customLabelText || defaultText;

  const displayStyle = isDisplayedOnOpen ? '' : 'display: none';
  const styleToAdd = customStyle ? customStyle : '';

  const wrapper = $('<div>', {
    id: constants.elements.AUTOCOMPLETE_WRAPPER_ID,
    style: displayStyle + '; padding-top: 5px; width: 320px;',
  });

  const label = $('<label>', {
    for: constants.elements.SUBJECT_AUTOCOMPLETE_ID,
  });

  const select = $('<select>', {
    id: constants.elements.SUBJECT_AUTOCOMPLETE_ID,
    style: styleToAdd + 'padding-bottom: 5px;',
  });

  const placeholderOption = getDefaultSelectedOption(defaultValue);

  const addNewSubjectLinkWrapper = $('<div></div>');

  const addNewSubjectLink = getAddNewSubjectLink(
    constants.translations.autocomplete.label.ADD_NEW_PERSON
  );

  return wrapper
    .append(label.append(labelText))
    .append(select.append(placeholderOption))
    .append(addNewSubjectLinkWrapper.append(addNewSubjectLink));
}

function getNoPersonFoundResultText() {
  const wrapper = $('<span></span>');

  const nothingFoundText =
    constants.translations.autocomplete.subjectSearch.NO_RESULTS_TEXT;
  const newSubjectLink = getAddNewSubjectLink(
    constants.translations.autocomplete.subjectSearch.ADD_NEW_PERSON
  );

  return wrapper
    .append(nothingFoundText)
    .append($('<br>'))
    .append(newSubjectLink)
    .html();
}

function convertSavedPersonGenderToString(gender) {
  if (gender === SAVED_PERSON_GENDER_FEMALE) {
    return constants.fieldValues.genders.FEMALE;
  }

  if (gender === SAVED_PERSON_GENDER_MALE) {
    return constants.fieldValues.genders.MALE;
  }
}

function setGenderValueToReadOnlyIfGenderSetForExistingPerson(person) {
  if (person && person.data && person.data.gender) {
    $(
      '#' + constants.elements.SUBJECT_GENDER_SUGGESTION_COMPONENT_ID + ' *'
    ).addClass('ajp-button-disabled');
    $(
      '#' +
        constants.elements.SUBJECT_GENDER_SUGGESTION_COMPONENT_ID +
        ' [data-value=' +
        person.data.gender +
        ']'
    ).addClass('btn-outline-primary');
  } else {
    $(
      '#' + constants.elements.SUBJECT_GENDER_SUGGESTION_COMPONENT_ID + ' *'
    ).removeClass('ajp-button-disabled');
  }
}

function initializePersonAutocomplete(autocompleteId) {
  const noResultText = getNoPersonFoundResultText();
  const debouncedGetRequest = debounce(getRequest, 400);

  return new SlimSelect({
    select: '#' + autocompleteId,
    placeholder: constants.translations.autocomplete.subjectSearch.PLACEHOLDER,
    searchingText:
      constants.translations.autocomplete.subjectSearch.SEARCHING_TEXT + '...',
    searchPlaceholder:
      constants.translations.autocomplete.subjectSearch.SEARCH_PLACEHOLDER,
    searchText: noResultText,
    allowDeselect: true,
    onChange: function (person) {
      setGenderValueToReadOnlyIfGenderSetForExistingPerson(person);
    },
    ajax: function (search, callback) {
      if (search.length < 2) {
        callback(
          constants.translations.autocomplete.subjectSearch
            .MIN_CHARACTERS_NEEDED
        );
        return;
      }

      const uri =
        '/autocomplete/subject-album-autocomplete/?get-json=true&q=' +
        encodeURI(search);

      const onSuccess = function (response) {
        const data = [];

        const currentSelectedValue = $('#' + autocompleteId).val();
        const hasFoundData =
          response && response.results && response.results.length > 0;

        if (hasFoundData) {
          response.results.forEach(function (value) {
            if (!!value) {
              const nameAndGender = value.text.split(';');
              if (value.id !== currentSelectedValue) {
                data.push({
                  value: value.id,
                  text: nameAndGender[0],
                  data: {
                    gender: convertSavedPersonGenderToString(
                      parseInt(nameAndGender[1])
                    ),
                  },
                });
              }
            }
          });
        }

        callback(data);
      };

      debouncedGetRequest(uri, null, null, null, onSuccess);
    },
  });
}

function getFormattedSelectOption(option) {
  return (
    '<div>' +
    '<div class="hide-on-select">' +
    '<div style="float: left;">' +
    '<a href="' +
    sanitizeHTML(option.url) +
    '" data-type="wiki-link" target="_blank" style="padding-right: 5px;">' +
    '<span class="material-icons notranslate">open_in_new</span>' +
    '</a>' +
    '</div>' +
    '<div style="width: 92px;">' +
    '<span style="font-weight: bold">' +
    sanitizeHTML(option.label) +
    '</span>' +
    '<br/>' +
    '<span style="font-size: 8pt">' +
    ' (' +
    sanitizeHTML(option.description) +
    ')' +
    '</span>' +
    '</div>' +
    '</div>' +
    '<span class="show-on-select">' +
    sanitizeHTML(option.label) +
    '</span>' +
    '</div>'
  );
}

function initializeObjectAutocomplete(autocompleteId, isOpenOnView, onChange) {
  const noResultText =
    constants.translations.autocomplete.objectSearch.NO_RESULTS_FOUND;
  const findByLabel = debounce(WikiData.findByLabel, 400);

  const select = new SlimSelect({
    select: '#' + autocompleteId,
    valuesUseText: false,
    placeholder: constants.translations.autocomplete.objectSearch.PLACEHOLDER,
    searchingText:
      constants.translations.autocomplete.objectSearch.SEARCHING_TEXT + '...',
    searchPlaceholder:
      constants.translations.autocomplete.objectSearch.SEARCH_PLACEHOLDER,
    searchText: noResultText,
    onChange: onChange,
    ajax: function (search, callback) {
      if (search.length < 2) {
        callback(
          constants.translations.autocomplete.objectSearch.MIN_CHARACTERS_NEEDED
        );
        return;
      }

      const onSuccess = function (response) {
        const data = [];
        const currentSelectedValue = $('#' + autocompleteId).val();

        if (response) {
          response.forEach(function (result) {
            if (!currentSelectedValue || imageUrl.id !== currentSelectedValue) {
              data.push({
                innerHTML: getFormattedSelectOption(imageUrl),
                text: imageUrl.label,
                value: imageUrl.id,
              });
            }
          });
        }

        callback(data);

        $('[data-type="wiki-link"]').each(function () {
          $(this).click(function (event) {
            event.stopPropagation();
          });
        });
      };

      findByLabel(search, onSuccess);
    },
  });

  if (isOpenOnView) {
    select.open();
  }

  return select;
}
