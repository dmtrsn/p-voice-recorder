from django.db import models

class AudioUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    result = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
