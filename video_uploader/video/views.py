from video_uploader.video.serializers import VideoSerializer
from video_uploader.video.models import Video
from rest_framework import viewsets

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by('-uploaded_at')
    serializer_class = VideoSerializer
