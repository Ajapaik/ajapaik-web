from models import Photo, City, Source, Album
from rest_framework import serializers

class PhotoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Photo
		fields = ('id', 'image', 'date_text', 'description', 'source_key', 'source_url', 'source', 'city', 'lat', 'lon', 'azimuth', 'confidence', 'azimuth_confidence')

class CitySerializer(serializers.ModelSerializer):
	class Meta:
		model = City
		fields = ('id', 'name', 'lat', 'lon')

class AlbumSerializer(serializers.ModelSerializer):
	class Meta:
		model = Album
		fields = ('id', 'name', 'slug', 'description', 'atype', 'profile_id', 'is_public', 'lat', 'lon')

class SourceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Source
		fields = ('id', 'name', 'description')