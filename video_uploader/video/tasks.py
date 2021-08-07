from django.conf import settings
from django.utils import timezone

from django_q.tasks import async_task, schedule, Schedule


from video_uploader.video.models import Video
from video_uploader.video.utils import create_transcode_job, extract_outputs,\
    upload_file, check_job_status


def post_save_video(video: Video) -> None:
    """Function to be called after createing Video Instance

    Uploads file to INPUT_BUCKET and schedules transcode job

    Args:
        video: Video Instance
    """
    upload_file(video.raw_file, settings.INPUT_BUCKET_NAME, video.raw_file.name)
    job_id: str = create_transcode_job(video.raw_file.name)

    video.transcoder_job_id = job_id
    video.save()

    async_task('video_uploader.tasks.watch_transcode_job', video)


def watch_transcode_job(video: Video) -> None:
    """Watches transcode job associated with video

    Re-schedules self until job is completed or errored
    If complete then sets output and thumbnail attributs

    Args:
        video: Video Instance
    """

    if not video.job_id:
        raise AssertionError("Video.job_id not set")

    video.status = check_job_status(video.job_id)
    video.save()

    if video.status == 'Complete':
        response: dict = extract_outputs(video.raw_file.name)

        video.outputs = response['outputs']
        video.thumbnail = response['thumbnail']
        video.save()

    elif video.status not in ['Canceled', 'Error']:
        # schedule next check after 15s
        schedule(
            'video_uploader.tasks.watch_transcode_job',
            video,
            schedule_type=Schedule.MINUTES,
            minutes=1,
            repeats=1,
            next_run=timezone.now() + timezone.timedelta(seconds=15)
        )
