from django.core.management.base import BaseCommand
from project.models import Photo, GeoTag, Skip

class Command(BaseCommand):
	help = "For testing photo difficulty levels"

	def handle(self,*args,**options):
		output_buf = []
		for photo in Photo.objects.all():
			photo_geotags = GeoTag.objects.filter(id=photo.id).count()
			photo_skips = Skip.objects.filter(id=photo.id).count()
			print photo_geotags
			print photo_skips
			print "asd"
			if photo_skips == 0:
				output_buf.append(";".join([str(photo.id), photo.description.encode('utf-8'), str(photo.confidence), "No skips", "1"]))
			else:
				ratio = photo_geotags / photo_skips
				if ratio > 1.2:
					level = "1"
				elif 1.2 >= ratio > 0.8:
					level = "2"
				else:
					level = "3"
				print ratio
				output_buf.append(";".join([str(photo.id), photo.description.encode('utf-8'), str(photo.confidence), str(ratio), level]))
		f = open("output.txt", "w")
		f.write("\n".join(output_buf))
		f.close()