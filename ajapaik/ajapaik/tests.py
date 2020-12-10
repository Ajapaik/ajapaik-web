import pytest
import responses

from ajapaik.ajapaik.models import Photo, Album


@pytest.mark.django_db
@pytest.mark.parametrize(('existing_key', 'existing_text'), [
    ('description_et', 'Estonia teatrimaja, vaade Estonia puiesteelt'),
    # ('description_fi', 'Rauman kanaalin meren puoleiselta osalta'),
])
@responses.activate
def test_photos_tartunlp_translation(existing_key, existing_text):
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


@pytest.mark.django_db
@pytest.mark.parametrize(('existing_key', 'existing_text'), [
    ('name_et', 'Stereofotosid Pariisist (Prantsusmaa)'),
])
@responses.activate
def test_albums_tartunlp_translation(existing_key, existing_text):
    for each in [
        'Stereofotos no Parīzes (Francija)',
        'Stereofotos iš Paryžiaus (Prancūzija)',
        'Stereophotos from Paris (France)',
        'Стереофоты из Парижа (Франция)',
        'Stereophotos aus Paris (Frankreich)',
        'Stereofotot Pariisista (Ranska)'
    ]:
        responses.add(responses.GET, 'https://api.neurotolge.ee/v1.1/translate', json={'tgt': each})
    test_instance = Album()
    setattr(test_instance, existing_key, existing_text)
    test_instance.fill_untranslated_fields()

    assert 'Pariisist' in getattr(test_instance, 'description_et')
    assert 'Parīzes' in getattr(test_instance, 'description_lv')
    assert 'Paryžiaus' in getattr(test_instance, 'description_lt')
    assert 'Paris' in getattr(test_instance, 'description_en')
    assert 'Парижа' in getattr(test_instance, 'description_ru')
    assert 'Frankreich' in getattr(test_instance, 'description_de')
    assert 'Pariisista' in getattr(test_instance, 'description_fi')
