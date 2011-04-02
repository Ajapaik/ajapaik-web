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
	for row in GeoTag.objects.filter(user=user_id,
								is_correct__isnull=False). \
				values('is_correct').annotate(count=Count('pk')):
		total_tries+=row['count']
		if row['is_correct']:
			correct_tries+=row['count']

	if not correct_tries:
		return 0

	return (1-0.9**correct_tries) * \
						correct_tries / float(total_tries)

def get_next_photos_to_geotag(user_id,nr_of_photos=5):

	#!!! use trustworthiness to select desired level

	trustworthiness=calc_trustworthiness(user_id)

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

	unknown_photos_to_get=0
	if trustworthiness > 0.2:
		unknown_photos_to_get= \
				int(nr_of_photos * (0.3+5*trustworthiness))
	unknown_photos_to_get=max(unknown_photos_to_get,
								nr_of_photos-len(known_photos))

	unknown_photos=set()

	if unknown_photos_to_get:
		photo_ids_with_few_guesses=frozenset(
					GeoTag.objects.values('photo_id'). \
					annotate(nr_of_geotags=Count('id')). \
					filter(nr_of_geotags__lte=10). \
					values_list('photo_id',flat=True)) - forbidden_photo_ids
		if photo_ids_with_few_guesses:
			unknown_photos.update(Photo.objects. \
						filter(confidence__lt=0.3,
									pk__in=photo_ids_with_few_guesses). \
						extra(**extra_args). \
						order_by('final_level')[:unknown_photos_to_get])

		if len(unknown_photos) < unknown_photos_to_get:
			unknown_photos.update(Photo.objects.exclude(
									pk__in=forbidden_photo_ids). \
						filter(confidence__lt=0.3). \
						extra(**extra_args). \
						order_by('final_level')[:(unknown_photos_to_get- \
										len(unknown_photos))])

	if len(unknown_photos.union(known_photos)) < nr_of_photos:
		unknown_photos.update(Photo.objects. \
					extra(**extra_args). \
					order_by('?')[:unknown_photos_to_get])

	photos=random.sample(list(unknown_photos.union(known_photos)),
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

def submit_guess(user,photo_id,lon=None,lat=None,
						type=GeoTag.MAP,hint_used=False):
	p=Photo.objects.get(pk=photo_id)

	is_correct=None
	this_guess_score=0

	if lon is not None and lat is not None:
		trustworthiness=calc_trustworthiness(user.pk)
		this_guess_score=max(20,int(300*trustworthiness))

		if p.confidence >= 0.3:
			error_in_meters=Photo.distance_in_meters(
							p.lon,p.lat,float(lon),float(lat))
			this_guess_score=int(130*max(0,min(1,(1-
						(error_in_meters-15)/float(94-15)))))
			is_correct=(this_guess_score > 0)

		if hint_used:
			this_guess_score/=3

		GeoTag(user=user,photo_id=p.id,type=type,
						lat=float(lat),lon=float(lon),
						is_correct=is_correct,
						score=this_guess_score,
						trustworthiness=trustworthiness).save()
	else:
		Guess(user=user,photo_id=p.id).save()

	p.set_calculated_fields()
	p.save()

	user.set_calculated_fields()
	user.save()

	return is_correct,this_guess_score,user.score

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
