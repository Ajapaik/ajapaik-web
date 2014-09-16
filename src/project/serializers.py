from models import Photo, City
from rest_framework import serializers

class PhotoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Photo
		fields = ('image', 'date', 'description', 'source_key', 'source_url', 'source', 'city', 'lat', 'lon', 'azimuth', 'confidence', 'azimuth_confidence')

class CitySerializer(serializers.ModelSerializer):
	class Meta:
		model = City
		fields = ('name', 'lat', 'lon')