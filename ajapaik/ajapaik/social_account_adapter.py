from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        return reverse('user_settings')

    def save_user(self, request, user, form, commit=True):
        user = super(MySocialAccountAdapter, self).save_user(request, user, form)
        social_account = SocialAccount.objects.filter(user=user).first()
        if social_account:
            if social_account.extra_data.get('username'):
                user.profile.display_name = social_account.extra_data.get('username')
            elif user.profile.first_name and user.profile.last_name:
                user.profile.display_name = '%s %s' % (user.profile.first_name, user.profile.last_name)
            elif user.profile.first_name:
                user.profile.display_name = user.profile.first_name
            elif user.profile.last_name:
                user.profile.display_name = user.profile.last_name

            if social_account.provider == 'google':
                user.profile.google_plus_id = social_account.uid
                if social_account.extra_data.get('picture'):
                    user.profile.google_plus_picture = social_account.extra_data.get('picture')
                if social_account.extra_data.get('email'):
                    user.profile.google_plus_email = social_account.extra_data.get('email')

            if social_account.provider == 'facebook':
                user.profile.fb_id = social_account.uid
                if social_account.extra_data.get('email'):
                    user.profile.fb_email = social_account.extra_data.get('email')
            user.profile.save()
