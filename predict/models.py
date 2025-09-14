from django.db import models
from django.utils import timezone
import uuid

class AudioUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    result = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Edit(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    REGION_CHOICES = [(0, 'Irish'),
                   (1,'Scottish'),]

    AGE_CHOICES = [
        (0, '20-30'),
        (1, '30-40'),
        (2, '40-50'),
    ]
    
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    audio_upload = models.ForeignKey(
        AudioUpload, 
        on_delete=models.CASCADE, 
        related_name='edit_tokens'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_right = models.BooleanField(null=True, default=None)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name = 'Gender', null=True, default=None)
    age = models.IntegerField(choices=AGE_CHOICES, verbose_name = 'Age', null=True, default=None)
    region = models.IntegerField(choices=REGION_CHOICES, verbose_name = 'Region', null=True, default=None)

    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Edit token for {self.audio_upload.id} - {self.token}"
    
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True