from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAdminUser
from models import Photo, Source, City
from project.serializers import PhotoSerializer, CitySerializer

class PhotoViewSet(viewsets.ModelViewSet):
	queryset = Photo.objects.all()
	serializer_class = PhotoSerializer

	def create(self, request, *args, **kwargs):
		try:
			Photo.objects.filter(source_key=request.POST.get("number"))[:1].get()
			return HttpResponse("Duplicate", status=400)
		except:
			pass
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
			"description": "; ".join(filter(None,[request.POST[key].strip() for key in ("title", "description") if key in request.POST]))
		}
		serializer = self.serializer_class(data=photo_data, files=request.FILES)
		if serializer.is_valid():
			serializer.save()
			return HttpResponse("OK", status=200)
		else:
			return HttpResponse(serializer.errors, status=400)

class CityViewSet(viewsets.ModelViewSet):
	queryset = City.objects.all()
	serializer_class = CitySerializer

def get_photo_info_by_source_keys(request):
	key_array = request.GET.getlist("source_keys[]")
	photos_with_same_source_keys = Photo.objects.filter(source_key__in=key_array)
	ret = []
	for existing_photo in photos_with_same_source_keys:
		ret.append({"source_key": existing_photo.source_key, "azimuth": existing_photo.azimuth, "lon": existing_photo.lon, "lat": existing_photo.lat, "confidence": existing_photo.confidence})
	return HttpResponse(ret, mimetype="application/json")

class GetCreateCities(generics.ListCreateAPIView):
	model = City
	serializer_class = CitySerializer
	permission_classes = (IsAdminUser,)

class PhotoListCreate(generics.ListCreateAPIView):
	model = Photo
	serializer_class = PhotoSerializer
	permission_classes = (IsAdminUser,)

	@csrf_exempt
	def post(self, request, *args, **kwargs):
		pass

	def get(self, request, *args, **kwargs):
		return "asd"