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
    iiif_image_url=request.build_absolute_uri('/iiif/work/iiif/ajapaik/' + remove_prefix(str(p.image), 'uploads/') + '.tif/info.json')
    return redirect(iiif_image_url)

    content={}
    return JsonResponse(content, content_type='application/json')

def photo_manifest_v2(request, photo_id=None, pseudo_slug=None):
    lang_code = request.LANGUAGE_CODE
    p = get_object_or_404(Photo, id=photo_id)

    if p.title:
       title=p.title 
    elif p.description:
       title=p.description
    else:
       title=request.build_absolute_uri('/photo/' + str(photo_id))

    # Render licence text
    licence_text=_render_licence_text(p.licence)
    rights_url=_render_rights_url(p.licence)
    source_text=_render_source_text(p.source, p.source_url, p.source_key)

    thumb_width, thumb_height=calculate_thumbnail_size(p.width, p.height, 400)
    iiif_image_url=request.build_absolute_uri('/iiif/work/iiif/ajapaik/' + remove_prefix(str(p.image), 'uploads/') + '.tif')

    content={
        '@context':  'http://iiif.io/api/presentation/2/context.json',
        '@id': request.build_absolute_uri('/photo/' + str(photo_id) + '/v2/manifest.json'),
        '@type': 'sc:Manifest',
        'label': multilang_string_v2(title, lang_code),
        'description': multilang_string_v2(title, lang_code),
        'attribution': source_text,
        'rendering': {
             '@id': request.build_absolute_uri('/photo/' + str(photo_id)),
             'format': 'text/html',
             'label': 'Full record view'
         },
        'thumbnail': {
             '@id': request.build_absolute_uri('/photo-thumb/' + str(photo_id) + '/400/'),
             '@type': 'dctypes:Image',
             'format': 'image/jpeg',
             'width': thumb_width,
             'height': thumb_height,
         }
    }

    metadata = []
    canvases = []
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

    attribution_text=_render_attribution(source_text, p.author, p.date_text, licence_text)
    canvases.append(_get_v2_canvas(request, photo_id, title, lang_code, iiif_image_url, p.width, p.height, 'photo_' +str(photo_id), attribution_text, rights_url, p))

    rephotos=Photo.objects.filter(rephoto_of=photo_id)
    for rephoto in rephotos:
        rephoto_iiif_image_url=request.build_absolute_uri('/iiif/work/iiif/ajapaik/' + remove_prefix(str(rephoto.image), 'uploads/') + '.tif')
        rephoto_licence_text=_render_licence_text(rephoto.licence)
        rephoto_rights_url=_render_rights_url(rephoto.licence)
        rephoto_source_text=_render_source_text(rephoto.source, rephoto.source_url, rephoto.source_key)
        if not rephoto_source_text:
            rephoto_uri=request.build_absolute_uri('/photo/' + str(rephoto.id))
            rephoto_source_text='Ajapaik.ee: <a href="' + rephoto_uri + '">' + str(rephoto.id) +'</a>'

        # Some author name for the rephotos
        if rephoto.author:
            rephoto_author=rephoto.author
        elif rephoto.user:
            rephoto_author=rephoto.user.get_display_name
        else:
            rephoto_author='Unknown'

        rephoto_attribution_text=_render_attribution(rephoto_source_text, rephoto_author, rephoto.date_text, rephoto_licence_text)

        if rephoto.title:
            rephoto_title=rephoto.title
        elif rephoto.description:
            rephoto_title=rephoto.description
        else:
            rephoto_title='Rephoto of ' + request.build_absolute_uri('/photo/' + str(photo_id)) + ' with title "' + title +'"'

        canvases.append(_get_v2_canvas(
            request,
            photo_id,
            rephoto_title,
            lang_code,
            rephoto_iiif_image_url,
            rephoto.width,
            rephoto.height,
            'rephoto_' + str(rephoto.id),
            rephoto_attribution_text,
            rephoto_rights_url,
            rephoto
          ))


    content['metadata']=metadata
    content['sequences']=[ {
            '@id': request.build_absolute_uri('/photo/' + photo_id + '/sequence/normal.json'),
            '@type': 'sc:Sequence',
            'canvases': canvases
    } ]


    response= JsonResponse(content, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response['Access-Control-Max-Age'] = '1000'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type'

    return response

def photo_annotations(request, photo_id=None, pseudo_slug=None):
    p = get_object_or_404(Photo, id=photo_id)

    content={}
    return JsonResponse(content, content_type='application/json')

########################################################################
# Helper functions
#

def _get_v2_canvas(request, photo_id, label, lang_code, iiif_image_url, width, height, canvas_name, source_text, licence_url, thumbnail):


    thumb_width, thumb_height=calculate_thumbnail_size(thumbnail.width, thumbnail.height, 400)

    photo_id=str(photo_id)
    canvas_id=request.build_absolute_uri('/photo/' + photo_id + '/canvas/' + canvas_name)
    canvas={
                '@id': canvas_id,
                '@type': 'sc:Canvas',
                'label': multilang_string_v2(label, lang_code),
                'width': width,
                'height': height,
                'thumbnail': {
                    '@id': request.build_absolute_uri('/photo-thumb/' + str(thumbnail.id) + '/400/'),
                    '@type': 'dctypes:Image',
                    'format': 'image/jpeg',
                    'width': thumb_width,
                    'height': thumb_height,
                },
                'images': [
                    {
                        '@id': request.build_absolute_uri('/photo/' + photo_id + '/annotation/' + canvas_name),
                        '@type': 'oa:Annotation',
                        'motivation': 'sc:painting',
                        'on': canvas_id,
                        'resource':
                            {
                                    '@id': iiif_image_url + '/full/max/0/default.jpg',
                                    '@type': 'dctypes:Image',
                                    'format': 'image/jpeg',
                                    'service':
                                        {
                                            '@id': iiif_image_url,
                                            '@context': 'http://iiif.io/api/image/2/context.json',
                                            'profile': 'http://iiif.io/api/image/2/level1.json'
                                        },
                                    'height': width,
                                    'width': height
                            }
                    }
                ]
            }
    if source_text:
        canvas['attribution']=source_text

    if licence_url:
        canvas['licence']=licence_url

    return canvas


# print html licence string
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

# canonical link to licence
def _render_rights_url(licence):
    rights_url=''
    if licence:
        rights_url= str(licence.url)
    # Canonical url to creative commons licence uses http://
    rights_url=rights_url.replace('https://creativecommons.org', 'http://creativecommons.org')
    return rights_url

# Print html credits line
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

def _render_attribution(source, author, date, licence):
    attribution=[]
    if source:
        attribution.append(source)
    if author:
        attribution.append(author)
    if date:
        attribution.append(str(date))
    if licence:
        attribution.append(licence)

    return ', '.join(attribution)

def multilang_string_v2(value, language):
    return { '@value': value, '@language': language}

