from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _, get_language_info

from ajapaik.ajapaik.models import Profile


class ChangeDisplayNameForm(forms.Form):
    display_name = forms.CharField()

    def clean(self):
        super(ChangeDisplayNameForm, self).clean()
        if self.cleaned_data.get('display_name') is None:
            self.errors['display_name'] = [_('Please specify what would you like your display name to be')]


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('preferred_language', 'newsletter_consent')
        languages = settings.LANGUAGES
        translated_languages = []
        for language in languages:
            li = get_language_info(language[0])
            translated_languages.append((language[0], (li['name_local'].capitalize())))
        labels = {
            'preferred_language': _('My preferred language is'),
            'newsletter_consent': _('I wish to receive the newsletter')
        }
        widgets = {
            'preferred_language': forms.Select(choices=translated_languages),
            'newsletter_consent': forms.Select(choices=[(True, _('Yes')), (False, _('No'))]),
        }

    def clean(self):
        super(UserSettingsForm, self).clean()
        if not self.cleaned_data.get('preferred_language'):
            self.errors['preferred_language'] = [_('Please specify your prefered language')]
        if self.cleaned_data.get('newsletter_consent') is None:
            self.errors['newsletter_consent'] = [_('Please specify whether you would like to receive the newsletter')]
