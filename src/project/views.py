# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext

from project.models import Photo

def index(request):
    return render_to_response('index.html', RequestContext(request, {
        'photos': Photo.objects.all()[:6],
        
    }))