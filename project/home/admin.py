from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from project.home.models import Photo, GeoTag, Profile, Source, Skip, Action, Album, CSVPhoto, Points, Area, AlbumPhoto


class CSVUploadAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='csv_uploaders').exists()

    def has_add_permission(self, request, obj=None):
        return request.user.groups.filter(name='csv_uploaders').exists()


class PhotoAdmin(ForeignKeyAutocompleteAdmin):
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

    related_search_fields = {
    'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name'),
    'rephoto_of': ('pk', 'description',)
    }


class SkipAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
    'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name'),
    'photo': ('pk', 'description',)
    }


class GeoTagAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
    'user': ('user__first_name', 'user__last_name', 'user__email', 'fb_name'),
    'photo': ('pk', 'description',)
    }


class ProfileAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
    'user': ('first_name', 'last_name', 'email'),
    }


admin.site.register(Photo, PhotoAdmin)
admin.site.register(GeoTag, GeoTagAdmin)
admin.site.register(Points)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Source)
admin.site.register(Skip, SkipAdmin)
admin.site.register(Action)
admin.site.register(Album)
admin.site.register(AlbumPhoto)
admin.site.register(Area)
# admin.site.register(CSVPhoto, CSVUploadAdmin)