import autocomplete_light
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from project.ajapaik.models import Photo, GeoTag, Profile, Source, Skip, Action, Album, CSVPhoto, Points, Area, \
    AlbumPhoto, Licence, Device, PhotoComment, Newsletter, Dating, Tour, TourRephoto, \
    DatingConfirmation, Video, TourGroup, NorwegianCSVPhoto


class CSVUploadAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='csv_uploaders').exists()

    def has_add_permission(self, request, obj=None):
        return request.user.groups.filter(name='csv_uploaders').exists()


class NorwegianCSVUploadAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='csv_uploaders').exists()

    def has_add_permission(self, request, obj=None):
        return request.user.groups.filter(name='csv_uploaders').exists()


class AlbumPhotoInline(admin.TabularInline):
    model = AlbumPhoto
    fields = 'album',

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(AlbumPhotoInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'album':
            formfield.choices = formfield.choices
        return formfield


class TourGroupInline(admin.TabularInline):
    model = TourGroup
    extra = 1


class TourAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Tour)


class TourGroupAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(TourGroup)


class TourRephotoAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(TourRephoto)


class DatingAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Dating)


class DatingConfirmationAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(DatingConfirmation)


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


class SkipAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Skip)


class GeoTagAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(GeoTag)


class ProfileAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Profile)


class PointsAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Points)


class AlbumAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Album)


class PhotoCommentAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(PhotoComment)


class SourceAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Source)


class AlbumPhotoAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(AlbumPhoto)


class AreaAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Area)


class LicenceAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Licence)


class DeviceAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Device)


class NewsletterAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Newsletter)


class VideoAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Video)


admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoComment, PhotoCommentAdmin)
admin.site.register(GeoTag, GeoTagAdmin)
admin.site.register(Points, PointsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Skip, SkipAdmin)
admin.site.register(Action)
admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumPhoto, AlbumPhotoAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Licence, LicenceAdmin)
admin.site.register(CSVPhoto, CSVUploadAdmin)
admin.site.register(NorwegianCSVPhoto, NorwegianCSVUploadAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Dating, DatingAdmin)
admin.site.register(DatingConfirmation, DatingConfirmationAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(TourGroup, TourGroupAdmin)
admin.site.register(TourRephoto, TourRephotoAdmin)
admin.site.register(Video, VideoAdmin)
