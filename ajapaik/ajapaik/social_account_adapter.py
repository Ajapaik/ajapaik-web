from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        return reverse('user_settings')

    def save_user(self, request, user, form, commit=True):
        user = super(MySocialAccountAdapter, self).save_user(request, user, form)
        social_account = SocialAccount.objects.filter(user=user).first()
        profile = user.profile

        if not social_account:
            return

        if social_account.extra_data.get('username'):
            profile.display_name = social_account.extra_data.get('username')
        elif profile.first_name and profile.last_name:
            profile.display_name = f'{profile.first_name} {profile.last_name}'
        elif profile.first_name or profile.last_name:
            profile.display_name = profile.first_name if profile.first_name else profile.last_name

        if social_account.provider == 'google':
            profile.google_plus_id = social_account.uid
            if social_account.extra_data.get('picture'):
                profile.google_plus_picture = social_account.extra_data.get('picture')
            if social_account.extra_data.get('email'):
                profile.google_plus_email = social_account.extra_data.get('email')

        if social_account.provider == 'facebook':
            profile.fb_id = social_account.uid
            if social_account.extra_data.get('email'):
                profile.fb_email = social_account.extra_data.get('email')
        profile.save()
