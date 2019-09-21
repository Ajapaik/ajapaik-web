'use strict';

var WikiData = (function() {
    var WIKIDATA_URL = 'https://www.wikidata.org/w/api.php';

    var WIKI_DATA_ACTION_SEARCH_USING_LABELS_AND_ALIASES = 'wbsearchentities';
    var WIKI_DATA_ACTION_TRANSLATE = 'wbgetentities';
    var WIKI_DATA_FORMAT = 'json';

    var TRANSLATIONS_IN_USE = 'et|ru|en';

    function getFindByLabelOnQuerySuccessFunction(onSuccess) {
        return function (data) {
            var results = data.search
                .filter(function(result) {
                    return !result.description || result.description.indexOf('Wikimedia') === -1;
                })
                .map(function(result) {
                    return {
                        id: result.id,
                        label: result.label,
                        description: result.description
                    };
                });

            if (onSuccess) {
                onSuccess(results);
            }
        };
    }

    var findByLabel = function(label, onSuccess) {
        var onQuerySuccess = getFindByLabelOnQuerySuccessFunction(onSuccess);

        var params = {
            action: WIKI_DATA_ACTION_SEARCH_USING_LABELS_AND_ALIASES,
            format: WIKI_DATA_FORMAT,
            search: label,
            language: window.language,
            uselang: window.language,
            limit: '15',
            origin: '*'
        };

        getRequest(WIKIDATA_URL, params, null, null, onQuerySuccess);
    };

    function getFindLabelTranslationsOnQuerySuccessFunction(onSuccess) {
        return function (data) {
            var results = data.entities;

            var labelTranslations = Object.keys(results)
                .map(function(key) {
                    return results[key].labels;
                });

            if (onSuccess) {
                onSuccess(labelTranslations);
            }
        };
    }

    var findLabelTranslations = function (ids, onSuccess) {
        var onQuerySuccess = getFindLabelTranslationsOnQuerySuccessFunction(onSuccess);

        var params = {
            action: WIKI_DATA_ACTION_TRANSLATE,
            format: WIKI_DATA_FORMAT,
            ids: ids.join('|'),
            languages: TRANSLATIONS_IN_USE,
            origin: '*',
            props: 'labels'
        };

        getRequest(WIKIDATA_URL, params, null, null, onQuerySuccess);
    };

    return {
        findByLabel: findByLabel,
        findLabelTranslations: findLabelTranslations
    };
})();
