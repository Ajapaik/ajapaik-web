from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import email_confirmed, user_signed_up
from allauth.socialaccount.signals import pre_social_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from django.dispatch import receiver


def move_user_data(old_user, new_user):
    # Ajapaik specific data.
    new_user.profile.photos.add(*old_user.profile.photos.all())
    new_user.profile.albums.add(*old_user.profile.albums.all())
    new_user.profile.album_photo_links.add(*old_user.profile.album_photo_links.all())
    new_user.profile.datings.add(*old_user.profile.datings.all())
    new_user.profile.dating_confirmations.add(*old_user.profile.dating_confirmations.all())
    new_user.profile.difficulty_feedbacks.add(*old_user.profile.difficulty_feedbacks.all())
    new_user.profile.geotags.add(*old_user.profile.geotags.all())
    new_user.profile.points.add(*old_user.profile.points.all())
    new_user.profile.skips.add(*old_user.profile.skips.all())
    new_user.profile.likes.add(*old_user.profile.likes.all())
    new_user.profile.tour_groups.add(*old_user.profile.tour_groups.all())
    new_user.profile.owned_tours.add(*old_user.profile.owned_tours.all())
    new_user.profile.tour_rephotos.add(*old_user.profile.tour_rephotos.all())
    new_user.profile.tour_views.add(*old_user.profile.tour_views.all())

    # Other user data.
    new_user.comment_comments.add(*old_user.comment_comments.all())


@receiver(email_confirmed)
def transfer_email_user_data(request, email_address, **kwargs):
    '''
    This slot move user data from old dummy user to newly email created user.
    '''
    # We listening for `email_confirmed` becose we need to move data in the
    # latest moment. Because user can do some action after registering user
    # and before email confirmation.
    old_user = request.user
    if not old_user.is_authenticated() and not old_user.is_dummy:
        # User is anonymous so no data to move. Or user is normal user(not
        # dummy) so data moving is not required.
        return

    try:
        new_user = User.objects.get(emailaddress__email=email_address)
    except (User.DoesNotExist, User.MultipleObjectsReturned):
        return

    move_user_data(old_user=old_user, new_user=new_user)


@receiver(user_signed_up)
def transfer_social_user_data(request, user, **kwargs):
    '''
    This slot move user data from old dummy user to newly social created user.
    '''
    # We need to be shure that we process social user because for sutable
    # listening for `email_confirmed` signal.
    is_social_user_registration = 'sociallogin' in kwargs
    if not is_social_user_registration:
        # Nothing to do here. We should move email user data in the latest
        # moment. Because user can do some actions after registration(period
        # after registration but before email confirmation) new user.
        return

    old_user = request.user
    if not old_user.is_authenticated() and not old_user.is_dummy:
        # User is anonymous so no data to move. Or user is normal user(not
        # dummy) so data moving is not required.
        return

    move_user_data(old_user=old_user, new_user=user)
