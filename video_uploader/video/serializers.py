from rest_framework import serializers

from video_uploader.video.models import Video

class VideoSerializer(serializers.ModelSerializer):
    file_name = serializers.ReadOnlyField(source='raw_file.name')

    class Meta:
        model = Video
        exclude = ('transcoder_job_id', )
        read_only_fields = ('converted_path', 'outputs', 'thumbnail', 'transcode_status')
