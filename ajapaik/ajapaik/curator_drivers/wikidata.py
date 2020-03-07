import json

import requests

WIKI_DATA_URL = 'https://www.wikidata.org/w/api.php'

WIKI_DATA_ACTION_TRANSLATE = 'wbgetentities'
WIKI_DATA_FORMAT = 'json'

TRANSLATIONS_IN_USE = 'et|ru|en'
FALLBACK_TRANSLATION = 'en'


def get_label_translation(label_id):
    global WIKI_DATA_URL, WIKI_DATA_FORMAT, WIKI_DATA_ACTION_TRANSLATE, FALLBACK_TRANSLATION

    params = {
        'action': WIKI_DATA_ACTION_TRANSLATE,
        'format': WIKI_DATA_FORMAT,
        'ids': label_id,
        'languages': TRANSLATIONS_IN_USE,
        'origin': '*',
        'props': 'labels'
    }

    result = requests.get(url=WIKI_DATA_URL, params=params)

    translations = result.json()['entities'][label_id]['labels']

    def get_translation(language):
        has_language_translation = language in translations
        fallback_translation = translations[FALLBACK_TRANSLATION]['value']
        return translations[language]['value'] if has_language_translation else fallback_translation

    return json.dumps({
        'en': get_translation('en'),
        'et': get_translation('et'),
        'ru': get_translation('ru')
    }).__str__()
