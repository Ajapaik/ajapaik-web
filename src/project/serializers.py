from models import Photo, City, Profile, Device, Source
from django.contrib.auth.models import User as BaseUser
from rest_framework import serializers

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ("id", "camera_make", "camera_model", "lens_make", "lens_model", "software")

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ("id", "name", "description")

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ("id", "username", "first_name", "last_name", "email", "is_staff", "is_active", "is_superuser", "last_login", "date_joined")

class ProfileSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer(required=False)

    class Meta:
        model = Profile
        fields = ("user", "fb_id", "avatar_url", "fb_name", "fb_link", "score", "score_rephoto", "google_plus_name", "google_plus_link", "google_plus_id", "google_plus_picture")

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'lat', 'lon')

class PhotoSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(required=False)
    device = DeviceSerializer(required=False)
    source = SourceSerializer(required=False)
    city = CitySerializer(required=False)

    class Meta:
        model = Photo
        fields = ('id', 'image', 'image_unscaled', 'date', 'date_text', 'description', 'level', 'user', 'guess_level',
        'lat', 'lon', 'bounding_circle_radius', 'confidence', 'source_key', 'source_url', 'source', 'device', 'city',
        'rephoto_of', 'created', 'modified', 'cam_scale_factor', 'cam_yaw', 'cam_pitch', 'cam_roll')