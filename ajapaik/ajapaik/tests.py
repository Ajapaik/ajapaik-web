import pytest
from django.conf import settings

from ajapaik.ajapaik.models import Photo


@pytest.mark.django_db
@pytest.mark.parametrize(('existing_key', 'existing_text'), [
    ('description_et', 'Estonia teatrimaja, vaade Estonia puiesteelt'),
    ('description_fi', 'Rauman kanaalin meren puoleiselta osalta'),
])
def test_nltk_translation(existing_key, existing_text):
    test_instance = Photo()
    setattr(test_instance, existing_key, existing_text)
    test_instance.fill_untranslated_fields()

    for each in settings.ESTNLTK_LANGUAGES:
        print(test_instance, f'description_{each}')
        assert getattr(test_instance, f'description_{each}') is not None
