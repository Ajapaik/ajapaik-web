import re,csv,hashlib,os.path,shutil
from django.core.management.base import BaseCommand,CommandError
from django.core.exceptions import ObjectDoesNotExist
from project.models import *

class Command(BaseCommand):
	args='csv_filename filename_prefix_to_skip [filenames...]'
	help='Imports photos from image files and a metadata CSV file'

	def handle(self,*args,**options):
		args=list(args)
		csv_filename=args.pop(0)
		filename_prefix_to_skip=args.pop(0)

		photos_metadata=dict()
		header_row=None
		dialect = csv.Sniffer().sniff(open(csv_filename,'rb').read(1024), delimiters=";,")
		for row in csv.reader(open(csv_filename,'rb'), dialect):
		#for row in csv.reader(open(csv_filename,'rb'), delimiter=';'):
			if not header_row:
				header_row=row
				continue
			row=dict(zip(header_row,row))
			photos_metadata[(row.get('Inv nr') or row.get('Alanr') or row.get('image')).lower()]=row

		for input_fname in args:
			file_key=os.path.basename(input_fname)
			if file_key.startswith(filename_prefix_to_skip):
				file_key=file_key[len(filename_prefix_to_skip):]
			file_key,_,fname_extension=file_key.rpartition('.')

			metadata=photos_metadata.get(file_key.lower()) \
				or photos_metadata.get(file_key.lower()+ '.' + fname_extension)

			if not metadata:
				print >>self.stderr,'Error: no metadata found for ' + file_key
				continue

			fname='uploads/' + hashlib.md5(input_fname).hexdigest() + '.' + \
														fname_extension
			shutil.copyfile(input_fname,'/var/garage/' + fname)

			description='; '.join(filter(None,[metadata[key].strip() \
										for key in ('Kirjeldus','title') \
										if key in metadata]))

			city_name=metadata.get('Pildistamise koht') or metadata.get('S\xc3\xbc\xc5\xbeee nimetus') or metadata.get('place') or "Ajapaik"

			try:
				city=City.objects.get(name=city_name)
			except ObjectDoesNotExist:
				city=City(name=city_name)
				city.save()
			
			source_description=metadata.get('institution') or "Ajapaik"
			try:
				source=Source.objects.get(description=source_description)
			except ObjectDoesNotExist:
				source=Source(name=source_description,description=source_description)
				source.save()

			source_key=metadata.get('number') or file_key
			source_url=metadata.get('url')

			p=Photo(date_text=metadata.get('Pildistamise aeg') or metadata.get('date'),
					city=city,
					description=description,
					source=source,
					source_url=source_url,
					source_key=source_key)
			p.image.name=fname
			p.save()
			print >>self.stdout, file_key,description
