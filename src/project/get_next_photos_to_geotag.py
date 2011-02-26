from project.models import *
from django.db.models import *
from sorl.thumbnail import get_thumbnail
import random

def _make_thumbnail(photo,size):
	image=get_thumbnail(photo.image,size)
	return {'url':image.url,
			'size':[image.width,image.height]}
 
def get_next_photos_to_geotag(user_id,nr_of_photos=5):

	#!!! kui hea arvaja sa oled

	forbidden_photo_ids=frozenset([g.photo_id \
			for g in Guess.objects.filter(user=user_id,
				created__gte= \
				datetime.datetime.now()-datetime.timedelta(1))] + \
			list(GeoTag.objects.filter(user=user_id). \
							values_list('photo_id',flat=True)))
	known_photos=list(Photo.objects.exclude(
								pk__in=forbidden_photo_ids). \
					filter(confidence__gte=0.3)[:nr_of_photos])
	unknown_photos=list(Photo.objects.exclude(
								pk__in=forbidden_photo_ids). \
					filter(confidence=0,pk__in= \
						GeoTag.objects.values_list(
									'photo_id',flat=True)) \
												[:nr_of_photos])
	if not unknown_photos:
		unknown_photos=list(Photo.objects.exclude(pk__in= \
						GeoTag.objects.values_list(
									'photo_id',flat=True)). \
				annotate(skips_count=Count('guess')). \
				order_by('skips_count')[:nr_of_photos])

	photos=random.sample(list(set(known_photos+unknown_photos)),
						nr_of_photos)

	data=[]
	for p in photos:
		data.append({'id':p.id,
					'big':_make_thumbnail(p,'510x375'),
					'small':_make_thumbnail(p,'160x160')})
	return data

	# photod mille kohta saab anda feedbacki, ja mida ma
	#						pole viimase 24h jooksul arvanud
	# photod millel on geotage, aga mille kohta ei saa veel
	#			anda feedbacki, ja mida ma pole viimase 24h
	#			jooksul arvanud; voi kui neid pole, siis
	#			photod millel pole geotage ja mida on koige
	#										vahem skipitud

def submit_guess(user,photo_id,lon=None,lat=None,
											type=GeoTag.MAP):
	p=Photo.objects.get(pk=photo_id)

	is_correct=None
	if lon is not None and lat is not None:
		g=GeoTag(user=user,photo_id=p.id,type=type,
						lat=float(lat),lon=float(lon))
		if p.confidence >= 0.3:
			is_correct=(Photo.distance_in_meters(p.lon,p.lat,
								float(lon),float(lat)) < 100)
			g.is_correct=is_correct
		g.save()
	else:
		Guess(user=user,photo_id=p.id).save()

	p.set_calculated_fields()
	p.save()

	return is_correct
