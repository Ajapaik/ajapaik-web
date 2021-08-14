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

    content={
        '@context': "http://iiif.io/api/presentation/2/context.json",
        '@id': "https://ajapaik.ee/photo/" + str(photo_id) + "/manifest.json",
        '@type': "sc:Manifest"
    }

    thumb_width, thumb_height=calculate_thumbnail_size(p.width, p.height, 800)

    if p.title:
       title=p.title 
    else:
       title=p.description

    if p.title:
        content['description'] = {
#            '@language': lang_code,
            '@value': p.description
        }

    if p.description:
        content['label']={
#             '@language': lang_code,
             '@value': title
        }

    metadata = []
    if p.date_text:
        metadata.append({'label': 'date', 'value': p.date_text})

    if p.source:
        metadata.append({'label': 'source', 'value': p.source.name})

    if p.source_url:
        metadata.append({'label': 'source_url', 'value': p.source_url})

    if p.source_key:
        metadata.append({'label': 'identifier', 'value': p.source_key})

    if p.author:
        metadata.append({'label': 'author', 'value': p.author})

    if p.licence:
        licence={ 'name': p.licence.name, 'url':p.licence.url}
        metadata.append({'label': 'licence', 'value': licence})

    if p.lat and p.lon:
        location={ 'lat': p.lat, 'lon': p.lon }
        metadata.append({'label': 'DC.Coverage.spatial', 'value': location })

    if p.lat and p.lon:
        location={ 'lat': p.lat, 'lon': p.lon }
        metadata.append({'label': 'DC.Coverage.spatial', 'value': location })

    if p.perceptual_hash:
        metadata.append({'label': 'perceptual hash', 'value': p.perceptual_hash, 'description': 'Perceptual hash (phash) checksum calculated using ImageHash library', 'url': 'https://pypi.org/project/ImageHash/'  })

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
                    'width': p.width,
                    'height': p.height,
                    'images': [
                    {
                        '@id': "https://ajapaik.ee/photo/" + str(photo_id) + "/annotation/a0.json",
                        '@type': "oa:Annotation",
                        'motivation': "sc:painting",
                        'on': "https://ajapaik.ee/photo/" + str(photo_id) + "/canvas/c0.json",
                        'resource': {
                            '@id': "https://ajapaik.ee/" + str(p.image),
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

