from django.http import HttpResponse, JsonResponse
from django.utils.http import urlencode
from django.shortcuts import redirect, get_object_or_404, render
from ajapaik.ajapaik.models import Album, Photo, PhotoSceneSuggestion, Points, Profile, Licence, PhotoLike
from ajapaik.utils import calculate_thumbnail_size

def photo_info(request, photo_id=None, pseudo_slug=None):
    p = get_object_or_404(Photo, id=photo_id)
    return redirect('/iiif/ajapaik/' + str(p.image) + "/info.json")

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
 

    content={
        '@context':  "http://iiif.io/api/presentation/3/context.json",
        'id': "https://ajapaik.ee/photo/" + str(photo_id) + "/manifest.json",
        'type': "Manifest",
        'label': { "en" : [ title ] },
        'description': '',
        'licence': licence_text,
        'attribution': source_text 
    }

    thumb_width, thumb_height=calculate_thumbnail_size(p.width, p.height, 800)


    metadata = []
    if p.date_text:
        metadata.append({'label': { 'en' : ['Date'] }, 'value': { 'none' : [p.date_text] } })

    if p.source:
        metadata.append({'label': { 'en' : ['Source'] }, 'value': { 'none': [source_text], '@id': p.source_url } })

    if p.source_key:
        metadata.append({'label': { 'en': ['Identifier'] } , 'value': { 'none': [p.source_key] } })

    if p.author:
        metadata.append({'label': { 'en': ['Author'] } , 'value':  { 'none': [p.author] } })

    if p.licence:
        licence={ '@value': p.licence.name, '@id':p.licence.url}
        metadata.append({'label': {'en': ['Licence'] }, 'value': { 'none' : [licence_text], '@id': p.licence.url} })

    if p.lat and p.lon:
        location={ '@value': str(p.lat) +', ' + str(p.lon), 'lat': p.lat, 'lon': p.lon }
        metadata.append({'label': { 'en' : ['Coordinates'] } , 'value': { 'none' : [location] } })

    if p.perceptual_hash:
        metadata.append({'label': { 'en': ['Perceptual hash'] }, 'value': { 'none': [p.perceptual_hash] }, 'description': 'Perceptual hash (phash) checksum calculated using ImageHash library. https://pypi.org/project/ImageHash/'  })

    content['metadata']=metadata
    content['sequences']=[
            {
                '@id': "https://ajapaik.ee/photo/" + str(photo_id)+ "/sequence/normal.json",
                '@type': "sc:Sequence",
                'label': "default order",
                'canvases': [
                {
                    '@id': "https://ajapaik.ee/photo/" + str(photo_id) + "/canvas/c0.json",
                    '@type': "sc:Canvas",
                    'label': "p 1",
                    'width': p.width,
                    'height': p.height,
                    'images': [
                    {
                        '@id': "https://ajapaik.ee/photo/" + str(photo_id) + "/annotation/a0.json",
                        '@type': "oa:Annotation",
                        'motivation': "sc:painting",
                        'on': "https://ajapaik.ee/photo/" + str(photo_id) + "/canvas/c0.json",
                        'resource': {
                            '@id': "https://ajapaik.ee/media/" + str(p.image),
                            '@type': "dctypes:Image",
                            'format': "image/jpeg",
	                    'width': p.width,
        	            'height': p.height,
                        }
                    }
                ],
                'label': {
#                    '@language': lang_code,
                    '@value': title
                },
#                'otherContent': [
#                   {
#                      '@id': "https://wd-image-positions.toolforge.org/iiif/Q1231009/P18/list/annotations.json",
#                      '@type': "sc:AnnotationList",
#                      'label': "Things depicted on this canvas"
#                   }
#                ],
                'thumbnail': {
                   '@id': "https://ajapaik.ee/photo-thumb/" + str(photo_id) + "/800/",
                   '@type': "dctypes:Image",
                   'format': "image/jpeg",
                   'width': thumb_width,
                   'height': thumb_height,
                }
                }
                ]
            }
        ]

    return JsonResponse(content, content_type='application/json')


def photo_annotations(request, photo_id=None, pseudo_slug=None):
    p = get_object_or_404(Photo, id=photo_id)

    content={}
    return JsonResponse(content, content_type='application/json')

