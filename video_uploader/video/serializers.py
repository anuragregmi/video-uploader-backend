from rest_framework import serializers

from video_uploader.video.models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"
        read_only_fields = ('converted_path',)
