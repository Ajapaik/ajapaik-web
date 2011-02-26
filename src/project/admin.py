from django.contrib import admin
from django.conf import settings
from project.models import  Photo, GeoTag, \
                            Profile, Source, \
                            Guess, Action
                            
admin.site.register(Photo)
admin.site.register(GeoTag)
admin.site.register(Profile)
admin.site.register(Source)
admin.site.register(Guess)
admin.site.register(Action)