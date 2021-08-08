from django.db import models
from django.core.validators import FileExtensionValidator

from django_q.tasks import async_task

class Video(models.Model):
    raw_file = models.FileField(validators=[FileExtensionValidator(
        allowed_extensions=["mp4", "mov", "wmv", "webm", "mkv"])])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    outputs = models.JSONField(null=True, blank=True)
    thumbnail = models.CharField(max_length=255, blank=True)
    transcoder_job_id = models.CharField(max_length=255, blank=True)
    transcode_status = models.CharField(max_length=25, default="Pending")

    def __str__(self):
        return self.raw_file.name

    def save(self, *args, **kwargs) -> None:
        created = not self.id
        super().save(*args, **kwargs)

        if created:
            async_task('video_uploader.video.tasks.post_save_video', self)
