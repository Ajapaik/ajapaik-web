from project.models import *
from django.db.models import *
from sorl.thumbnail import get_thumbnail
import random

def _make_thumbnail(photo,size):
	image=get_thumbnail(photo.image,size)
	return {'url':image.url,
			'size':[image.width,image.height]}
 
def calc_trustworthiness(user_id):
	total_tries=0
	correct_tries=0
	for row in GeoTag.objects.filter(user=user.pk,
								is_correct__isnull=False). \
				values('is_correct').annotate(count=Count('pk')):
		total_tries+=row['count']
		if row['is_correct']:
			correct_tries+=row['count']

	if not total_tries:
		return 0

	return (1-0.9**total_tries) * \
						correct_tries / float(total_tries)

def get_next_photos_to_geotag(user_id,nr_of_photos=5):

	#!!! use trustworthiness

	extra_args={'select': {'final_level':
			"(case when level > 0 then level else " + \
							"coalesce(guess_level,1) end)"},
				'where': ['rephoto_of_id IS NULL']}

	forbidden_photo_ids=frozenset([g.photo_id \
			for g in Guess.objects.filter(user=user_id,
				created__gte= \
				datetime.datetime.now()-datetime.timedelta(1))] + \
			list(GeoTag.objects.filter(user=user_id). \
							values_list('photo_id',flat=True)))
	known_photos=list(Photo.objects.exclude(
								pk__in=forbidden_photo_ids). \
					filter(confidence__gte=0.3). \
					extra(**extra_args). \
					order_by('final_level')[:nr_of_photos])
	unknown_photos=list(Photo.objects.exclude(
								pk__in=forbidden_photo_ids). \
					filter(confidence=0,pk__in= \
							GeoTag.objects.values_list(
									'photo_id',flat=True)). \
					extra(**extra_args). \
					order_by('final_level')[:nr_of_photos])
	if not unknown_photos:
		unknown_photos=list(Photo.objects. \
				exclude(pk__in=GeoTag.objects.values_list(
									'photo_id',flat=True)). \
				extra(**extra_args). \
				annotate(skips_count=Count('guess')). \
				order_by('final_level','skips_count') \
											[:nr_of_photos])

	photos=random.sample(list(set(known_photos+unknown_photos)),
						nr_of_photos)

	data=[]
	for p in photos:
		data.append({'id':p.id,
					'description':p.description,
					'date_text':p.date_text,
					'source_key':p.source_key,
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

def get_total_score(user_id):
	return GeoTag.objects.filter(user=user_id).aggregate(
				total_score=Sum('score'))['total_score'] or 0

def submit_guess(user,photo_id,lon=None,lat=None,
											type=GeoTag.MAP):
	p=Photo.objects.get(pk=photo_id)

	scoring_table={None:10,True:100}

	is_correct=None
	this_guess_score=scoring_table.get(is_correct,0)

	if lon is not None and lat is not None:
		if p.confidence >= 0.3:
			is_correct=(Photo.distance_in_meters(p.lon,p.lat,
								float(lon),float(lat)) < 100)
			this_guess_score=scoring_table.get(is_correct,0)

		GeoTag(user=user,photo_id=p.id,type=type,
						lat=float(lat),lon=float(lon),
						is_correct=is_correct,
						score=this_guess_score).save()
	else:
		Guess(user=user,photo_id=p.id).save()

	p.set_calculated_fields()
	p.save()

	return is_correct,this_guess_score,get_total_score(user.pk)

def get_geotagged_photos():
	rephotographed_ids=frozenset(Photo.objects.filter(
			rephoto_of__isnull=False).values_list(
									'rephoto_of',flat=True))
	data=[]
	for p in Photo.objects.filter(confidence__gte=0.3,
						lat__isnull=False,lon__isnull=False,
						rephoto_of__isnull=True):
		data.append((p.id,p.lon,p.lat,p.id in rephotographed_ids))
	return data
