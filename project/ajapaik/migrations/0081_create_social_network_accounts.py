# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_users(apps, schema_editor):
    SocialAccount = apps.get_model('socialaccount', 'SocialAccount')
    EmailAddress = apps.get_model('account', 'EmailAddress')
    Profile = apps.get_model('ajapaik', 'Profile')
    RegistrationProfile = apps.get_model('registration', 'RegistrationProfile')
    User = apps.get_model('auth', 'User')

    # Social network accounts migration.
    facebook_profiles = Profile.objects.filter(fb_id__isnull=False) \
        .prefetch_related('user')

    google_profiles = Profile.objects.filter(google_plus_id__isnull=False) \
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
        if profile.fb_email and not email_exists:
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
        if profile.google_plus_email and not email_exists:
            EmailAddress.objects.create(
                email=profile.google_plus_email,
                verified=False,
                primary=True,
                user=profile.user
            )

    # E-mail registered accouts migration.
    old_profiles = RegistrationProfile.objects.all()
    for profile in old_profiles:
        email = profile.user.email
        if not email:
            print('No email for user: {user_id} during email accounts '
                  'migration. Skipping...'.format(profile.user.id))
        else:
            email_address = EmailAddress.objects \
                .filter(email=profile.user.email)
            if not email_address:
                EmailAddress.objects.create(
                    email=profile.user.email,
                    verified=profile.activated,
                    primary=True,
                    user=profile.user
                )
            else:
                if not email_address.user == profile.user:
                    print('EmailAddress with email "{email}" already exists '
                          'and belong to user with id {email_user_id}'
                          'But we try to process email that belongs to other '
                          'user(user id {other_user_id})'
                          .format(email=email_address.email,
                                  email_user_id=email_address.user.id,
                                  other_user_id=profile.user.id))
                else:
                    # Everything is ok. Email exists but it belong to the same
                    # user that pointed in RegistrationProfile.
                    pass

    # Users registered not with social network and not with 'register'
    # application. Possibly with 'createsuperuser' command.
    email_registered_users = User.objects.filter(
        email__ne='',
        profile__fb_id__isnull=True,
        profile__google_plus_id__isnull=True,
        registrationprofile__isnull=True
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
