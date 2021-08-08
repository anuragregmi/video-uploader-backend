from unittest.mock import patch
from tempfile import NamedTemporaryFile
from video_uploader.video.models import Video

from django.urls import reverse
from rest_framework.test import APITestCase

from video_uploader.users.test.factories import UserFactory

class VideoSaveTestCase(APITestCase):

    def setUp(self) -> None:
        super().setUp()

        self.user = UserFactory()
        self.client.force_login(self.user)

    def test_creating_video_calls_post_save_video(self):
        """Test post_save_video is called while creating video"""

        with NamedTemporaryFile(suffix='video.mp4') as video_file:
            video_file.write(b'Some content that doesnot matter')
            video_file.seek(0)

            print("filename", video_file.name)

            data: dict = {
                "raw_file": video_file
            }
            url = reverse('video:video-list')
            with patch('video_uploader.video.tasks.post_save_video', return_value=None) as mocked:
                response = self.client.post(url, data)

                self.assertEqual(response.status_code, 201)

                video = Video.objects.get(id=response.data.get('id'))

                # assert post save is called with video instance
                mocked.assert_called_once_with(video)
