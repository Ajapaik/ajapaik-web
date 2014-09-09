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
		city_name = request.POST.get("Pildistamise koht") or request.POST.get("S\xc3\xbc\xc5\xbeee nimetus") or request.POST.get("place") or "Ajapaik"
		try:
			city = City.objects.filter(name=city_name)[:1].get()
		except ObjectDoesNotExist:
			city = Source(name=city_name)
			city.save()
		description1 = request.POST.get("Kirjeldus").strip()
		description2 = request.POST.get("title").strip()
		photo_data = {
			"source": source.__dict__,
			"city": city.__dict__,
			"source_key": request.POST.get("number"),
			"source_url": request.POST.get("url"),
			"date_text": request.POST.get('Pildistamise aeg') or request.POST.get('date'),
			"description": '; '.join([description1, description2])
		}
		serializer = self.serializer_class(data=photo_data)
		if serializer.is_valid():
			return HttpResponse("VALID")
		else:
			return HttpResponse(serializer.errors)