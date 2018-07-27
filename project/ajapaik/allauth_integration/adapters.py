from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User

from .utils import move_user_data


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = super(CustomSocialAccountAdapter, self).populate_user(
            request, sociallogin, data
        )
        dummy_user = getattr(request, 'dummy_user', None)
        # We need this workaround with dummy_user_id in newly created user
        # because in case FB registration we can have FB account without email
        # or this email already occupied so allauth asking for email. But
        # allauth already logout user so middleware can't determinate dummy
        # user.
        if dummy_user is not None:
            user.dummy_user_id = dummy_user.id
        return user

    def save_user(self, request, sociallogin, form=None):
        dummy_user_id = getattr(sociallogin.user, 'dummy_user_id', None)
        user = super(CustomSocialAccountAdapter, self).save_user(
            request, sociallogin, form
        )
        old_user = None
        if dummy_user_id is not None:
            old_user = User.objects.filter(id=dummy_user_id).first()
        if old_user is not None:
            move_user_data(old_user=old_user, new_user=user)
            old_user.is_active = False
            old_user.save()
        return user
