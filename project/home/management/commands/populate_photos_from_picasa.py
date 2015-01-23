import urllib,lxml.etree,re,csv,hashlib,os.path
from django.core.management.base import BaseCommand,CommandError
from project.models import *

class Command(BaseCommand):
	args='picasa_userid picasa_albumid picasa_authkey csv_filename'
	help='Imports photos from Picasa album and metadata CSV file'

	def handle(self,*args,**options):
		userid,albumid,authkey,csv_filename=args

		photos_metadata=dict()
		header_row=None
		dialect = csv.Sniffer().sniff(open(csv_filename,'rb').read(1024))
		for row in csv.reader(open(csv_filename,'rb'), dialect):
			if not header_row:
				header_row=row
				continue
			row=dict(zip(header_row,row))
			photos_metadata[(row.get('Inv nr') or row['Alanr']]=row

		url='http://picasaweb.google.com/data/feed/api/user/%s/album/%s?authkey=%s&kind=photo&start-index=%s&max-results=%s' % \
					(userid,albumid,authkey,1,10000)
		data=urllib.urlopen(url).read()
		doc=lxml.etree.XML(data)

		for node in doc.xpath('picasa:entry',
				namespaces={'picasa':'http://www.w3.org/2005/Atom'}):
			urls=node.xpath('media:group/media:content/@url',
					namespaces={'media':'http://search.yahoo.com/mrss/'})
			if not urls:
				print >>self.stderr,'Error: no URL for photo'
				continue

			url=urls[0]
			m=re.search(r'_([0-9]+)(\.*[a-z]*)_*$',url)
			if not m:
				print >>self.stderr,'Error: no source_key in URL ' + url
				continue

			source_key=m.group(1)

			fname='uploads/' + hashlib.md5(url).hexdigest() + \
													m.group(2)
			full_fname='/var/garage/' + fname
			if not os.path.exists(full_fname):
				urllib.urlretrieve(url,full_fname)

			metadata=photos_metadata.get(source_key)
			if not metadata:
				print >>self.stderr,'Error: no metadata found for URL ' + url
				continue

			description='; '.join(filter(None,[metadata[key].strip() \
						for key in ('Kirjeldus','')]))

			p=Photo(date_text=metadata['Pildistamise aeg'],
					description=description,
					source_id=1,
					source_key=source_key)
			p.image.name=fname
			p.save()
			print >>self.stdout, source_key,description,metadata['Pildistamise aeg']
