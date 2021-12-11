import re
from django.db import models
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField
from tinymce.models import HTMLField


class Beallitas(models.Model):
    nev = models.CharField(max_length=200, verbose_name='név', unique='True')
    ertek = models.CharField(max_length=200, blank=True, null=True, verbose_name='érték')
    szoveg = HTMLField(max_length=100000, blank=True, null=True, verbose_name='szöveg')
    magyarazat = models.CharField(max_length=400, verbose_name='magyarázat', blank=True, null=True)

    class Meta:
        verbose_name = 'beállítás'
        verbose_name_plural = 'beállítások'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class Temakor(models.Model):
    cim = models.CharField(max_length=255, unique='True', verbose_name='cím')

    class Meta:
        verbose_name = 'témakör'
        verbose_name_plural = 'témakörök'
        ordering = ['cim']

    def __str__(self):
        return re.sub(r'^(.{75}).*$', '\g<1>...', self.cim)


class Temavezeto(models.Model):
    elotag = models.CharField(max_length=20, blank=True, verbose_name='előtag')
    vezeteknev = models.CharField(max_length=100, verbose_name='vezetéknév')
    keresztnev = models.CharField(max_length=100, verbose_name='keresztnév')
    neptun_kod = models.CharField(max_length=6, verbose_name='neptun kód')
    max_letszam = models.IntegerField(verbose_name='maximális létszám')
    temakorok = models.ManyToManyField(Temakor, through='TemavezetoTemakor', blank=True, verbose_name='témák')
    tel = PhoneNumberField(blank=True, verbose_name='telefon')
    email = models.EmailField(verbose_name='email')
    avatott_nev = models.CharField(max_length=100, blank=True, verbose_name='avatott név')
    valaszthato = models.BooleanField(verbose_name='választható', default=False)
    inaktiv = models.BooleanField(verbose_name='inaktív', default=False)
    sorszam = models.IntegerField(verbose_name='sorszám', blank=True, null=True, unique='True')

    class Meta:
        verbose_name = 'témavezető'
        verbose_name_plural = 'témavezetők'
        ordering = ['vezeteknev', 'keresztnev']
        unique_together = ('vezeteknev', 'keresztnev', 'neptun_kod')

    def __str__(self):
        return '%s %s (%s)' % (self.vezeteknev, self.keresztnev, self.neptun_kod)

    def megirt_temak_szama(self):
        temavezetonel_megirt_temak_szama = 0
        for temavezetotemakor in self.temavezetotemakor_set.all():
            temavezetonel_megirt_temak_szama = temavezetonel_megirt_temak_szama + temavezetotemakor.megirt_temak().count()

        return temavezetonel_megirt_temak_szama

    def nem_megirt_temak_szama(self):
        temavezetonel_nem_megirt_temak_szama = 0
        for temavezetotemakor in self.temavezetotemakor_set.all():
            temavezetonel_nem_megirt_temak_szama = temavezetonel_nem_megirt_temak_szama + temavezetotemakor.nem_megirt_temak().count()

        return temavezetonel_nem_megirt_temak_szama

    def valaszthato_temakorok_szama(self):
        temavezeto_valaszthato_temakoreinek_szama = self.temavezetotemakor_set.filter(rejtett=False).count()

        return temavezeto_valaszthato_temakoreinek_szama

    def valaszthato_temakorok(self):
        valaszthato_temakorok = self.temavezetotemakor_set.filter(rejtett=False)

        return valaszthato_temakorok

    def valaszthato_temakorok_hallgatoknak_szama(self):
        #temavezeto_valaszthato_temakoreinek_szama_hallgatoknak = self.temavezetotemakor_set.filter(rejtett=False).exclude(temakor=112).count()
        temavezeto_valaszthato_temakoreinek_szama_hallgatoknak = self.temavezetotemakor_set.filter(rejtett=False).count()

        return temavezeto_valaszthato_temakoreinek_szama_hallgatoknak

    def valaszthato_temakorok_hallgatoknak(self):
        #valaszthato_temakorok_hallgatoknak = self.temavezetotemakor_set.filter(rejtett=False).exclude(temakor=112)
        valaszthato_temakorok_hallgatoknak = self.temavezetotemakor_set.filter(rejtett=False)

        return valaszthato_temakorok_hallgatoknak


