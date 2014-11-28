from django.core.management.base import BaseCommand
from project.models import Photo

class Command(BaseCommand):
	help = "Will run set_calculated_fields for every photo"

	def handle(self,*args,**options):
		for photo in Photo.objects.all():
			photo.set_calculated_fields()
			photo.save()