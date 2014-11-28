from django.conf import settings
def analytics(self):
    return {
        'analytics': {
            'google_analytics_key': settings.GOOGLE_ANALYTICS_KEY,
            
        }
    }