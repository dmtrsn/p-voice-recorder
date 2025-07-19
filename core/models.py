from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужчина'),
        ('F', 'Женщина'),
    ]

    REGION_CHOICES = [(0, 'Andalucía'),
                   (1,'Aragón'),
                   (2, 'Principado de Asturias'),
                   (3, 'Islas Baleares'),
                   (4, 'Comunidad Valenciana'),
                   (5, 'Galicia'),
                   (6, 'Canarias'),
                   (7, 'Cantabria'),
                   (8, 'Castilla-La Mancha'),
                   (9, 'Castilla y León'),
                   (10, 'Cataluña'),
                   (11, 'Comunidad de Madrid'),
                   (12, 'Región de Murcia'),
                   (13, 'Comunidad Foral de Navarra'),
                   (14, 'La Rioja'),
                   (15, 'Pais Vasco'),
                   (16, 'Extremadura'),]

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
    region = models.IntegerField(choices=REGION_CHOICES, verbose_name = 'Регион')
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