class TemavezetoTemakor(models.Model):
    temavezeto = models.ForeignKey(Temavezeto, on_delete=models.CASCADE, verbose_name='témavezető')
    temakor = models.ForeignKey(Temakor, on_delete=models.CASCADE, verbose_name='témakör')
    rejtett = models.BooleanField(verbose_name='rejtett', default=False)

    class Meta:
        verbose_name = 'témavezető témaköre'
        verbose_name_plural = 'témavezetők témakörei'
        ordering = ['temavezeto', 'temakor']
        unique_together = ('temavezeto', 'temakor')

    def __str__(self):
        return '%s --- %s' % (self.temavezeto, self.temakor)

    def nem_megirt_temak(self):
        return self.tema_set.exclude(tema_statusz=3).exclude(tema_statusz=5)

    def megirt_temak(self):
        return self.tema_set.filter(tema_statusz=3)

    def szabad_temak(self):
        return self.tema_set.filter(tema_statusz=1)

    def szabad_plusz_temak(self):
        return self.tema_set.filter(Q(tema_statusz=1) | Q(tema_statusz=4))

    def foglalt_temak(self):
        return self.tema_set.filter(tema_statusz=2)

    def cimbejelento_temak(self):
        return self.tema_set.filter(tema_statusz=6)

    def szabad_plusz_cimbejelento_temak(self):
        return self.tema_set.filter(Q(tema_statusz=1) | Q(tema_statusz=4) | Q(tema_statusz=6))


