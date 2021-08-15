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

def photo_manifest_v3(request, photo_id=None, pseudo_slug=None):
    lang_code = request.LANGUAGE_CODE
    p = get_object_or_404(Photo, id=photo_id)

    if p.title:
       title=p.title 
    else:
       title=p.description

    # Render licence text
    licence_text=_render_licence_text(p.licence)
    rights_url=_render_rights_url(p.licence)
    source_text=_render_source_text(p.source, p.source_url, p.source_key)

    # Canonical url to creative commons licence uses http://
    rights_url=rights_url.replace('https://creativecommons.org', 'http://creativecommons.org')
    thumb_width, thumb_height=calculate_thumbnail_size(p.width, p.height, 800)
    iiif_image_url="https://ajapaik.ee/iiif/work/iiif/ajapaik/" + remove_prefix(str(p.image), 'uploads/') + ".tif"

    content={
        '@context':  "http://iiif.io/api/presentation/3/context.json",
        'id': "https://ajapaik.ee/photo/" + str(photo_id) + "/manifest.json",
        'type': "Manifest",
        'label': { "en" : [ title ] },
        'rights': rights_url,
        'requiredStatement': {
            'label': { 'en': [ 'Attribution' ] },
            'value': { 'en': [ source_text ] }
         },
         'thumbnail': [ {
             'id': "https://ajapaik.ee/photo-thumb/" + str(photo_id) + "/800/",
             'type': "dctypes:Image",
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
        licence={ '@value': p.licence.name, '@id':rights_url}
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

def photo_manifest_v2(request, photo_id=None, pseudo_slug=None):
    lang_code = request.LANGUAGE_CODE
    p = get_object_or_404(Photo, id=photo_id)

    if p.title:
       title=p.title 
    else:
       title=p.description

    # Render licence text
    licence_text=_render_licence_text(p.licence)
    rights_url=_render_rights_url(p.licence)
    source_text=_render_source_text(p.source, p.source_url, p.source_key)

    thumb_width, thumb_height=calculate_thumbnail_size(p.width, p.height, 400)
    iiif_image_url="https://ajapaik.ee/iiif/work/iiif/ajapaik/" + remove_prefix(str(p.image), 'uploads/') + ".tif"

    content={
        '@context':  "http://iiif.io/api/presentation/2/context.json",
        '@id': "https://ajapaik.ee/photo/" + str(photo_id) + "/v2/manifest.json",
        '@type': "sc:Manifest",
        'label': title ,
        'attribution': source_text,

         'thumbnail': {
             '@id': "https://ajapaik.ee/photo-thumb/" + str(photo_id) + "/400/",
             '@type': "dctypes:Image",
             'format': "image/jpeg",
             'width': thumb_width,
             'height': thumb_height,
         }
    }

    metadata = []
    if p.date_text:
        metadata.append({'label': multilang_string_v2('Date', 'en'), 'value': p.date_text })

    if p.source:
        metadata.append({'label': multilang_string_v2('Source', 'en'), 'value': source_text })

    if p.source_key:
        metadata.append({'label': multilang_string_v2('Identifier', 'en'), 'value': p.source_key })

    if p.author:
        metadata.append({'label': multilang_string_v2('Author', 'en'), 'value': p.author })

    if p.licence:
        metadata.append({'label': multilang_string_v2('Licence', 'en'), 'value': licence_text, 'id': rights_url })

    if p.lat and p.lon:
        location='Latitude: ' + str(p.lat) +', Longitude: ' + str(p.lon)
        metadata.append({'label': multilang_string_v2('Coordinates', 'en'), 'value': location })

    if p.perceptual_hash:
        # signed int to unsigned int conversion
        if p.perceptual_hash<0:
            phash=str(p.perceptual_hash & 0xffffffffffffffff)
        else:
            phash=str(p.perceptual_hash)
        metadata.append({'label': multilang_string_v2('Perceptual hash', 'en'), 'value': str(phash), 'description': 'Perceptual hash (phash) checksum calculated using ImageHash library. https://pypi.org/project/ImageHash/'  })


    canvas_id='https://ajapaik.ee/photo/' + str(photo_id)+ '/canvas/p1'
    content['metadata']=metadata
    content['sequences']=[
            {
            '@id': 'https://ajapaik.ee/photo/' + str(photo_id) + '/sequence/normal.json',
            '@type': "sc:Sequence",
            'canvases': [ {
                '@id': canvas_id,
                '@type': "sc:Canvas",
                'label': multilang_string_v2(title, 'en'),
                'width': p.width,
                'height': p.height,
                'images': [
                    {
                        "@id": "https://ajapaik.ee/photo/" + str(photo_id)+ "/annotation/a1",
                        "@type": "oa:Annotation",
                        "motivation": "sc:painting",
                        "on": canvas_id,
                        "resource":
                            {
                                    "@id": iiif_image_url + "/full/max/0/default.jpg",
                                    "@type": "Image",
                                    "format": "image/jpeg",
                                    "service": [
                                        {
                                            '@id': iiif_image_url,
                                            '@context': 'http://iiif.io/api/image/2/context.json',
                                            'profile': 'http://iiif.io/api/image/2/level1.js'
                                        }
                                    ],
                                    "height": p.width,
                                    "width": p.height
                            }
                    }
                ]
                } ],
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



def _render_licence_text(licence):
    licence_text=''
    if licence:
        if licence.url and licence.name:
            licence_text='<a href=' + licence.url + '>' + licence.name +'</a>'
        elif licence.url:
            licence_text=licence.url
        elif licence.name:
            licence_text=licence.name
    return licence_text

def _render_rights_url(licence):
    rights_url=''
    if licence:
        rights_url= str(licence.url)
    # Canonical url to creative commons licence uses http://
    rights_url=rights_url.replace('https://creativecommons.org', 'http://creativecommons.org')
    return rights_url

def _render_source_text(source, source_url, identifier):
    source_text = ''

    # Render source text
    if source_url and source and source.name and identifier:
        source_text=source.name +': <a href=' + source_url + '>' + identifier + '</a>'
    elif source_url and identifier:
        source_text='<a href=' + source_url + '>' + identifier + '</a>'
    elif source_url and source and source.name:
        source_text='<a href=' + source_url + '>' + source.name + '</a>'
    elif source and source.name and identifier:
        source_text = source.name + ':' + identifier
    elif source and source.name:
        source_text = source.name
    elif identifier:
        source_text = identifier

    return source_text

def multilang_string_v2(value, language):
    return { '@value': value, '@language': language}
