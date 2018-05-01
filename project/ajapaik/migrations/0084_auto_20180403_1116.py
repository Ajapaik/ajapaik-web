# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sys import stdout

from django.db import migrations, models
from django.contrib.sessions.backends.db import SessionStore


def migrate_sessions(apps, schema_editor):
    Session = apps.get_model('sessions', 'Session')

    all_sessions = list(Session.objects.all())
    sessions_count = len(all_sessions)
    old_auth_backend = 'project.ajapaik.user_middleware.AuthBackend'
    django_model_backend = 'django.contrib.auth.backends.ModelBackend'
    backend_session_key = '_auth_user_backend'

    stdout.write('\n')
    for number, session in enumerate(all_sessions, 1):
        stdout.write('\rProcessing session {number} of {count}.'
                     .format(number=number, count=sessions_count))
        stdout.flush()
        session_store = SessionStore(session_key=session.session_key)
        if backend_session_key not in session_store:
            continue
        if session_store[backend_session_key] == old_auth_backend:
            session_store[backend_session_key] = django_model_backend
            session_store.save()
    stdout.write('\n')


class Migration(migrations.Migration):

    dependencies = [
        ('ajapaik', '0083_auto_20180326_1111'),
        ('sessions', '0001_initial'),
    ]

    operations = [
         migrations.RunPython(migrate_sessions),
    ]
