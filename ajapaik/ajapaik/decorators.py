from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

try:
    # Optional import: only used to detect that the user has linked a social account
    from allauth.socialaccount.models import SocialAccount  # type: ignore
except Exception:  # pragma: no cover - allauth always installed in this project
    SocialAccount = None  # type: ignore


def _is_registered_user(user):
    """Return True only for authenticated, non-anonymous (non-bot/session) users.

    Our custom AuthBackend (ajapaik.ajapaik.user_middleware.AuthBackend) auto-creates
    pseudo users for anonymous sessions and bots. These users have usernames that
    start with an underscore (e.g., "_session_<...>") or with the pattern "_bot_".

    Consider the user registered when:
    - user is authenticated AND username does not start with '_' (typical real users), OR
    - user is authenticated AND has any linked SocialAccount (defensive: in case
      some real users happen to have usernames starting with '_').
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False

    username = getattr(user, "username", "") or ""
    if username and not username.startswith("_"):
        return True

    # Fallback: treat users with a social account as registered even if
    # the username happens to start with an underscore for historical reasons.
    if SocialAccount is not None:
        try:
            return SocialAccount.objects.filter(user_id=getattr(user, "id", None)).exists()
        except Exception:
            # If DB is not reachable for some reason, fall back to the strict rule
            return False

    return False


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
