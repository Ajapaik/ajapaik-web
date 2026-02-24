import json

import requests

WIKIDATA_URL = 'https://www.wikidata.org/w/api.php'

WIKIDATA_ACTION_TRANSLATE = 'wbgetentities'
WIKIDATA_FORMAT = 'json'

TRANSLATIONS_IN_USE = 'et|ru|en'
FALLBACK_TRANSLATION = 'en'


def get_label_translation(label_id):
    global WIKIDATA_URL, WIKIDATA_FORMAT, WIKIDATA_ACTION_TRANSLATE, FALLBACK_TRANSLATION

    params = {
        'action': WIKIDATA_ACTION_TRANSLATE,
        'format': WIKIDATA_FORMAT,
        'ids': label_id,
        'languages': TRANSLATIONS_IN_USE,
        'origin': '*',
        'props': 'labels'
    }

    result = requests.get(url=WIKIDATA_URL, params=params)

    translations = result.json()['entities'][label_id]['labels']

    def get_translation(language):
        has_language_translation = language in translations

        if has_language_translation:
            return translations[language]['value']
        elif FALLBACK_TRANSLATION in translations:
            return translations[FALLBACK_TRANSLATION]['value']
        elif 'et' in translations:
            return translations['et']['value']
        elif 'ru' in translations:
            return translations['ru']['value']

    return json.dumps({
        'en': get_translation('en'),
        'et': get_translation('et'),
        'ru': get_translation('ru')
    }).__str__()
