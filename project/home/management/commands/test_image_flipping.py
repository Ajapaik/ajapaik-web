from django.core.management.base import BaseCommand
from project.home.models import Photo

class Command(BaseCommand):
	help = "For testing horizontal flip on images"
	args = "photo_id"

	def handle(self,*args,**options):
		photo_id = args[0]
		photo = Photo.objects.filter(id=photo_id)[:1].get()
		photo.flip_horizontal()