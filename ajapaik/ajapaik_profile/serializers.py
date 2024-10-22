from rest_framework import serializers

from ajapaik.ajapaik.models import Profile


class ProfileLinkSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_display_name')
    profile_url = serializers.CharField(source='get_profile_url')

    class Meta:
        model = Profile
        fields = (
            'name', 'profile_url'
        )
