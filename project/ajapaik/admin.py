import autocomplete_light
from PIL import Image, ImageOps
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.translation import ugettext as _
from django_comments_xtd.admin import XtdCommentsAdmin
from sorl.thumbnail import delete as sorl_delete

from project.ajapaik import settings
from project.ajapaik.models import Photo, GeoTag, Profile, Source, Skip, Action, Album, CSVPhoto, Points, Area, \
    AlbumPhoto, Licence, Device, Newsletter, Dating, Tour, TourRephoto, \
    DatingConfirmation, Video, TourGroup, NorwegianCSVPhoto, MyXtdComment


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
    form = autocomplete_light.modelform_factory(Tour, fields='__all__')


class TourGroupAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(TourGroup, fields='__all__')


class TourRephotoAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(TourRephoto, fields='__all__')


class DatingAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Dating, fields='__all__')


class DatingConfirmationAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(DatingConfirmation, fields='__all__')


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

    def _invertcolors(self, id):
        from django.http.response import HttpResponse
        photo = Photo.objects.filter(pk=id).first()
        if photo:
            photo_path = settings.MEDIA_ROOT + "/" + str(photo.image)
            img = Image.open(photo_path)
            inverted_grayscale_image = ImageOps.invert(img).convert('L')
            inverted_grayscale_image.save(photo_path)
            photo.invert = not photo.invert
            sorl_delete(photo.image, delete_file=False)
            photo.light_save()
            return HttpResponse(u'Photo inverted!')

        return HttpResponse(u'Failed to invert photo!')

    extra_buttons = [
        {
            'url': '_invertcolors',
            'textname': _('Invert colors'),
            'func': _invertcolors
        },
    ]

    def change_view(self, request, object_id, form_url='', extra_context={}):
        extra_context['extra_buttons'] = self.extra_buttons
        return super(PhotoAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        from django.conf.urls import url
        urls = super(PhotoAdmin, self).get_urls()
        my_urls = list((url(r'^(.+)/%(url)s/$' % b, self.admin_site.admin_view(b['func'])) for b in self.extra_buttons))
        return my_urls + urls

    inlines = (AlbumPhotoInline,)

    form = autocomplete_light.modelform_factory(Photo, fields='__all__')


class SkipAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Skip, fields='__all__')


class GeoTagAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(GeoTag, fields='__all__')


class ProfileAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Profile, fields='__all__')


class PointsAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Points, fields='__all__')


class AlbumAdmin(ModelAdmin):
    form = autocomplete_light.modelform_factory(Album, fields='__all__')


class SourceAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Source, fields='__all__')


class AlbumPhotoAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(AlbumPhoto, fields='__all__')


class AreaAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Area, fields='__all__')


class LicenceAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Licence, fields='__all__')


class DeviceAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Device, fields='__all__')


class NewsletterAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Newsletter, fields='__all__')


class VideoAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Video, fields='__all__')

admin.site.register(Photo, PhotoAdmin)
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
admin.site.register(MyXtdComment, XtdCommentsAdmin)
