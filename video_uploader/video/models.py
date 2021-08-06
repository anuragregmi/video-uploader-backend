from video_uploader.video.utils import upload_file
from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings

class Video(models.Model):
    name = models.CharField(max_length=255, unique=True)
    raw_file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=["mp4", "mov", "wmv"])])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    converted_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        import ipdb; ipdb.set_trace()

        # TODO: @anurag move this to background task
        if upload_file(self.raw_file, "input-videos-anurag", self.raw_file.name):
            print("uploaded successfully")
        else:
            print("Upload failed")
