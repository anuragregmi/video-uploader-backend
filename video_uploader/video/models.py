from django.db import models
from django.core.validators import FileExtensionValidator

class Video(models.Model):
    name = models.CharField(max_length=255)
    raw_file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=["mp4", "mov", "wmv"])])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    converted_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
