import autocomplete_light.shortcuts as al

from project.ajapaik.models import Profile, Photo, Tour

al.register(Profile,
    search_fields=['user__first_name', 'user__last_name', 'user__email', 'fb_name', 'google_plus_name'],
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