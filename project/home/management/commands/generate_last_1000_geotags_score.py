from django.core.management.base import BaseCommand
from project.models import Profile, GeoTag


class Command(BaseCommand):
	help = "Recalculates scores taking only the last 1000 geotags into account"

	def handle(self, *args, **options):
		last_1000_geotag_ids = GeoTag.objects.order_by("-created")[:1000].values_list("id", flat=True)
		for p in Profile.objects.all():
			score = 0
			for g in p.geotags.all():
				if g.id in last_1000_geotag_ids:
					score += g.score
			p.score_last_1000_geotags = score
			p.save()