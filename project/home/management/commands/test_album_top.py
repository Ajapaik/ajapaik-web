from django.core.management.base import BaseCommand
from project.home.views import _get_album_leaderboard50


class Command(BaseCommand):
    help = "Test album leaderboard"
    args = "user_id, album_id"

    def handle(self, *args, **options):
        user_id = args[0]
        album_id = args[1]
        _get_album_leaderboard50(user_id, album_id)