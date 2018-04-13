from allauth.account.signals import email_confirmed
from django.contrib.auth.models import User
from django.dispatch import receiver

from .utils import move_user_data


@receiver(email_confirmed)
def transfer_email_user_data(request, email_address, **kwargs):
    '''
    This slot move user data from old dummy user to newly email created user.
    '''
    # We listening for `email_confirmed` becose we need to move data in the
    # latest moment. Because user can do some action after registering user
    # and before email confirmation.
    old_user = getattr(request, 'dummy_user', None)
    if old_user is None or not old_user.is_active:
        # We haven't old_user so haven't source from which to move data.
        # Or we have inactive user maybe we already processed this user.
        return

    try:
        new_user = User.objects.get(emailaddress__email=email_address)
    except (User.DoesNotExist, User.MultipleObjectsReturned):
        return
    move_user_data(old_user=old_user, new_user=new_user)

    # We moved data and mark this user as inactive.
    old_user.is_active = False
    old_user.save()
