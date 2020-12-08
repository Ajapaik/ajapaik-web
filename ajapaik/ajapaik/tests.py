from unittest import mock

import pytest
from django.conf import settings

from ajapaik.ajapaik.models import Photo


@pytest.mark.django_db
@pytest.mark.parametrize(('existing_key', 'existing_text'), [
    ('description_et', 'Estonia teatrimaja, vaade Estonia puiesteelt'),
    ('description_fi', 'Rauman kanaalin meren puoleiselta osalta'),
])
def test_nltk_translation(existing_key, existing_text):
    with mock.patch('socket.socket') as mock_socket:
        mock_socket.return_value.recv.return_value = b'{"raw_trans": ["-"], "raw_input": ["-"], "final_trans": ' \
                                                     b'"Rauma kanali mere poolel"}'
        test_instance = Photo()
        setattr(test_instance, existing_key, existing_text)
        test_instance.fill_untranslated_fields()

        for each in settings.TARTUNLP_LANGUAGES:
            if f'description_{each}' == existing_key:
                continue
            assert getattr(test_instance, f'description_{each}') == 'Rauma kanali mere poolel'
