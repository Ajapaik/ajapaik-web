from django.core.management.base import BaseCommand
from project.models import Profile


class Command(BaseCommand):
	help = "Recalculates scores taking only the last 1000 geotags into account"

	def handle(self, *args, **options):
		for p in Profile.objects.all():
			p.set_calculated_fields()
			p.save()
			print p.id