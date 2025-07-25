import os
from django.db import models
from django.utils import timezone
from .validators import validate_region


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужчина'),
        ('F', 'Женщина'),
    ]

    AGE_CHOICES = [
        (0, '20-30'),
        (1, '30-40'),
        (2, '40-50'),
    ]

    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('S', 'Success')
    ]

    name = models.CharField(max_length=100, verbose_name = 'Имя')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name = 'Пол')
    age = models.IntegerField(choices=AGE_CHOICES, verbose_name = 'Возраст')
    region = models.CharField(max_length=200, verbose_name = 'Регион', validators=[validate_region])
    audio_file = models.FileField(upload_to='media/', verbose_name = 'Аудио')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name = 'Статус', default='P')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        ordering = ['-id']
    
    def __str__(self):
        return str(self.id) + ' - ' + self.name

    @property
    def timesince(self):
        return (timezone.now()-self.created_at).total_seconds()
