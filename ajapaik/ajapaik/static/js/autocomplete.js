'use strict';

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

function initializePersonAutocomplete(autocompleteId) {
    var noResultText = getNoPersonFoundResultText();
    var debouncedGetRequest = debounce(getRequest, 400);

    return new SlimSelect({
        select: '#' + autocompleteId,
        placeholder: constants.translations.autocomplete.subjectSearch.PLACEHOLDER,
        searchingText: constants.translations.autocomplete.subjectSearch.SEARCHING_TEXT + '...',
        searchPlaceholder: constants.translations.autocomplete.subjectSearch.SEARCH_PLACEHOLDER,
        searchText: noResultText,
        allowDeselect: true,
        ajax: function (search, callback) {

          if (search.length < 2) {
              callback(constants.translations.autocomplete.subjectSearch.MIN_CHARACTERS_NEEDED);
              return;
          }

          var uri = '/autocomplete/SubjectAlbumAutocomplete/?q=' + encodeURI(search);

          var onSuccess = function(response) {
              var data = [];

              response
                  .replace(new RegExp('</span>', 'g'), ',')
                  .replace(new RegExp('<span data-value="', 'g'), '')
                  .replace(new RegExp('">', 'g'), '-')
                  .split(',')
                  .forEach(function(value) {
                      if (!!value) {
                           var parts = value.split('-');

                          data.push({
                              value: parts[0],
                              text: parts[1]
                          });
                      }
                  });

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
            '<span style="font-weight: bold">' +
                sanitizeHTML(option.label) +
            '</span>' +
            '<br/>' +
            '<span style="font-size: 8pt">' +
                ' (' + sanitizeHTML(option.description) + ')' +
            '</span>' +
        '</div>'
    );
}

function initializeObjectAutocomplete(autocompleteId, isOpenOnView) {
    var noResultText = constants.translations.autocomplete.objectSearch.NO_RESULTS_FOUND;
    var findByLabel = debounce(WikiData.findByLabel, 400);

    var select = new SlimSelect({
        select: '#' + autocompleteId,
        valuesUseText: true,
        placeholder: constants.translations.autocomplete.objectSearch.PLACEHOLDER,
        searchingText: constants.translations.autocomplete.objectSearch.SEARCHING_TEXT + '...',
        searchPlaceholder: constants.translations.autocomplete.objectSearch.SEARCH_PLACEHOLDER,
        searchText: noResultText,
        ajax: function (search, callback) {

          if (search.length < 2) {
              callback(constants.translations.autocomplete.objectSearch.MIN_CHARACTERS_NEEDED);
              return;
          }

          var onSuccess = function(response) {
              var data = [];

              if (response) {
                  response.forEach(function(result) {
                      data.push({
                          innerHTML: getFormattedSelectOption(result),
                          text: result.label,
                          value: result.id
                      });
                  });
              }

              callback(data);
          };

          findByLabel(search, onSuccess);
        }
    });

    if (isOpenOnView) {
        select.open();
    }

    return select;
}
