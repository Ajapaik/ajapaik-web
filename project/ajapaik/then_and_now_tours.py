from django.template import RequestContext
from django.shortcuts import render_to_response

def frontpage(request):
    ret = {

    }
    return render_to_response('then_and_now/frontpage.html', RequestContext(request, ret))