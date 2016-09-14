from django.conf import settings


def analytics(self):
    return {
        'analytics': {
            'google_analytics_key': settings.GOOGLE_ANALYTICS_KEY,
        }
    }


def is_user_upload(request):
    ret = False
    if ('HTTP_REFERER' in request.META and 'user-upload' in request.META['HTTP_REFERER']) \
            or ('next' in request.GET and 'user-upload' in request.GET['next']) \
            or ('next' in request.POST and 'user-upload' in request.POST['next']):
        ret = True
    return {
        'is_user_upload': ret
    }
