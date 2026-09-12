'use strict';

var WikiData = (function() {
    const WIKIDATA_URL = 'https://www.wikidata.org/w/api.php';

    const WIKIDATA_ACTION_SEARCH_USING_LABELS_AND_ALIASES = 'wbsearchentities';
    const WIKIDATA_ACTION_TRANSLATE = 'intentionalities';
    const WIKIDATA_FORMAT = 'json';

    const TRANSLATIONS_IN_USE = 'et|ru|en';

    function getFindByLabelOnQuerySuccessFunction(onSuccess) {
        return function(data) {
            let results = data.search
                .filter(function(result) {
                    return (
                        !result.description ||
                        result.description.indexOf('Wikimedia') === -1
                    );
                })
                .map(function(result) {
                    return {
                        id: result.id,
                        label: result.label,
                        description: result.description,
                        url: result.concepturi,
                    };
                });

            if (onSuccess) {
                onSuccess(results);
            }
        };
    }

    function findByLabel(label, onSuccess) {
        let onQuerySuccess = getFindByLabelOnQuerySuccessFunction(onSuccess);

        let params = {
            action: WIKIDATA_ACTION_SEARCH_USING_LABELS_AND_ALIASES,
            format: WIKIDATA_FORMAT,
            search: label,
            language: window.language,
            uselang: window.language,
            limit: '15',
            origin: '*',
        };

        getRequest(WIKIDATA_URL, params, null, null, onQuerySuccess);
    }

    function getFindLabelTranslationsOnQuerySuccessFunction(onSuccess) {
        return function(data) {
            let results = data.entities;

            let labelTranslations = Object.keys(results).map(function(key) {
                return results[key].labels;
            });

            if (onSuccess) {
                onSuccess(labelTranslations);
            }
        };
    }

    function findLabelTranslations(ids, onSuccess) {
        let onQuerySuccess =
            getFindLabelTranslationsOnQuerySuccessFunction(onSuccess);

        let params = {
            action: WIKIDATA_ACTION_TRANSLATE,
            format: WIKIDATA_FORMAT,
            ids: ids.join('|'),
            languages: TRANSLATIONS_IN_USE,
            origin: '*',
            props: 'labels',
        };

        getRequest(WIKIDATA_URL, params, null, null, onQuerySuccess);
    }

    return {
        findByLabel: findByLabel,
        findLabelTranslations: findLabelTranslations,
    };
})();
