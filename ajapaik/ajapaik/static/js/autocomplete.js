'use strict';

var SAVED_PERSON_GENDER_MALE = 1;
var SAVED_PERSON_GENDER_FEMALE = 0;

function getDefaultSelectedOption(defaultValue) {
    if (defaultValue) {
        var displayText = defaultValue.label;
        var optionValue = defaultValue.id;

        var o = new Option(displayText, optionValue);
        $(o).html(displayText);

        return o;
    }

    return $('<option data-placeholder="true"></option>');
}

function getPersonAutoComplete(isDisplayedOnOpen, customStyle, defaultValue, customLabelText) {
    var addNewSubjectText = constants.translations.autocomplete.label.ADD_NEW_PERSON;

    var specifyName = constants.translations.autocomplete.label.SPECIFY_NAME;
    var optional = constants.translations.common.OPTIONAL;
    var defaultText = specifyName + ' (' + optional + ')';

    var labelText = customLabelText || defaultText;

    var displayStyle = isDisplayedOnOpen ? '' : 'display: none';
    var styleToAdd = customStyle ? customStyle : '';

    var wrapper = $('<div>', {
        id: constants.elements.AUTOCOMPLETE_WRAPPER_ID,
        style: displayStyle + '; padding-top: 5px; width: 180px;'
    });

    var label = $('<label>', {
        for: constants.elements.SUBJECT_AUTOCOMPLETE_ID
    });

    var select = $('<select>', {
        id: constants.elements.SUBJECT_AUTOCOMPLETE_ID,
        style: styleToAdd + 'padding-bottom: 5px;'
    });

    var placeholderOption = getDefaultSelectedOption(defaultValue);

    var addNewSubjectLinkWrapper = $('<div></div>');

    var addNewSubjectLink = getAddNewSubjectLink(addNewSubjectText);

    return wrapper
        .append(label
            .append(labelText)
        )
        .append(select
            .append(placeholderOption)
        )
        .append(addNewSubjectLinkWrapper
            .append(addNewSubjectLink)
        );
}

function getNoPersonFoundResultText() {
    var wrapper = $('<span></span>');

    var nothingFoundText = constants.translations.autocomplete.subjectSearch.NO_RESULTS_TEXT;
    var newSubjectLink = getAddNewSubjectLink(constants.translations.autocomplete.subjectSearch.ADD_NEW_PERSON);

    return wrapper
        .append(nothingFoundText)
        .append(newSubjectLink)
        .html();
}

function convertSavedPersonGenderToString(gender) {
    if (gender === SAVED_PERSON_GENDER_FEMALE) {
        return constants.fieldValues.FEMALE;
    }

    if (gender === SAVED_PERSON_GENDER_MALE) {
        return constants.fieldValues.MALE;
    }
}

function setGenderValueToReadOnlyIfGenderSetForExistingPerson(person, genderSelect) {
    if (genderSelect && person && person.data && person.data.gender) {
        genderSelect.set(person.data.gender);
        genderSelect.disable();
    } else {
        genderSelect.enable();
    }
}

function initializePersonAutocomplete(autocompleteId, genderSelect) {
    var noResultText = getNoPersonFoundResultText();
    var debouncedGetRequest = debounce(getRequest, 400);

    return new SlimSelect({
        select: '#' + autocompleteId,
        placeholder: constants.translations.autocomplete.subjectSearch.PLACEHOLDER,
        searchingText: constants.translations.autocomplete.subjectSearch.SEARCHING_TEXT + '...',
        searchPlaceholder: constants.translations.autocomplete.subjectSearch.SEARCH_PLACEHOLDER,
        searchText: noResultText,
        allowDeselect: true,
        onChange: function(person) {
            setGenderValueToReadOnlyIfGenderSetForExistingPerson(person, genderSelect);
        },
        ajax: function (search, callback) {

          if (search.length < 2) {
              callback(constants.translations.autocomplete.subjectSearch.MIN_CHARACTERS_NEEDED);
              return;
          }

          var uri = '/autocomplete/SubjectAlbumAutocomplete/?get-json=true&q=' + encodeURI(search);

          var onSuccess = function(response) {
              var data = [];

              var currentSelectedValue = $('#' + autocompleteId).val();
              var hasFoundData = response.indexOf('data-value') !== -1;

              if (hasFoundData) {
                  response
                      .replace(new RegExp('&quot;', 'g'), '"')
                      .replace(new RegExp('</span>', 'g'), ';')
                      .replace(new RegExp('<span data-value="', 'g'), '')
                      .replace(new RegExp('">', 'g'), '-')
                      .split(';')
                      .forEach(function(value) {
                          if (!!value) {
                              var parts = value.split('-');
                              var personId = parts[0];

                              var personData = JSON.parse(parts[1]);
                              var personName = personData.name;
                              var personGender = convertSavedPersonGenderToString(personData.gender);

                              if (personId !== currentSelectedValue) {
                                  data.push({
                                      value: personId,
                                      text: personName,
                                      data: {
                                          gender: personGender
                                      }
                                  });
                              }
                          }
                      });
              }

              callback(data);
          };

          debouncedGetRequest(
              uri,
              null,
              null,
              null,
              onSuccess
          );
        }
    });
}

function getFormattedSelectOption(option) {
    return (
        '<div>' +
            '<div class="hide-on-select">' +
                '<div style="float: left;">' +
                    '<a href="' + sanitizeHTML(option.url) + '" data-type="wiki-link" target="_blank" style="padding-right: 5px;">' +
                        '<i class="material-icons notranslate">open_in_new</i>' +
                    '</a>' +
                '</div>' +
                '<div style="width: 92px;">' +
                    '<span style="font-weight: bold">' +
                        sanitizeHTML(option.label) +
                    '</span>' +
                    '<br/>' +
                    '<span style="font-size: 8pt">' +
                        ' (' + sanitizeHTML(option.description) + ')' +
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
    var noResultText = constants.translations.autocomplete.objectSearch.NO_RESULTS_FOUND;
    var findByLabel = debounce(WikiData.findByLabel, 400);

    var select = new SlimSelect({
        select: '#' + autocompleteId,
        valuesUseText: false,
        placeholder: constants.translations.autocomplete.objectSearch.PLACEHOLDER,
        searchingText: constants.translations.autocomplete.objectSearch.SEARCHING_TEXT + '...',
        searchPlaceholder: constants.translations.autocomplete.objectSearch.SEARCH_PLACEHOLDER,
        searchText: noResultText,
        onChange: onChange,
        ajax: function (search, callback) {

          if (search.length < 2) {
              callback(constants.translations.autocomplete.objectSearch.MIN_CHARACTERS_NEEDED);
              return;
          }

          var onSuccess = function(response) {
              var data = [];
              var currentSelectedValue = $('#' + autocompleteId).val();

              if (response) {
                  response.forEach(function(result) {
                      if (!currentSelectedValue || result.id !== currentSelectedValue) {
                          data.push({
                              innerHTML: getFormattedSelectOption(result),
                              text: result.label,
                              value: result.id
                          });
                      }
                  });
              }

              callback(data);

              $('[data-type="wiki-link"]').each(function() {
                  var el = $(this);

                  el.click(function(event) {
                      event.stopPropagation();
                  });

              });
          };

          findByLabel(search, onSuccess);
        }
    });

    if (isOpenOnView) {
        select.open();
    }

    return select;
}
