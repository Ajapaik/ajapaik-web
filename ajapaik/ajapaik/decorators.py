from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def _is_registered_user(user):
    """Return True only for authenticated, non-anonymous (non-bot/session) users.

    Our custom AuthBackend (ajapaik.ajapaik.user_middleware.AuthBackend) auto-creates
    pseudo users for anonymous sessions and bots. These users have usernames that
    start with an underscore (e.g., "_session_<...>") or with the pattern "_bot_".

    Real, registered users should therefore not have usernames starting with "_".
    """
    return bool(user and user.is_authenticated and not getattr(user, "username", "").startswith("_"))


def registered_login_required(function=None, redirect_field_name="next", login_url=None):
    """Decorator like django.contrib.auth.decorators.login_required but
    requiring a truly registered user, not just an auto-authenticated session.

    If the user fails the check, they are redirected to settings.LOGIN_URL with
    the usual "next" parameter preserved, so that after successful login they
    are returned to the originally requested URL.
    """
    actual_login_url = login_url or settings.LOGIN_URL
    decorator = user_passes_test(
        _is_registered_user,
        login_url=actual_login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return decorator(function)
    return decorator
