import celery
from django.core import management

# TODO: Maybe use django-background-tasks?
@celery.task
def refresh_albums():
    try:
        management.call_command('refresh_albums', verbosity=0)
        return 'Albums refreshed'
    except Exception as e:
        print(e)

# TODO: Stats export
# TODO: DB backup?
# TODO: Vanalinnad update?
