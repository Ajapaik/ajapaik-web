from django.core.management.base import BaseCommand
from project.home.models import calc_trustworthiness


class Command(BaseCommand):
    help = "Test calc_trustworthiness"
    args = "user_id"

    def handle(self, *args, **options):
        user_id = args[0]
        print calc_trustworthiness(user_id)