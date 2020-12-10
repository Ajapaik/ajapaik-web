import pytest
import responses

from ajapaik.ajapaik.models import Photo


@pytest.mark.django_db
@pytest.mark.parametrize(('existing_key', 'existing_text'), [
    ('description_et', 'Estonia teatrimaja, vaade Estonia puiesteelt'),
    # ('description_fi', 'Rauman kanaalin meren puoleiselta osalta'),
])
@responses.activate
def test_nltk_translation(existing_key, existing_text):
    for each in [
        'Igaunijas teātrimaja, skatā Igaunija puiesteelt',
        'Estijos teatro namai, vaizdas Estija puiesteelt',
        'Estonia Theatre House, view Estonia puiesteelt',
        'Эстония театрический дом, вид Эстония пуiesteelt',
        'Estlands Theaterhaus, Sicht auf Estland puiesteelt',
        'Viro teatrimaja, vaade Viro puiesteelt'
    ]:
        responses.add(responses.GET, 'https://api.neurotolge.ee/v1.1/translate', json={'tgt': each})
    test_instance = Photo()
    setattr(test_instance, existing_key, existing_text)
    test_instance.fill_untranslated_fields()

    assert 'teatrimaja' in getattr(test_instance, 'description_et')
    assert 'Igaunijas' in getattr(test_instance, 'description_lv')
    assert 'Estijos' in getattr(test_instance, 'description_lt')
    assert 'Theatre' in getattr(test_instance, 'description_en')
    assert 'театрический' in getattr(test_instance, 'description_ru')
    assert 'Theaterhaus' in getattr(test_instance, 'description_de')
    assert 'Viro' in getattr(test_instance, 'description_fi')
