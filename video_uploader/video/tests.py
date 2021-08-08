from unittest.mock import patch
from tempfile import NamedTemporaryFile

from django.urls import reverse
from django.conf import settings
from django.core.files import File
from django_q.models import Schedule
from rest_framework.test import APITestCase

from video_uploader.users.test.factories import UserFactory
from video_uploader.video.models import Video
from video_uploader.video import tasks

class VideoSaveTestCase(APITestCase):

    def setUp(self) -> None:
        super().setUp()

        self.user = UserFactory()
        self.client.force_login(self.user)

    def get_video_instance(self) -> Video:
        with NamedTemporaryFile(suffix='video.mp4') as video_file:
            video_file.write(b'Some content that doesnot matter')
            video_file.seek(0)

            with patch('video_uploader.video.tasks.post_save_video', return_value=None):
                video: Video = Video()
                video.raw_file.save('video.mp4', File(video_file), save=True)

        return video

    def test_creating_video_calls_post_save_video(self) -> None:
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

    def test_post_save_video(self) -> None:
        video: Video = self.get_video_instance()

        with patch(
            'video_uploader.video.utils.upload_file', return_value=None
        ) as upload_file, patch(
            'video_uploader.video.utils.create_transcode_job', return_value='123456'
        ) as create_job, patch(
            'video_uploader.video.tasks.watch_transcode_job', return_value=None
        ) as watch_transcode_job:
            tasks.post_save_video(video)

            upload_file.assert_called_once_with(
                video.raw_file,
                settings.INPUT_BUCKET_NAME,
                video.raw_file.name
            )

            create_job.assert_called_once_with(
                video.raw_file.name
            )

            # make sure video has transcoder_job_id attribute set
            self.assertEqual(video.transcoder_job_id, '123456')

            watch_transcode_job.assert_called_once_with(video)

    def test_watch_transcode_job_returning_processing(self) -> None:
        video: Video = self.get_video_instance()
        video.transcoder_job_id = '123456'
        video.save()

        with patch(
            'video_uploader.video.utils.check_job_status', return_value='Processing'
        ) as check_job_status, patch(
            'video_uploader.video.utils.extract_outputs', return_value={}
        ) as extract_outputs, patch(
            'video_uploader.video.tasks.watch_transcode_job_given_video_id', return_value=None
        ):
            tasks.watch_transcode_job(video)

            check_job_status.assert_called_once_with(video.transcoder_job_id)
            extract_outputs.assert_not_called()

            self.assertEqual(video.transcode_status, 'Processing')

            self.assertTrue(
                Schedule.objects.filter(
                    func='video_uploader.video.tasks.watch_transcode_job_given_video_id',
                    repeats=1,
                    args=f'({video.id},)'
                ).exists()
            )

    def test_watch_transcode_job_returning_error(self) -> None:
        video: Video = self.get_video_instance()
        video.transcoder_job_id = '123456'
        video.save()

        with patch(
            'video_uploader.video.utils.check_job_status', return_value='Error'
        ) as check_job_status, patch(
            'video_uploader.video.utils.extract_outputs', return_value={}
        ) as extract_outputs, patch(
            'video_uploader.video.tasks.watch_transcode_job_given_video_id', return_value=None
        ):
            tasks.watch_transcode_job(video)

            check_job_status.assert_called_once_with(video.transcoder_job_id)
            extract_outputs.assert_not_called()

            self.assertEqual(video.transcode_status, 'Error')

            self.assertFalse(
                Schedule.objects.filter(
                    func='video_uploader.video.tasks.watch_transcode_job_given_video_id'
                ).exists()
            )

    def test_watch_transcode_job_returning_complete(self) -> None:
        video: Video = self.get_video_instance()
        video.transcoder_job_id = '123456'
        video.save()

        sample_output: dict = {
            "outputs": [{
                "playlist": "playlist_url",
                "thumbnail": "thumbnail_url",
                "display": "display_name"
            }],
            "thumbnail": "thumbnail_url"
        }

        with patch(
            'video_uploader.video.utils.check_job_status', return_value='Complete'
        ) as check_job_status, patch(
            'video_uploader.video.utils.extract_outputs', return_value=sample_output
        ) as extract_outputs, patch(
            'video_uploader.video.tasks.watch_transcode_job_given_video_id', return_value=None
        ):
            tasks.watch_transcode_job(video)

            check_job_status.assert_called_once_with(video.transcoder_job_id)
            extract_outputs.assert_called_once_with(video.raw_file.name)

            self.assertEqual(video.transcode_status, 'Complete')
            self.assertEqual(video.outputs, sample_output['outputs'])
            self.assertEqual(video.thumbnail, sample_output['thumbnail'])

            self.assertFalse(
                Schedule.objects.filter(
                    func='video_uploader.video.tasks.watch_transcode_job_given_video_id'
                ).exists()
            )

    def test_calling_watch_transcode_job_without_job_id(self) -> None:
        video: Video = self.get_video_instance()
        with patch(
            'video_uploader.video.utils.check_job_status', return_value='Error'
        ), patch(
            'video_uploader.video.utils.extract_outputs', return_value={}
        ), patch(
            'video_uploader.video.tasks.watch_transcode_job_given_video_id', return_value=None
        ):
            self.assertRaises(AssertionError, tasks.watch_transcode_job, video)

    def test_watch_transcode_job_given_video_id(self) -> None:
        video: Video = self.get_video_instance()
        with patch(
            'video_uploader.video.tasks.watch_transcode_job', return_value='Complete'
        ) as watch_transcode_job:

            tasks.watch_transcode_job_given_video_id(video.id)
            watch_transcode_job.assert_called_once_with(video)
