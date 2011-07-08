import re,csv,hashlib,os.path,shutil
from django.core.management.base import BaseCommand,CommandError
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
		for row in csv.reader(open(csv_filename,'rb')):
			if not header_row:
				header_row=row
				continue
			row=dict(zip(header_row,row))
			photos_metadata[(row.get('Inv nr') or row['Alanr']).lower()]=row

		for input_fname in args:
			source_id=os.path.basename(input_fname)
			if source_id.startswith(filename_prefix_to_skip):
				source_id=source_id[len(filename_prefix_to_skip):]
			source_id,_,fname_extension=source_id.rpartition('.')

			metadata=photos_metadata.get(source_id.lower())
			if not metadata:
				print >>self.stderr,'Error: no metadata found for ' + input_fname
				continue

			fname='uploads/' + hashlib.md5(input_fname).hexdigest() + '.' + \
														fname_extension
			shutil.copyfile(input_fname,'/var/garage/' + fname)

			description='; '.join(filter(None,[metadata[key].strip() \
										for key in ('Kirjeldus','')]))

			p=Photo(date_text=metadata['Pildistamise aeg'],
					description=description,
					source_key=source_id)
			p.image.name=fname
			p.save()
			print >>self.stdout, source_id,description,metadata['Pildistamise aeg']
