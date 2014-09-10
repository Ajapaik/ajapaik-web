from models import Photo
from rest_framework import serializers

class PhotoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Photo
		fields = ('image', 'date', 'description', 'source_key', 'source_url', 'source', 'city')