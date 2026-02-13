from PIL import Image, ImageOps
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import NotRegistered, AlreadyRegistered
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.urls import re_path
from django.utils.translation import gettext as _
from django_comments_xtd.admin import XtdCommentsAdmin
from sorl.thumbnail import delete as sorl_delete

from ajapaik import settings
from ajapaik.ajapaik.autocomplete import autocomplete_form_factory
from ajapaik.ajapaik.models import Photo, GeoTag, Profile, Source, Skip, Album, Points, Area, \
    AlbumPhoto, Licence, Device, Dating, \
    DatingConfirmation, Video, MyXtdComment, Supporter, \
    Location, LocationPhoto, ApplicationException, ImportBlacklist


class AlbumPhotoInline(admin.TabularInline):
    model = AlbumPhoto
    fields = 'album',
    raw_id_fields = ('album',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(AlbumPhotoInline, self).formfield_for_dbfield(db_field, **kwargs)
        return formfield


class DatingAdmin(ModelAdmin):
    form = autocomplete_form_factory(Dating)


class DatingConfirmationAdmin(ModelAdmin):
    form = autocomplete_form_factory(DatingConfirmation)


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
            all_photo_geotags = GeoTag.objects.filter(photo_id=obj.id)
            for geotag in all_photo_geotags:
                d = self._distance_between_two_points_on_sphere(obj.lon, obj.lat, geotag.lon, geotag.lat)
                if d > obj.bounding_circle_radius:
                    geotag.is_correct = False
                else:
                    geotag.is_correct = True
                geotag.save()
        obj.save()

    def _invertcolors(self, id):
        photo = Photo.objects.filter(pk=id.split('/')[0]).first()
        if photo:
            photo_path = f'{settings.MEDIA_ROOT}/{str(photo.image)}'
            img = Image.open(photo_path)
            inverted_grayscale_image = ImageOps.invert(img).convert('L')
            inverted_grayscale_image.save(photo_path)
            photo.invert = not photo.invert
            sorl_delete(photo.image, delete_file=False)
            photo.light_save()
            return HttpResponse('Photo inverted!')

        return HttpResponse('Failed to invert photo!')

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
        urls = super(PhotoAdmin, self).get_urls()
        my_urls = list(
            (re_path(r'^(.+)/%(url)s/$' % b, self.admin_site.admin_view(b['func'])) for b in self.extra_buttons))
        return my_urls + urls

    inlines = (AlbumPhotoInline,)

    form = autocomplete_form_factory(Photo)
    search_fields = (
        'id',
        'description_et',
        'description_lv',
        'description_lt',
        'description_fi',
        'description_sv',
        'description_nl',
        'description_de',
        'description_ru',
        'description_en',
        'description_nl',
        'description_no',
        'title_et',
        'title_lv',
        'title_lt',
        'title_fi',
        'title_sv',
        'title_nl',
        'title_de',
        'title_ru',
        'title_en',
        'title_no',
        'title_nl',
        'author',
        'types',
        'keywords',
        'source__name',
        'source_key',
        'address',
        'muis_title',
        'muis_comment',
        'muis_event_description_set_note',
        'muis_text_on_object',
        'muis_legends_and_descriptions'
    )


class SkipAdmin(ModelAdmin):
    form = autocomplete_form_factory(Skip)


class GeoTagAdmin(ModelAdmin):
    form = autocomplete_form_factory(GeoTag)


class ProfileAdmin(ModelAdmin):
    form = autocomplete_form_factory(Profile)
    search_fields = (
        'user__id',
        'display_name',
        'first_name',
        'last_name',
        'fb_name',
        'google_plus_name'
    )


class PointsAdmin(ModelAdmin):
    form = autocomplete_form_factory(Points)


class AlbumAdmin(ModelAdmin):
    form = autocomplete_form_factory(Album)
    search_fields = (
        'id',
        'name_et',
        'name_lv',
        'name_lt',
        'name_fi',
        'name_sv',
        'name_nl',
        'name_de',
        'name_ru',
        'name_en',
        'name_nl',
        'name_no',
        'description',
        'slug'
    )


class SourceAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(Source)
    search_fields = (
        'id',
        'name',
        'description'
    )


class AlbumPhotoAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(AlbumPhoto)


class AreaAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(Area)


class LicenceAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(Licence)
    search_fields = ('id', 'name')


class DeviceAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(Device)


class VideoAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(Video)


class SupporterAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(Supporter)


class MyUserAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(User)
    search_fields = ('id', 'username', 'emailaddress__email', 'profile__display_name')


class LocationPhotoAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(LocationPhoto)


class LocationAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(Location)


class ApplicationExceptionAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(ApplicationException)


class ImportBlacklistAdmin(admin.ModelAdmin):
    form = autocomplete_form_factory(ImportBlacklist)


try:
    admin.site.unregister(User)
except NotRegistered:
    pass
try:
    admin.site.register(User, MyUserAdmin)
except AlreadyRegistered:
    pass
admin.site.register(ApplicationException, ApplicationExceptionAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(GeoTag, GeoTagAdmin)
admin.site.register(Points, PointsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Skip, SkipAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(AlbumPhoto, AlbumPhotoAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Licence, LicenceAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Dating, DatingAdmin)
admin.site.register(DatingConfirmation, DatingConfirmationAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(MyXtdComment, XtdCommentsAdmin)
admin.site.register(Supporter, SupporterAdmin)
admin.site.register(LocationPhoto, LocationPhotoAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(ImportBlacklist, ImportBlacklistAdmin)
