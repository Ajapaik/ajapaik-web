from django.conf import settings

def analytics(self):
    return {
        'analytics': {
            'google_analytics_key': settings.GOOGLE_ANALYTICS_KEY,
        }
    }


def is_then_and_now(request):
    ret = False
    if ('HTTP_REFERER' in request.META and 'then-and-now-tours' in request.META['HTTP_REFERER']) \
            or ('next' in request.GET and 'then-and-now-tours' in request.GET['next'])\
            or ('next' in request.POST and 'then-and-now-tours' in request.POST['next']):
        ret = True
    return {
        'is_then_and_now': ret
    }