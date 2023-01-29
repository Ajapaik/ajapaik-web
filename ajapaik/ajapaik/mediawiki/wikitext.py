import re
from typing import Any


def replace_or_die(old, new, text):
    new_text = text.replace(old, new)
    if new_text == text:
        print("Replace_or_die failed:" + old + "\t" + new)
        exit(1)

    return new_text


def get_licence_template(value: str):
    if value in ["CC BY 4.0", "CC-BY-4.0"]:
        return "{{cc-by-4.0}}"
    else:
        print("get_licence_template failed")
        exit(1)


def get_institution_template(value: str):
    if value == "Ajapaik":
        return "{{Institution:Ajapaik}}"
    elif value == "":
        return ""
    else:
        print("get_institution_template failed")
        exit(1)


def get_institution_category(value: str):
    if value == "Ajapaik":
        return "[[Category:Files from Ajapaik]]"
    elif value == "":
        return ""
    else:
        print("get_institution_category failed")
        exit(1)


def upload_own_photo_wikitext(out: dict[str, Any]):
    template = """
=={{int:filedesc}}==
{{Information
|description=___DESCRIPTION___
|date=___DATE___
|source=___SOURCE___
|author=___AUTHOR___
|permission=
|other versions=
|other fields=___COORD___
}}

== {{int:license-header}} ==
___LICENCE_TEMPLATE___
___FOOTER_TEMPLATE___
___INSTITUTION_CATEGORY___
___CREATOR_CATEGORY___
___TRACKING_CATEGORY___
___YEAR_CATEGORY___
___PLACE_CATEGORY___
   """

    params = {
        'AUTHOR': out["author"],
        #      'TITLE': out["title"],
        'DESCRIPTION': out["description"],
        #      'PLACE': out["place"],
        'DATE': out["date"],
        'LICENCE_TEMPLATE': get_licence_template(out["licence"]),
        #      'PERMISSION' : "",
        'SOURCE': out["source"],
        #      'IDENTIFIER': out["identifierString"],
        #      'INSTITUTION_TEMPLATE': get_institution_template(out["institution"]),
        'COORD': "",
        'FOOTER_TEMPLATE': out["footer_template"],
        'INSTITUTION_CATEGORY': get_institution_category(out["institution"]),
        'CREATOR_CATEGORY': "",
        'TRACKING_CATEGORY': "[[Category:Files uploaded by Ajapaik]]",
        'YEAR_CATEGORY': out["year_category"],
        'PLACE_CATEGORY': ""
    }

    for key in params:
        full_key = "___" + key + "___"
        template = replace_or_die(full_key, params[key], template)

    return re.sub('\n+', '\n', template.strip())
