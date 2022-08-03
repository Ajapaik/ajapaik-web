import json
import re

def replace_or_die(old, new, text):
   if not new:
       new=""

   newtext=text.replace(old, new)
   if (newtext==text):
      print("Replace_or_die failed:" + old +"\t" + new)
      exit(1)

   return newtext

def get_licence_template(str): 
   licences={
      'CC BY 4.0' : '{{cc-by-4.0}}',
      'CC-BY-4.0' : '{{cc-by-4.0}}',
      'https://creativecommons.org/licenses/by/4.0/' : '{{cc-by-4.0}}',
      'https://creativecommons.org/licenses/by/4.0/#1' : '{{cc-by-4.0}}'
   }

   if str in licences:
      return licences[str]
   else:
      return False

def get_institution_template(str):
   if (str=="Ajapaik"):
      return "{{Institution:Ajapaik}}"
   elif (str==""):
      return ""
   else:
      print("get_institution_template failed")
      exit(1)

def get_institution_category(str):
   if (str=="Ajapaik"):
      return "[[Category:Files from Ajapaik]]";
   elif (str==""):
      return "";
   else:
      print("get_institution_category failed")
      exit(1)


def get_ajapaik_photo_wikitext(out):
   template="""
=={{int:filedesc}}==
{{Information
|description=___DESCRIPTION___
|date=___DATE___
|source=___SOURCE___
|author=___AUTHOR___
|permission=
|other versions=
|other fields=___LOCATION_TEMPLATE___
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

   params={
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
      'LOCATION_TEMPLATE': out["location_template"],
      'FOOTER_TEMPLATE': out["footer_template"],
      'INSTITUTION_CATEGORY': get_institution_category(out["institution"]),
      'CREATOR_CATEGORY': "",
      'TRACKING_CATEGORY': "[[Category:Files uploaded by Ajapaik]]",
      'YEAR_CATEGORY': out["year_category"],
      'PLACE_CATEGORY':""
   }

   for key in params:
      fullkey="___" + key + "___"
      template=replace_or_die(fullkey, params[key], template)

   return re.sub('\n+', '\n', template.strip())


