from django.http import HttpResponse
from models import Photo
from json import loads, dumps

def check_for_duplicate_source_keys(request):
    #Returns photo source_keys that are already in the database
    id_array = loads(request.POST.get("source_keys_json"))
    photos_with_same_source_keys = Photo.objects.filter(source_key__in=id_array)
    ret = []
    for existing_photo in photos_with_same_source_keys:
        ret.append(existing_photo.source_key)
    return HttpResponse(dumps(ret), mimetype="application/json")