# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_users(apps, schema_editor):
    SocialAccount = apps.get_model('socialaccount', 'SocialAccount')
    EmailAddress = apps.get_model('account', 'EmailAddress')
    Profile = apps.get_model('ajapaik', 'Profile')
    RegistrationProfile = apps.get_model('registration', 'RegistrationProfile')
    User = apps.get_model('auth', 'User')


################################################################################
### Moving contribution data from duplicating social users to email registered
### user.
################################################################################
    # Users registerd with email.
    email_users = User.objects.filter(
        email__ne='', profile__fb_email=None, profile__google_plus_email=None
    )
    for email_user in email_users:
        duplicating_social_users = User.objects.filter(
            models.Q(profile__google_plus_email=email_user.email)
            | models.Q(profile__fb_email=email_user.email)
        )
        for social_user in duplicating_social_users:
            # Moving contribution data from social user to registered through email.
            email_user.profile.photos.add(*social_user.profile.photos.all())
            email_user.profile.albums.add(*social_user.profile.albums.all())
            email_user.profile.album_photo_links.add(*social_user.profile.album_photo_links.all())
            email_user.profile.datings.add(*social_user.profile.datings.all())
            email_user.profile.dating_confirmations.add(*social_user.profile.dating_confirmations.all())
            email_user.profile.difficulty_feedbacks.add(*social_user.profile.difficulty_feedbacks.all())
            email_user.profile.geotags.add(*social_user.profile.geotags.all())
            email_user.profile.points.add(*social_user.profile.points.all())
            email_user.profile.skips.add(*social_user.profile.skips.all())
            email_user.profile.likes.add(*social_user.profile.likes.all())
            email_user.profile.tour_groups.add(*social_user.profile.tour_groups.all())
            email_user.profile.owned_tours.add(*social_user.profile.owned_tours.all())
            email_user.profile.tour_rephotos.add(*social_user.profile.tour_rephotos.all())
            email_user.profile.tour_views.add(*social_user.profile.tour_views.all())

            # Freeing social user
            social_user.profile.photos.clear()
            social_user.profile.album_photo_links.clear()
            social_user.profile.datings.clear()
            social_user.profile.dating_confirmations.clear()
            social_user.profile.difficulty_feedbacks.clear()
            social_user.profile.geotags.clear()
            social_user.profile.points.clear()
            social_user.profile.skips.clear()
            social_user.profile.likes.clear()
            social_user.profile.tour_groups.clear()
            social_user.profile.owned_tours.clear()
            social_user.profile.tour_rephotos.clear()
            social_user.profile.tour_views.clear()

            social_user.is_active = False

            email_user.save()
            social_user.save()


################################################################################
### Creating social acconts.
################################################################################
    # Social network accounts migration.
    facebook_profiles = Profile.objects \
        .filter(fb_id__isnull=False, user__is_active=True) \
        .prefetch_related('user')

    google_profiles = Profile.objects \
        .filter(google_plus_id__isnull=False, user__is_active=True) \
        .prefetch_related('user')

    for profile in facebook_profiles:
        SocialAccount.objects.create(
            provider='facebook',
            uid=profile.fb_id,
            date_joined=profile.user.date_joined,
            last_login=profile.user.last_login,
            user=profile.user,
            extra_data={}
        )
        if not profile.user.email and profile.fb_email:
            profile.user.email = profile.fb_email
        if not profile.user.first_name and profile.first_name:
            profile.user.first_name = profile.first_name
        if not profile.user.last_name and profile.last_name:
            profile.user.last_name = profile.last_name
        email_exists = EmailAddress.objects \
            .filter(email=profile.fb_email) \
            .exists()
        # if profile.fb_email and not email_exists:
        if profile.fb_email:
            EmailAddress.objects.create(
                email=profile.fb_email,
                verified=False,
                primary=True,
                user=profile.user
            )

    for profile in google_profiles:
        SocialAccount.objects.create(
            provider='google',
            uid=profile.google_plus_id,
            date_joined=profile.user.date_joined,
            last_login=profile.user.last_login,
            user=profile.user,
            extra_data={}
        )
        if not profile.user.email and profile.google_plus_email:
            profile.user.email = profile.google_plus_email
        if not profile.user.first_name and profile.first_name:
            profile.user.first_name = profile.first_name
        if not profile.user.last_name and profile.last_name:
            profile.user.last_name = profile.last_name
        email_exists = EmailAddress.objects \
            .filter(email=profile.google_plus_email) \
            .exists()
        # if profile.google_plus_email and not email_exists:
        if profile.google_plus_email:
            EmailAddress.objects.create(
                email=profile.google_plus_email,
                verified=False,
                primary=True,
                user=profile.user
            )

    # E-mail registered accouts migration.
    old_profiles = RegistrationProfile.objects.all().prefetch_related('user')
    for profile in old_profiles:
        email = profile.user.email
        if not email:
            print('No email for user: {user_id} during email accounts '
                  'migration. Skipping...'.format(user_id=profile.user.id))
            continue
        try:
            email_address = EmailAddress.objects.get(email=email)
            email_address.verified = profile.activated
            if profile.user != email_address.user:
                print('Different users for email "{email}". Profile user ID '
                      '"{profile_user_id}" EmailAddress current user ID '
                      '{email_user_id}.'
                      .format(email=email,
                              profile_user_id=profile.user.id,
                              email_user_id=email_address.user.id))
            email_address.save()
        except EmailAddress.DoesNotExist:
            EmailAddress.objects.create(
                email=email,
                verified=profile.activated,
                primary=True,
                user=profile.user
            )

    # Users registered not with social network and not with 'register'
    # application. Possibly with 'createsuperuser' command.
    email_registered_users = User.objects.filter(
        email__ne='',
        profile__fb_id__isnull=True,
        profile__google_plus_id__isnull=True,
        registrationprofile__isnull=True,
        emailaddress__isnull=True
    )
    for user in email_registered_users:
        EmailAddress.objects.create(
                email=user.email,
                verified=True,
                primary=True,
                user=user
            )


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0080_auto_20180214_1055'),
        ('registration', '0004_supervisedregistrationprofile'),
        ('socialaccount', '0003_extra_data_default_dict'),
        ('account', '0002_email_max_length'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunPython(migrate_users),
    ]
