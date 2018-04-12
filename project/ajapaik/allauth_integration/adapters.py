from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .utils import move_user_data


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super(CustomSocialAccountAdapter, self).save_user(
            request, sociallogin, form
        )
        old_user = getattr(request, 'dummy_user', None)
        if old_user is not None:
            move_user_data(old_user=old_user, new_user=user)
            old_user.is_active = False
            old_user.save()
        return user
