from django.contrib import admin
from django.conf import settings
from project.models import  Photo, GeoTag, \
                            Profile, Source, \
                            Guess, Action, \
                            Album
                            
from sorl.thumbnail.admin import AdminImageMixin

class PhotoAdmin(AdminImageMixin, admin.ModelAdmin):
    pass

admin.site.register(Photo, PhotoAdmin)
admin.site.register(GeoTag)
admin.site.register(Profile)
admin.site.register(Source)
admin.site.register(Guess)
admin.site.register(Action)
admin.site.register(Album)