class TemaStatusz(models.Model):
    nev = models.CharField(max_length=50, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'cím státusza'
        verbose_name_plural = 'címek státuszai'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class NemMegirtTemaManager(models.Manager):
    def get_queryset(self):
        return super(NemMegirtTemaManager, self).get_queryset().exclude(tema_statusz=3)

class MegirtTemaManager(models.Manager):
    def get_queryset(self):
        return super(MegirtTemaManager, self).get_queryset().filter(tema_statusz=3)

class FoglaltTemaManager(models.Manager):
    def get_queryset(self):
        return super(FoglaltTemaManager, self).get_queryset().filter(tema_statusz=2)

class CimbejelentoTemaManager(models.Manager):
    def get_queryset(self):
        return super(CimbejelentoTemaManager, self).get_queryset().filter(tema_statusz=6)


class Tema(models.Model):
    cim = models.CharField(max_length=255, unique='True', verbose_name='cím')
    idegen_nyelv_szukseges = models.CharField(max_length=500, blank=True, verbose_name='idegen nyelv szükséges')
    megjegyzes = models.CharField(max_length=500, blank=True, verbose_name='megjegyzés')
    temavezeto_temakor = models.ForeignKey(TemavezetoTemakor, on_delete=models.CASCADE, verbose_name='témavezető témaköre')
    tema_statusz = models.ForeignKey(TemaStatusz, on_delete=models.CASCADE, verbose_name='cím státusza')
    objects = models.Manager()
    nemmegirt = NemMegirtTemaManager()
    megirt = MegirtTemaManager()
    foglalt = FoglaltTemaManager()
    cimbejelento = CimbejelentoTemaManager()

    class Meta:
        verbose_name = 'cím'
        verbose_name_plural = 'címek'
        ordering = ['temavezeto_temakor', 'cim']

    def __str__(self):
        return '%s --- %s' % (self.temavezeto_temakor, re.sub(r'^(.{75}).*$', '\g<1>...', self.cim))


class Hallgato(models.Model):
    elotag = models.CharField(max_length=20, blank=True, verbose_name='előtag')
    vezeteknev = models.CharField(max_length=100, verbose_name='vezetéknév')
    keresztnev = models.CharField(max_length=100, verbose_name='keresztnév')
    neptun_kod = models.CharField(max_length=6, verbose_name='neptun kód')

    class Meta:
        verbose_name = 'hallgató'
        verbose_name_plural = 'hallgatók'
        ordering = ['vezeteknev', 'keresztnev']
        unique_together = ('vezeteknev', 'keresztnev', 'neptun_kod')

    def __str__(self):
        return '%s %s (%s)' % (self.vezeteknev, self.keresztnev, self.neptun_kod)


class Statusz(models.Model):
    nev = models.CharField(max_length=30, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'státusz'
        verbose_name_plural = 'státuszok'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class Tagozat(models.Model):
    nev = models.CharField(max_length=20, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'tagozat'
        verbose_name_plural = 'tagozatok'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class Kepzes(models.Model):
    kepzes_kod = models.CharField(max_length=10, unique='True', verbose_name='képzés kód')
    kepzes_nev = models.CharField(max_length=50, verbose_name='képzés név')
    tagozat = models.ForeignKey(Tagozat, on_delete=models.CASCADE, verbose_name='tagozat')
    hallgatok = models.ManyToManyField(Hallgato, through='HallgatoKepzes', verbose_name='hallgatók')

    class Meta:
        verbose_name = 'képzés'
        verbose_name_plural = 'képzések'
        ordering = ['kepzes_kod']
        unique_together = ('kepzes_kod', 'kepzes_nev', 'tagozat')

    def __str__(self):
        return '%s - %s (%s)' % (self.kepzes_nev, self.tagozat, self.kepzes_kod)


class HallgatoKepzes(models.Model):
    hallgato = models.ForeignKey(Hallgato, on_delete=models.CASCADE, verbose_name='hallgató')
    kepzes = models.ForeignKey(Kepzes, on_delete=models.CASCADE, verbose_name='képzés')
    kezdet = models.DateField(verbose_name='kezdet')
    veg = models.DateField(blank=True, null=True, verbose_name='vég')
    statusz = models.ForeignKey(Statusz, on_delete=models.CASCADE, verbose_name='státusz')
    temak = models.ManyToManyField(Tema, through='HallgatoKepzesTema', verbose_name='témák')

    class Meta:
        verbose_name = 'hallgató képzése'
        verbose_name_plural = 'hallgatók képzései'
        ordering = ['hallgato', 'kezdet']
        unique_together = ('hallgato', 'kepzes', 'kezdet')

    def __str__(self):
        return '%s - %s - %s' % (self.hallgato, self.kepzes, self.statusz)


class ErdemJegy(models.Model):
    nev = models.CharField(max_length=15, unique='True', verbose_name='név')
    ertek = models.IntegerField(unique='True', verbose_name='érték')

    class Meta:
        verbose_name = 'érdemjegy'
        verbose_name_plural = 'érdemjegyek'
        ordering = ['ertek']
        unique_together = ('nev', 'ertek')

    def __str__(self):
        return '%s (%s)' % (self.nev, self.ertek)


class HallgatoKepzesTema(models.Model):
    kerveny_00 = 'kerveny_00'
    kerveny_01 = 'kerveny_01'
    kerveny_02 = 'kerveny_02'
    KERVENYEK_CHOICES = ((kerveny_00, 'Még nem volt kérvény'), (kerveny_01, 'Első kérvény'), (kerveny_02, 'Második kérvény'))
    hallgato_kepzes = models.ForeignKey(HallgatoKepzes, on_delete=models.CASCADE, verbose_name='hallgató képzése')
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, verbose_name='cím')
    kezdet = models.DateField(verbose_name='kezdet')
    veg = models.DateField(blank=True, null=True, verbose_name='vég')
    erdemjegy = models.ForeignKey(ErdemJegy, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='érdemjegy')
    szakdolgozat_targyat_felvett = models.BooleanField(verbose_name='szakdolgozat tárgyat felvett vagy kérvény alapján segíti témavezető', default=False)
    kerveny = models.CharField(max_length=12, choices=KERVENYEK_CHOICES, default=kerveny_00, verbose_name='hányszor kérvényezte a témavezetői segítséget', help_text='Ezt a mezőt még nem használjuk, az eggyel fentebb lévő mezőbe kell az erre vonatkozó adatot beírni.')
    szakdolgozat_link = models.URLField(blank=True, null=True, verbose_name='szakdolgozat link')

    class Meta:
        verbose_name = 'hallgató szakdolgozat címe képzésen'
        verbose_name_plural = 'hallgatók szakdolgozat címei képzésen'
        ordering = ['hallgato_kepzes', 'kezdet']
        unique_together = ('hallgato_kepzes', 'tema', 'kezdet')

    def __str__(self):
        return '%s --- %s --- %s - %s' % (self.hallgato_kepzes, self.tema, self.kezdet, self.veg)


