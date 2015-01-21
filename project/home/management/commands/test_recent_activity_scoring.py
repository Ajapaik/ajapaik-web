from django.core.management.base import BaseCommand
from project.home.get_next_photos_to_geotag import calculate_recent_activity_scores

class Command(BaseCommand):
    help = "Test recent activity scoring"

    def handle(self, *args, **options):
        calculate_recent_activity_scores()