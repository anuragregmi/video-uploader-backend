from video_uploader.video.views import VideoViewSet
from rest_framework.routers import DefaultRouter

app_name = "video"

router: DefaultRouter = DefaultRouter()


router.register('', VideoViewSet, basename="video")

urlpatterns = router.urls
