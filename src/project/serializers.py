from models import Photo, City, Profile, Device, Source
from rest_framework import serializers

class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ("id", "camera_make", "camera_model", "lens_make", "lens_model", "software")

class SourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Source
        fields = ("id", "name", "created", "modified", "description")

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "username", "first_name", "last_name", "email", "is_staff", "is_active", "is_superuser", "last_login", "date_joined", "fb_name", "fb_link", "fb_id", "fb_token", "google_plus_id", "google_plus_link", "google_plus_name",
        "google_plus_token", "google_plus_picture", "avatar_url", "modified", "score", "score_rephoto")

class CitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'lat', 'lon')

class PhotoSerializer(serializers.HyperlinkedModelSerializer):
    city = CitySerializer(many=True)
    profile = ProfileSerializer

    class Meta:
        model = Photo
        fields = ('id', 'image', 'image_unscaled', 'date', 'date_text', 'description', 'user', 'level', 'guess_level',
        'lat', 'lon', 'bounding_circle_radius', 'confidence', 'source_key', 'source_url', 'source', 'device', 'city',
        'rephoto_of', 'created', 'modified', 'cam_scale_factor', 'cam_yaw', 'cam_pitch', 'cam_roll')