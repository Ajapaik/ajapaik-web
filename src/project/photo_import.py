import time

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication
from models import Photo, Source, City
from json import loads, dumps
from project.serializers import PhotoSerializer

def check_for_duplicate_source_keys(request):
	# Returns photo source_keys that are already in the database
	id_array = loads(request.POST.get("source_keys_json"))
	photos_with_same_source_keys = Photo.objects.filter(source_key__in=id_array)
	ret = []
	for existing_photo in photos_with_same_source_keys:
		ret.append(existing_photo.source_key)
	return HttpResponse(dumps(ret), mimetype="application/json")

class PostNewHistoricPhoto(generics.CreateAPIView):
	serializer_class = PhotoSerializer
	permission_classes = (IsAdminUser,)

	# TODO: Currently pissing on security and ignoring CSRF, since passing along the cookie in our use case makes things
	# TODO: way more uncomfortable, implementing token authentication may make sense when we have more time, right now
	# TODO: we may as well accept the risk that some evil genius will bait one of the admins into uploading crappy historic photos (e.g. so what?)
	@csrf_exempt
	@authentication_classes(SessionAuthentication)
	def post(self, request, *args, **kwargs):
		# TODO: This looks really disgusting code-brevity wise
		source_description = request.POST.get("institution") or "Ajapaik"
		try:
			source = Source.objects.filter(description=source_description)[:1].get()
		except ObjectDoesNotExist:
			source = Source(name=source_description, description=source_description)
			source.save()
		city_name = request.POST.get("place") or "Ajapaik"
		try:
			city = City.objects.filter(name=city_name)[:1].get()
		except ObjectDoesNotExist:
			city = City(name=city_name)
			city.save()
		photo_data = {
			"source": source.id,
			"city": city.id,
			"source_key": request.POST.get("number"),
			"source_url": request.POST.get("url"),
			"date_text": request.POST.get("date"),
			"description": "; ".join(filter(None,[request.POST[key].strip() for key in ("description","title") if key in request.POST]))
		}
		serializer = self.serializer_class(data=photo_data, files=request.FILES)
		if serializer.is_valid():
			serializer.save()
			return HttpResponse("OK", status=200)
		else:
			return HttpResponse(serializer.errors, status=400)