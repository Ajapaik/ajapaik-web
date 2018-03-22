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
    profiles = Profile.objects.filter(
        models.Q(fb_id__isnull=False) | models.Q(google_plus_id__isnull=False)
    ) \
        .annotate(
            provider=models.Case(
                models.When(fb_id__isnull=False, then=models.Value('facebook')),
                models.When(google_plus_id__isnull=False, then=models.Value('google')),
                output_field=models.CharField()
            )
        ) \
        .annotate(
            social_user_id=models.Case(
                models.When(fb_id__isnull=False, then=models.F('fb_id')),
                models.When(google_plus_id__isnull=False, then=models.F('google_plus_id')),
                output_field=models.CharField()
            )
        )

    for profile in profiles:
        SocialAccount.objects.create(
            provider=profile.provider,
            uid=profile.social_user_id,
            date_joined=profile.user.date_joined,
            last_login=profile.user.last_login,
            user=profile.user,
            extra_data={}
        )

    # E-mail registered accouts migration.
    old_profiles = RegistrationProfile.objects.all()
    for profile in old_profiles:
        email = profile.user.email
        if not email:
            print('No email for user: {user_id} during email accounts '
                  'migration. Skipping...'.format(profile.user.id))
        else:
            EmailAddress.objects.create(
                email=profile.user.email,
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
