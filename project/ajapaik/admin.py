import autocomplete_light
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from project.ajapaik.models import Photo, GeoTag, Profile, Source, Skip, Action, Album, CSVPhoto, Points, Area,\
    AlbumPhoto, Licence, Device, PhotoComment, CredentialsModel, Newsletter, Dating, Tour, TourPhoto, TourRephoto, \
    DatingConfirmation, Video, TourGroup


class CSVUploadAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='csv_uploaders').exists()

    def has_add_permission(self, request, obj=None):
        return request.user.groups.filter(name='csv_uploaders').exists()


class AlbumPhotoInline(admin.TabularInline):
    model=AlbumPhoto
    fields = 'album',
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(AlbumPhotoInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'album':
            formfield.choices = formfield.choices
        return formfield


class TourPhotoInline(admin.TabularInline):
    model = TourPhoto
    extra = 1


class TourGroupInline(admin.TabularInline):
    model = TourGroup
    extra = 1


class TourAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Tour)

    #inlines = (TourGroupInline,)


class TourGroupAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(TourGroup)


class TourRephotoAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'),
        'original': ('pk', 'description',)
    }


class DatingAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'profile': ('user__first_name', 'user__last_name', 'email', 'fb_name', 'google_plus_name'),
        'photo': ('pk', 'description',),
    }


class DatingConfirmationAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'profile': ('user__first_name', 'user__last_name', 'email', 'fb_name', 'google_plus_name'),
        'confirmation_of': ('pk',),
    }


class PhotoAdmin(ModelAdmin):
    @staticmethod
    def _distance_between_two_points_on_sphere(lon_1, lat_1, lon_2, lat_2):
        import math

        rad = math.pi / 180.0
        equatorial_radius_meters = 6378137
        lon_1_rad = lon_1 * rad
        lat_1_rad = lat_1 * rad
        lon_2_rad = lon_2 * rad
        lat_2_rad = lat_2 * rad
        cos_angle = math.sin(lat_1_rad) * math.sin(lat_2_rad) + math.cos(lat_1_rad) * math.cos(lat_2_rad) * math.cos(
            lon_2_rad - lon_1_rad)

        if cos_angle >= 1:
            return 0

        angle = math.acos(cos_angle)
        return angle * equatorial_radius_meters

    def save_model(self, request, obj, form, change):
        if obj.lat and obj.lon and obj.bounding_circle_radius:
            # If an administrator sets a bounding circle, invalidate GeoTags outside of it
            all_photo_geo_tags = GeoTag.objects.filter(photo_id=obj.id)
            for geo_tag in all_photo_geo_tags:
                d = self._distance_between_two_points_on_sphere(obj.lon, obj.lat, geo_tag.lon, geo_tag.lat)
                if d > obj.bounding_circle_radius:
                    geo_tag.is_correct = False
                else:
                    geo_tag.is_correct = True
                geo_tag.save()
        obj.save()

    inlines = (AlbumPhotoInline,)

    form = autocomplete_light.modelform_factory(Photo)

    # related_search_fields = {
    #     'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'),
    #     'rephoto_of': ('pk', 'description',)
    # }


class SkipAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'),
        'photo': ('pk', 'description',)
    }


class GeoTagAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'),
        'photo': ('pk', 'description',)
    }


class ProfileAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'),
    }


class PointsAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'),
        'photo': ('pk', 'description',),
        'geotag': ('pk', 'photo__description')
    }


class AlbumAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'profile': ('user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'),
        'cover_photo': ('pk', 'description',),
    }


class CredentialsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoComment)
admin.site.register(GeoTag, GeoTagAdmin)
admin.site.register(Points, PointsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Source)
admin.site.register(Skip, SkipAdmin)
admin.site.register(Action)
admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumPhoto)
admin.site.register(Area)
admin.site.register(Licence)
admin.site.register(CSVPhoto, CSVUploadAdmin)
admin.site.register(Device)
admin.site.register(CredentialsModel, CredentialsAdmin)
admin.site.register(Newsletter)
admin.site.register(Dating, DatingAdmin)
admin.site.register(DatingConfirmation, DatingConfirmationAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(TourGroup, TourGroupAdmin)
admin.site.register(TourRephoto, TourRephotoAdmin)
admin.site.register(Video)