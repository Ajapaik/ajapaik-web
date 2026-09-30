import pytest
import responses

from ajapaik.ajapaik.models import Album, Photo


@pytest.mark.django_db
@responses.activate
def test_photos_tartunlp_translation():
    for each in [
        "Igaunijas teātrimaja, skatā Igaunija puiesteelt",
        "Estijos teatro namai, vaizdas Estija puiesteelt",
        "Estonia Theatre House, view Estonia puiesteelt",
        "Эстония театрический дом, вид Эстония пуiesteelt",
        "Estlands Theaterhaus, Sicht auf Estland puiesteelt",
    ]:
        responses.add(
            responses.POST,
            "https://api.tartunlp.ai/translation/v2",
            json={"result": each},
        )
    # Make sure _fi isn't overridden - et is picked as the source because it is at the start of TARTUNLP_LANGUAGES
    test_instance = Photo(
        description_et="Estonia teatrimaja, vaade Estonia puiesteelt",
        description_fi="Viro teatrimaja, vaade Viro puiesteelt",
    )
    test_instance.fill_untranslated_fields()

    assert "teatrimaja" in test_instance.description_et
    assert "Igaunijas" in test_instance.description_lv
    assert "Estijos" in test_instance.description_lt
    assert "Theatre" in test_instance.description_en
    assert "театрический" in test_instance.description_ru
    assert "Theaterhaus" in test_instance.description_de
    assert "Viro" in test_instance.description_fi
    assert "et,fi" == test_instance.description_original_language


@pytest.mark.django_db
@responses.activate
def test_albums_tartunlp_translation():
    for each in [
        "Stereofotos no Parīzes (Francija)",
        "Stereofotos iš Paryžiaus (Prancūzija)",
        "Stereophotos from Paris (France)",
        "Стереофоты из Парижа (Франция)",
        "Stereofotot Pariisista (Ranska)",
    ]:
        responses.add(
            responses.POST,
            "https://api.tartunlp.ai/translation/v2",
            json={"result": each},
        )

    test_instance = Album(
        name_et="Stereofotosid Pariisist (Prantsusmaa)",
        name_de="Stereophotos aus Paris (Frankreich)",
        atype=Album.CURATED,
    )
    test_instance.fill_untranslated_fields()

    assert "Pariisist" in test_instance.name_et
    assert "Parīzes" in test_instance.name_lv
    assert "Paryžiaus" in test_instance.name_lt
    assert "Paris" in test_instance.name_en
    assert "Парижа" in test_instance.name_ru
    assert "Frankreich" in test_instance.name_de
    assert "Pariisista" in test_instance.name_fi
    assert "et,de" == test_instance.name_original_language
