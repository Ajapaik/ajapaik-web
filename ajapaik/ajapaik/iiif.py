from django.http import HttpResponse, JsonResponse
from django.utils.http import urlencode
from django.shortcuts import redirect, get_object_or_404, render
from ajapaik.ajapaik.models import Album, Photo, PhotoSceneSuggestion, Points, Profile, Licence, PhotoLike
from ajapaik.utils import calculate_thumbnail_size

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text 

def photo_info(request, photo_id=None, pseudo_slug=None):
    p = get_object_or_404(Photo, id=photo_id)
    iiif_image_url="https://ajapaik.ee/iiif/work/iiif/ajapaik/" + remove_prefix(str(p.image), 'uploads/') + ".tif/info.json"
    return redirect(iiif_image_url)

    content={}
    return JsonResponse(content, content_type='application/json')

def photo_manifest(request, photo_id=None, pseudo_slug=None):
    lang_code = request.LANGUAGE_CODE
    p = get_object_or_404(Photo, id=photo_id)

    if p.title:
       title=p.title 
    else:
       title=p.description

    # Render licence text
    if p.licence.url and p.licence.name:
        licence_text='<a href=' + p.licence.url + '>' + p.licence.name +'</a>'
    elif p.licence.url:
        licence_text=p.licence.url
    elif p.licence.name:
        licence_text=p.licence.name
    else:
        licence_text=''

    # Render source text
    if p.source_url and p.source.name and p.source_key:
        source_text=p.source.name +': <a href=' + p.source_url + '>' + p.source_key + '</a>'
    elif p.source_url and p.source_key:
        source_text='<a href=' + p.source_url + '>' + p.source_key + '</a>'
    elif p.source_url and p.source.name:
        source_text='<a href=' + p.source_url + '>' + p.source.name + '</a>'
    elif p.source.name and p.source_key:
        source_text = p.source.name + ':' + p.source_key
    elif p.source_name:
        source_text = p.source_name
    elif p.source_key:
        source_text = p.source_key
    else:
        source_text = ''
 


    rights_url= str(p.licence.url)
     
    # Canonical url to creative commons licence uses http://
    rights_url=rights_url.replace('https://creativecommons.org', 'http://creativecommons.org')
    thumb_width, thumb_height=calculate_thumbnail_size(p.width, p.height, 800)
    iiif_image_url="https://ajapaik.ee/iiif/work/iiif/ajapaik/" + remove_prefix(str(p.image), 'uploads/') + ".tif"

    content={
        '@context':  "http://iiif.io/api/presentation/3/context.json",
        'id': "https://ajapaik.ee/photo/" + str(photo_id) + "/manifest.json",
        'type': "Manifest",
        'label': { "en" : [ title ] },
        'rights': str(p.licence.url).replace('https://creativecommons.org', 'http://creativecommons.org'),
        'requiredStatement': {
            'label': { 'en': [ 'Attribution' ] },
            'value': { 'en': [ source_text ] }
         },
         'thumbnail': [ {
             '@id': "https://ajapaik.ee/photo-thumb/" + str(photo_id) + "/800/",
             '@type': "dctypes:Image",
             'format': "image/jpeg",
             'width': thumb_width,
             'height': thumb_height,
         } ]
    }

    metadata = []
    if p.date_text:
        metadata.append({'label': { 'en' : ['Date'] }, 'value': { 'none' : [p.date_text] } })

    if p.source:
        metadata.append({'label': { 'en' : ['Source'] }, 'value': { 'none': [source_text] } })

    if p.source_key:
        metadata.append({'label': { 'en': ['Identifier'] } , 'value': { 'none': [p.source_key] } })

    if p.author:
        metadata.append({'label': { 'en': ['Author'] } , 'value':  { 'none': [p.author] } })

    if p.licence:
        licence={ '@value': p.licence.name, '@id':p.licence.url}
        metadata.append({'label': {'en': ['Licence'] }, 'value': { 'none' : [licence_text] } })

    if p.lat and p.lon:
        location='Latitude: ' + str(p.lat) +', Longitude: ' + str(p.lon)
        metadata.append({'label': { 'en' : ['Coordinates'] } , 'value': { 'en' : [location] } })

    if p.perceptual_hash:
        # signed int to unsigned int conversion
        if p.perceptual_hash<0:
            phash=str(p.perceptual_hash & 0xffffffffffffffff)
        else:
            phash=str(p.perceptual_hash)
        metadata.append({'label': { 'en': ['Perceptual hash'] }, 'value': { 'none': [str(phash)] }, 'description': 'Perceptual hash (phash) checksum calculated using ImageHash library. https://pypi.org/project/ImageHash/'  })

    content['metadata']=metadata
    content['items']=[
            {

#"id": "https://example.org/iiif/book1/canvas/p1",
                'id': "https://ajapaik.ee/photo/" + str(photo_id)+ "/canvas/p1",
                'type': "canvas",
                'label': { "none": [ "p. 1" ] },
                'width': p.width,
                'height': p.height,
                'items': [
                    {
                        "id": "https://ajapaik.ee/photo/" + str(photo_id)+ "/canvas/p1/1",
                        "type": "AnnotationPage",
                        "items": [
                            {
                                "id": "https://ajapaik.ee/photo/" + str(photo_id)+ "/annotation/p0001-image",
                                "type": "Annotation",
                                "motivation": "painting",
                                "body": {
                                    "id": iiif_image_url + "/full/max/0/default.jpg",
                                    "type": "Image",
                                    "format": "image/jpeg",
                                    "service": [
                                        {
                                            "id": iiif_image_url,
                                            "type": "ImageService2",
                                            "profile": "level2",
                                        }
                                    ],
                                    "height": p.width,
                                    "width": p.height
                                },
                                "target": "https://ajapaik.ee/photo/" + str(photo_id)+ "/canvas/p1"
                            }
                        ]
                    }
                ],
            }
        ]

    response= JsonResponse(content, content_type='application/json')
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

    return response

def photo_annotations(request, photo_id=None, pseudo_slug=None):
    p = get_object_or_404(Photo, id=photo_id)

    content={}
    return JsonResponse(content, content_type='application/json')

