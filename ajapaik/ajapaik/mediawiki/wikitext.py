import json
import re

def replace_or_die(old, new, text, die_on_error=False):
   if not old:
       old=''

   if not new:
       new=''

   if text:
      newtext=text.replace(old, new)
      if (newtext==text and die_on_error):
         print("Replace_or_die failed:" + old +"\t" + new)
         return False
      else:
         return newtext

   return False

def get_licence_template(str): 
   licences={
      'CC BY 4.0' : '{{cc-by-4.0}}',
      'CC-BY-4.0' : '{{cc-by-4.0}}',
      'https://creativecommons.org/licenses/by/4.0/' : '{{cc-by-4.0}}'
   }

   if str in licences:
      return licences[str]
   else:
      return False

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
|description=___DESCRIPTION______PLACE___
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
      'LICENCE_TEMPLATE': out["licence"],
#      'PERMISSION' : "",
      'SOURCE': out["source"],
#      'IDENTIFIER': out["identifierString"],
#      'INSTITUTION_TEMPLATE': out["institution"],
      'LOCATION_TEMPLATE':out['location_template'],
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
      if template == False:
         return False

   return re.sub('\n+', '\n', template.strip())



def get_ajapaik_photo_wikitext_params(p):   
    # r=wikimedia_whoami(user)

    ajapaik_url='https://ajapaik.ee/photo/' + str(p.id)
   
    # External id
    if p.external_id and p.external_id.strip():
        external_id=p.external_id
    elif p.source_url and ('urn:' in p.source_url or 'URN:' in p.source_url) and 'http' not in p.source_url :
        external_id=p.source_url
    else:
        external_id=''

    # Date
    if p.date_text:
        date_text=p.date_text
    else:
        date_text=p.date.strftime('%Y-%m-%d')
   
    # Source text
    if p.source_url and 'http' in p.source_url:
        source_url=p.source_url
    else:
        source_url=ajapaik_url

    if external_id:
        source_text='[' + source_url + ' ' + external_id +']'
    else:
        source_text=source_url
   
    # Rephoto texts
    if p.rephoto_of_id:
        pp=p.rephoto_of
        author_text=p.user.get_display_name
    else:
        pp=p
        author_text=pp.author

    # Target filename
    if pp.title:
        commons_filename=pp.title[:50] 
    elif pp.description:
        commons_filename=pp.description[:50]
    else:
        commons_filename='no name give'

    if p.rephoto_of_id:
        commons_filename="Rephoto of " + commons_filename 

        if p.description:
            description_text=p.description 
        elif pp.description:
            description_text='historical photo description: ' +  pp.description 
        elif p.title:
            description_text=p.title
        elif pp.title:
            description_text='historical photo title: ' +  pp.title
        else:
            description_text=''
    else:
        description_text=p.description or p.title or ''


    if external_id:
        commons_filename=commons_filename + '_-_' + external_id
    else:
        commons_filename=commons_filename + '_-_' + date_text

    # Coordinates
    if p.lat and p.lon and p.azimuth:
        if p.azimuth < 0:
            location_template='{{Location|' + str(p.lat) + '|' + str(p.lon) + '|heading:' + str(360-p.azimuth) + ' source:'+ajapaik_url+'}}' 
        else:
            location_template='{{Location|' + str(p.lat) + '|' + str(p.lon) + '|heading:' + str(p.azimuth) + ' source:'+ajapaik_url+'}}' 
    elif p.lat and p.lon:
        location_template='{{Location|' + str(p.lat) + '|' + str(p.lon) +'|source:'+ajapaik_url+' }}'
    elif pp.lat and pp.lon and pp.azimuth:
        if pp.azimuth < 0:
            location_template='{{Location|' + str(pp.lat) + '|' + str(pp.lon) + '|heading:' + str(360-pp.azimuth) + ' source:'+ajapaik_url+'}}' 
        else:
            location_template='{{Location|' + str(pp.lat) + '|' + str(pp.lon) + '|heading:' + str(pp.azimuth) + ' source:'+ajapaik_url+'}}' 
    elif pp.lat and pp.lon:
        location_template='{{Location|' + str(pp.lat) + '|' + str(pp.lon) +'|source:'+ajapaik_url+' }}'
    else:
        location_template='' 

    # Place
    if p.address:
        address_text='; ' + p.address
    elif pp.address:
        address_text='; ' + pp.address
    else:
        address_text=''

    licence_text=get_licence_template(p.licence.url)
    if not licence_text:
        return False

    out={}
    out["licence"]=get_licence_template(p.licence.url)
#    out["title"]=title_text
    out["description"]=description_text  or title_text
    out["author"]=author_text
    out["date"]=date_text
    out["place"]=address_text
    out["institution"]=""
    out["year_category"]=""
    out["source"]=source_text
    out["identifierString"]=external_id
    out["footer_template"]=""
    out["location_template"]=location_template
    out["target_filename"]=target_filename
    out["source_filename"]='media/' + str(p.image)
    out["ajapaik_url"]=ajapaik_url
    return out
