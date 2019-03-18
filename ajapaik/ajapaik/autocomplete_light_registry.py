import autocomplete_light.shortcuts as al
from autocomplete_light.shortcuts import AutocompleteModelBase
from django.contrib.auth.models import User

from ajapaik.ajapaik.models import Profile, Photo, Points, GeoTag, Album, Dating, DatingConfirmation, AlbumPhoto, \
    Video, PhotoComment, Source, Skip, Area, Licence, Device

al.register(Profile,
            search_fields=['user__pk', 'first_name', 'last_name', 'user__email', 'fb_name', 'google_plus_name'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(User,
            search_fields=['pk', 'first_name', 'last_name', 'email'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Photo,
            search_fields=['pk', 'description'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Photo,
            search_fields=['pk', 'description'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            name='LocatedPhotosAutocomplete',
            choices=Photo.objects.filter(lat__isnull=False, lon__isnull=False)
            )

al.register(Points,
            search_fields=['pk', ],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(GeoTag,
            search_fields=['pk', ],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )


class AlbumAutocomplete(AutocompleteModelBase):
    model = Album
    name = 'AlbumAutocomplete'
    search_fields = ['pk', 'name_en', 'name_et', 'name_fi', 'name_nl', 'name_ru', 'name_sv', 'name_no', 'name_de']
    limit_choices = 1000
    attrs = {
        'data-autocomplete-minimum-characters': 2,
    }
    widget_attrs = {
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    }


al.register(AlbumAutocomplete)


class PublicAlbumAutocomplete(AutocompleteModelBase):
    model = Album
    name = 'PublicAlbumAutocomplete'
    search_fields = ['pk', 'name_en', 'name_et', 'name_fi', 'name_nl', 'name_ru', 'name_sv', 'name_no', 'name_de']
    limit_choices = 1000
    attrs = {
        'data-autocomplete-minimum-characters': 2,
    }
    widget_attrs = {
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    }
    add_another_url_name = 'user_upload_add_album'

    def choices_for_request(self):
        self.choices = self.choices.filter(atype__in=[Album.CURATED, Album.PERSON])

        return super(PublicAlbumAutocomplete, self).choices_for_request()


al.register(PublicAlbumAutocomplete)


class SubjectAlbumAutocomplete(AutocompleteModelBase):
    model = Album
    name = 'SubjectAlbumAutocomplete'
    search_fields = ['pk', 'name_en', 'name_et', 'name_fi', 'name_nl', 'name_ru', 'name_sv', 'name_no', 'name_de']
    limit_choices = 1000
    attrs = {
        'data-autocomplete-minimum-characters': 2,
    }
    widget_attrs = {
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    }
    add_another_url_name = 'face_recognition_add_subject'

    def choices_for_request(self):
        self.choices = self.choices.filter(atype__in=[Album.PERSON])

        return super(SubjectAlbumAutocomplete, self).choices_for_request()


al.register(SubjectAlbumAutocomplete)

al.register(AlbumPhoto,
            search_fields=['pk', ],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Dating,
            search_fields=['pk', ],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(DatingConfirmation,
            search_fields=['pk', ],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Video,
            search_fields=['pk', 'name'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(PhotoComment,
            search_fields=['pk', 'text'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Source,
            search_fields=['pk', 'name', 'description'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Skip,
            search_fields=['pk', ],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Area,
            search_fields=['pk', 'name'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Licence,
            search_fields=['pk', 'name'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )

al.register(Device,
            search_fields=['pk', 'camera_make', 'camera_model'],
            attrs={
                'data-autocomplete-minimum-characters': 2,
            },
            widget_attrs={
                'data-widget-maximum-values': 4,
                'class': 'modern-style',
            },
            )
