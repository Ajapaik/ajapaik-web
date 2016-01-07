import autocomplete_light.shortcuts as al
from django.contrib.auth.models import User

from project.ajapaik.models import Profile, Photo, Tour, Points, GeoTag, Album, Dating, DatingConfirmation, AlbumPhoto, \
    Video, PhotoComment, Source, Skip, Area, Licence, Device, Newsletter, TourGroup, TourRephoto

al.register(Profile,
    search_fields=['user__pk', 'user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'],
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
    name = 'LocatedPhotosAutocomplete',
    choices = Photo.objects.filter(lat__isnull=False, lon__isnull=False)
)

al.register(Tour,
    search_fields=['pk', 'name'],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)

al.register(TourGroup,
    search_fields=['pk', 'name'],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)

al.register(TourRephoto,
    search_fields=['pk',],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)

al.register(Points,
    search_fields=['pk',],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)

al.register(GeoTag,
    search_fields=['pk',],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)

al.register(Album,
    search_fields=['pk', 'name'],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)

al.register(AlbumPhoto,
    search_fields=['pk',],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)

al.register(Dating,
    search_fields=['pk',],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)

al.register(DatingConfirmation,
    search_fields=['pk',],
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
    search_fields=['pk',],
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

al.register(Newsletter,
    search_fields=['pk',],
    attrs={
        'data-autocomplete-minimum-characters': 2,
    },
    widget_attrs={
        'data-widget-maximum-values': 4,
        'class': 'modern-style',
    },
)