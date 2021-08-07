from django.conf import settings

from django_q.tasks import async_task


from video_uploader.video.models import Video
from video_uploader.video.utils import create_transcode_job, upload_file


def post_save_video(video: Video) -> None:
    """Function to be called after createing Video Instance
    
    Uploads file to INPUT_BUCKET and schedules transcode job

    Args:
        video: Video Instance
    """
    upload_file(video.raw_file, settings.INPUT_BUCKET_NAME, video.raw_file.name)
    job_id = create_transcode_job(video.raw_file.name)

    video.transcoder_job_id = job_id
    video.save()

    # TODO: schedule check job
