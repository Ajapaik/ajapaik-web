from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin

from project.sift.models import CatAlbum, CatPhoto, CatTag, CatTagPhoto, CatUserFavorite, CatPushDevice, CatProfile, \
    Source


class ProfileAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'user': ('user__first_name', 'user__last_name', 'user__email'),
    }


class CatTagPhotoAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'profile': ('user__first_name', 'user__last_name', 'user__email'),
    }


class CatUserFavoriteAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'profile': ('user__first_name', 'user__last_name', 'user__email'),
    }


class CatPushDeviceAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'profile': ('user__first_name', 'user__last_name', 'user__email'),
    }


admin.site.register(CatAlbum)
admin.site.register(CatPhoto)
admin.site.register(CatTag)
admin.site.register(CatProfile, ProfileAdmin)
admin.site.register(Source)
admin.site.register(CatTagPhoto, CatTagPhotoAdmin)
admin.site.register(CatUserFavorite, CatUserFavoriteAdmin)
admin.site.register(CatPushDevice, CatPushDeviceAdmin)
