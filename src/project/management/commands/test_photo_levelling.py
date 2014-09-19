from django.core.management.base import BaseCommand
from project.models import Photo, GeoTag, Skip

class Command(BaseCommand):
	help = "For testing photo difficulty levels"

	def handle(self,*args,**options):
		output_buf = ["id\tdescription\tconfidence\tgeotags\tskips\tratio\tlevel"]
		for photo in Photo.objects.all():
			photo_geotags = GeoTag.objects.filter(photo_id=photo.id).count()
			photo_skips = Skip.objects.filter(photo_id=photo.id).count()
			if photo_skips == 0:
				output_buf.append("\t".join([str(photo.id), photo.description.encode('utf-8'), str(photo.confidence), str(photo_geotags), "0", "No skips", "1"]))
			else:
				ratio = float(photo_geotags) / float(photo_skips)
				if ratio > 1.2:
					level = "1"
				elif 1.2 >= ratio > 0.8:
					level = "2"
				else:
					level = "3"
				output_buf.append("\t".join([str(photo.id), photo.description.encode('utf-8'), str(photo.confidence), str(photo_geotags), str(photo_skips), str(ratio), level]))
		f = open("output.txt", "w")
		f.write("\n".join(output_buf))
		f.close()