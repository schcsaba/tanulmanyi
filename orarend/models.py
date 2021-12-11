from django.db import models


class Beallitas(models.Model):
    nev = models.CharField(max_length=200, verbose_name='név', unique='True')
    ertek = models.CharField(max_length=200, verbose_name='érték')
    magyarazat = models.CharField(max_length=400, verbose_name='magyarázat', blank=True, null=True)

    class Meta:
        verbose_name = 'beállítás'
        verbose_name_plural = 'beállítások'
        ordering = ['nev']

    def __str__(self):
        return '%s: %s' % (self.nev, self.ertek)


class OrarendFajl(models.Model):
    orarendfajl = models.FileField(upload_to='orarendek/', verbose_name='órarendfájl', help_text='Hallgatói órarendfájl esetében "...years_days_horizontal.html", oktatói órarendfájl esetében pedig "...teachers_days_horizontal.html" végű órarendfájlt kell ide feltölteni. Más fájlok esetén hibaüzenetet ír ki az oldal.')
    oktatoi_orarendfajl = models.BooleanField(default=False, verbose_name='oktatói órarendfájl', help_text='Ha nincs kipipálva, akkor ez egy hallgatói órarendfájl.')
    aktiv = models.BooleanField(default=False, verbose_name='aktív')

    class Meta:
        verbose_name = 'órarendfájl'
        verbose_name_plural = 'órarendfájlok'

    def __str__(self):
        return self.orarendfajl.name

