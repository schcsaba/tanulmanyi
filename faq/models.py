from django.db import models
from tinymce.models import HTMLField

class Kerdes(models.Model):
    kerdes = models.TextField(max_length=500, verbose_name='kérdés')
    valasz = HTMLField(max_length=2000, verbose_name='válasz')
    publikalt = models.BooleanField(default='True', verbose_name='publikált')

    class Meta:
        verbose_name = 'kérdés'
        verbose_name_plural = 'kérdések'
        ordering = ['kerdes']

    def __str__(self):
        return self.kerdes
