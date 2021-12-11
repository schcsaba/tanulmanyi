from django.db import models

class Szabalyzat(models.Model):
    nev = models.CharField(max_length=200, verbose_name='név', unique='True')
    szabalyzatfajl = models.FileField(upload_to='szabalyzatok/', verbose_name='szabályzatfájl')
    csak_oktatoknak = models.BooleanField(default=False, verbose_name='csak oktatóknak')

    class Meta:
        verbose_name_plural = 'szabályzatok'
        ordering = ['nev']

    def __str__(self):
        return self.nev