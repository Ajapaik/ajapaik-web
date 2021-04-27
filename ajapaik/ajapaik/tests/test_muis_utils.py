import os
import hashlib
import pytest
from datetime import datetime
from django.contrib.auth.models import User
from PIL import Image
from ajapaik import settings
from ajapaik.ajapaik.muis_utils import add_person_albums, extract_dating_from_event, add_dating_to_photo, \
    add_geotag_from_address_to_photo, get_muis_date_and_prefix, set_text_fields_from_muis, reset_modeltranslated_field, \
    raw_date_to_date
import xml.etree.ElementTree as ET
from ajapaik.ajapaik.models import Album

ns = {'d': 'http://www.openarchives.org/OAI/2.0/', 'lido': 'http://www.lido-schema.org'}

@pytest.mark.django_db
def test_add_person_albums():
    xml_string = \
        """<lido:actorInRole>
                <lido:actor>
                    <lido:actorID lido:type="I">
                        1523248
                    </lido:actorID>
                    <lido:nameActorSet>
                        <lido:appellationValue lido:pref="preferred" lido:label="kehtiv nimi">
                            Tuglas,Friedebert
                        </lido:appellationValue>
                    </lido:nameActorSet>
                    <lido:nameActorSet>
                        <lido:appellationValue lido:pref="alternate" lido:label="endine nimetus">
                            1923. aastani Friedebert Mihkelson
                        </lido:appellationValue>
                    </lido:nameActorSet>
                    <lido:vitalDatesActor>
                        <lido:earliestDate>1886</lido:earliestDate>
                        <lido:latestDate>1971</lido:latestDate>
                    </lido:vitalDatesActor>
                </lido:actor>
                <lido:roleActor>
                    <lido:term>kujutatu</lido:term>
                </lido:roleActor>
            </lido:actorInRole>"""
    tree = ET.ElementTree(ET.fromstring(xml_string))
    assert tree == 2
