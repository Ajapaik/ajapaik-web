# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from project.models import Photo

def test1(request):
    return HttpResponse(unicode(request.get_user()))

def index(request):
    return render_to_response('index.html', RequestContext(request, {
        'photos': Photo.objects.all()[:6],
        
    }))
    
def geotag_add(request, photo_id):
    return ''
