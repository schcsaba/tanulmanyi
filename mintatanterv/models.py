from django.db import models
from tinymce.models import HTMLField
from phonenumber_field.modelfields import PhoneNumberField

class Munkarend(models.Model):
    nev = models.CharField(max_length=20, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'munkarend'
        verbose_name_plural = 'munkarendek'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class Kovetelmeny(models.Model):
    nev = models.CharField(max_length=40, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'követelmény'
        verbose_name_plural = 'követelmények'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class Kurzustipus(models.Model):
    nev = models.CharField(max_length=30, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'kurzustípus'
        verbose_name_plural = 'kurzustípusok'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class Vizsgatipus(models.Model):
    nev = models.CharField(max_length=50, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'vizsgatípus'
        verbose_name_plural = 'vizsgatípusok'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class Oktatotipus(models.Model):
    nev = models.CharField(max_length=50, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'oktatótípus'
        verbose_name_plural = 'oktatótípusok'
        ordering = ['nev']

    def __str__(self):
        return self.nev


class Oktato(models.Model):
    elotag = models.CharField(max_length=20, blank=True, verbose_name='előtag')
    vezeteknev = models.CharField(max_length=100, verbose_name='vezetéknév')
    keresztnev = models.CharField(max_length=100, verbose_name='keresztnév')
    neptun_kod = models.CharField(max_length=6, verbose_name='neptun kód')
    avatott_nev = models.CharField(max_length=100, blank=True, verbose_name='avatott név')
    tel = PhoneNumberField(blank=True, verbose_name='telefon')
    email = models.EmailField(verbose_name='email', blank=True)
    megjelenites = models.BooleanField(default=False, verbose_name='Megjelenítés', help_text="Megjelenjen-e az oktató az oktatók előrhetősége oldalon?")

    class Meta:
        verbose_name = 'oktató'
        verbose_name_plural = 'oktatók'
        ordering = ['vezeteknev', 'keresztnev']
        unique_together = ('vezeteknev', 'keresztnev', 'neptun_kod')

    def __str__(self):
        return '%s %s %s (%s)' % (self.elotag, self.vezeteknev, self.keresztnev, self.avatott_nev) if self.avatott_nev else '%s %s %s' % (self.elotag, self.vezeteknev, self.keresztnev)

    def get_absolute_url(self):
        return "/%i/" % self.id


class KepzesiSzint(models.Model):
    nev = models.CharField(max_length=100, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'képzési szint'
        verbose_name_plural = 'képzési szintek'

    def __str__(self):
        return self.nev


class Kepzes(models.Model):
    nev = models.CharField(max_length=200, verbose_name='név')
    kepzesi_szint = models.ForeignKey(KepzesiSzint, on_delete=models.CASCADE, verbose_name='képzési szint')

    class Meta:
        verbose_name = 'képzés'
        verbose_name_plural = 'képzések'

    def __str__(self):
        return '%s - %s' % (self.nev, self.kepzesi_szint)


class Szak(models.Model):
    nev = models.CharField(max_length=200, verbose_name='név')
    kepzes = models.ForeignKey(Kepzes, on_delete=models.CASCADE, verbose_name='képzés')

    class Meta:
        verbose_name = 'szak'
        verbose_name_plural = 'szakok'
        unique_together = ('nev', 'kepzes')

    def __str__(self):
        return '%s szak - %s képzés' % (self.nev, self.kepzes)


class NagyTargyCsoport(models.Model):
    nev = models.CharField(max_length=200, verbose_name='név')
    szak = models.ForeignKey(Szak, on_delete=models.CASCADE, verbose_name='szak')

    class Meta:
        verbose_name = 'nagytárgycsoport'
        verbose_name_plural = 'nagytárgycsoportok'
        unique_together = ('nev', 'szak')

    def __str__(self):
        return '%s nagytárgycsoport - %s' % (self.nev, self.szak)


class Szakirany(models.Model):
    nev = models.CharField(max_length=200, verbose_name='név')
    szak = models.ForeignKey(Szak, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='szak')

    class Meta:
        verbose_name = 'szakirány'
        verbose_name_plural = 'szakirányok'
        unique_together = ('nev', 'szak')

    def __str__(self):
        if self.szak:
            return '%s szakirány - %s' % (self.nev, self.szak)
        else:
            return '%s szakirány' % (self.nev)


class Specializacio(models.Model):
    nev = models.CharField(max_length=200, verbose_name='név')
    szak = models.ForeignKey(Szak, on_delete=models.CASCADE, verbose_name='szak')

    class Meta:
        verbose_name = 'specializáció'
        verbose_name_plural = 'specializációk'
        unique_together = ('nev', 'szak')

    def __str__(self):
        return '%s specializáció - %s' % (self.nev, self.szak)


class NagyTargy(models.Model):
    targykod = models.CharField(max_length=10, unique='True', verbose_name='tárgykód')
    targynev = models.CharField(max_length=200, verbose_name='tárgynév')
    kredit = models.IntegerField(verbose_name='kredit')
    szakirany = models.ManyToManyField(Szakirany, blank=True, related_name='szakirany', verbose_name='szakirány')
    szak = models.ManyToManyField(Szak, blank=True, related_name='szak', verbose_name='szak')
    nagytargycsoport = models.ManyToManyField(NagyTargyCsoport, blank=True, related_name='nagytargycsoport', verbose_name='nagytárgycsoport')
    oktato = models.ManyToManyField(Oktato, through='NagyTargyOktato', blank=True, verbose_name='oktató')

    class Meta:
        verbose_name = 'nagytárgy'
        verbose_name_plural = 'nagytárgyak'
        ordering = ['targykod']

    def __str__(self):
        return '%s - %s' % (self.targykod, self.targynev)


class NagyTargyOktato(models.Model):
    nagytargy = models.ForeignKey(NagyTargy, on_delete=models.CASCADE, verbose_name='nagytárgy')
    oktato = models.ForeignKey(Oktato, on_delete=models.CASCADE, verbose_name='oktató')
    oktato_tipus = models.ForeignKey(Oktatotipus, on_delete=models.CASCADE, verbose_name='oktató típus')

    class Meta:
        verbose_name = 'nagytárgy oktató'
        verbose_name_plural = 'nagytárgyak oktatói'
        unique_together = ('nagytargy', 'oktato', 'oktato_tipus')

    def __str__(self):
        return '%s --- %s --- %s' % (self.nagytargy, self.oktato, self.oktato_tipus)


class Targy(models.Model):
    targykod = models.CharField(max_length=20, unique='True', verbose_name='tárgykód')
    targynev = models.CharField(max_length=200, verbose_name='tárgynév')
    kredit = models.IntegerField(verbose_name='kredit')
    kovetelmeny = models.ForeignKey(Kovetelmeny, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='követelmény')
    nagytargy = models.ManyToManyField(NagyTargy, blank=True, related_name='nagytargy', verbose_name='nagytárgy')
    kurzustipus = models.ManyToManyField(Kurzustipus, blank=True, verbose_name='kurzustípus')
    elofeltetel_targy = models.ManyToManyField('self', symmetrical=False, blank=True, verbose_name='előfeltétel tárgy', related_name='ezentargyakelofeltetele')
    elofeltetel_targy_tipussal = models.ManyToManyField('self', through='Elofeltetel', symmetrical=False, blank=True, verbose_name='előfeltétel tárgy típussal', related_name='ezentargyakelofelteteletipussal')
    ekvivalens_targy = models.ManyToManyField('self', blank=True, verbose_name='ekvivalens tárgy', related_name='targyekvivalenstargyai')
    munkarend = models.ManyToManyField(Munkarend, through='TargyMunkarend', blank=True, verbose_name='kurzus')
    oktato = models.ManyToManyField(Oktato, through='TargyOktato', blank=True, verbose_name='tárgyoktató')
    mintatanterv = models.ManyToManyField('Mintatanterv', through='MintatantervTargy', blank=True, verbose_name='tárgy mintatantervei', related_name='targymintatantervei')
    cel = HTMLField(max_length=100000, blank=True, null=True, verbose_name='A tantárgy elsajátításának célja')
    targyleiras = HTMLField(max_length=100000, blank=True, null=True, verbose_name='Tantárgyi program')
    modszertan = HTMLField(max_length=100000, blank=True, null=True, verbose_name='Módszertan')
    evkozi_kov = HTMLField(max_length=100000, blank=True, null=True, verbose_name='Évközi tanulmányi követelmények')
    vegso_kov = HTMLField(max_length=100000, blank=True, null=True, verbose_name='A félévvégi érdemjegy megszerzésének követelményei')
    kotelezo_olvasmanyok = HTMLField(max_length=100000, blank=True, null=True, verbose_name='Kötelező olvasmányok')
    ajanlott_irodalom = HTMLField(max_length=100000, blank=True, null=True, verbose_name='Ajánlott irodalom')

    class Meta:
        verbose_name = 'tárgy'
        verbose_name_plural = 'tárgyak'
        ordering = ['targykod']

    def __str__(self):
        return '%s - %s' % (self.targykod, self.targynev)

    def get_absolute_url(self):
        return "/mintatantervek/targyak/%i/" % self.id


class Nyelv(models.Model):
    nev = models.CharField(max_length=50, verbose_name='név', unique=True)

    class Meta:
        verbose_name = 'nyelv'
        verbose_name_plural = 'nyelvek'

    def __str__(self):
        return self.nev


class TargyMunkarend(models.Model):
    targy = models.ForeignKey(Targy, on_delete=models.CASCADE, verbose_name='tárgy')
    kurzuskod = models.CharField(max_length=20, verbose_name='kurzuskód', unique=True)
    munkarend = models.ForeignKey(Munkarend, on_delete=models.CASCADE, verbose_name='munkarend')
    orarend_oraszam = models.IntegerField(verbose_name='órarend óraszám')
    max_hianyzas = models.IntegerField(verbose_name='max hiányzás')
    akkr_oraszam = models.IntegerField(verbose_name='akkreditált óraszám')
    max_letszam = models.IntegerField(blank=True, null=True, verbose_name='maximális létszám')
    kurzustipus = models.ForeignKey(Kurzustipus, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='kurzustípus')
    nyelv = models.ForeignKey(Nyelv, on_delete=models.SET_DEFAULT, verbose_name='nyelv', default=1)
    lejelentkezes_letiltva = models.BooleanField(default=False, verbose_name='Lejelentkezés letiltva')
    jelentkezes_letiltva = models.BooleanField(default=False, verbose_name='Jelentkezés letiltva')
    megjegyzes = models.CharField(max_length=300, verbose_name='megjegyzés', blank=True, null=True)
    kurzusfelveteli_kovetelmeny = models.CharField(max_length=500, verbose_name='kurzusfelvételi követelmény', blank=True, null=True)
    kurzusfelveteli_kovetelmeny_leiras = models.CharField(max_length=500, verbose_name='kurzusfelvételi követelmény leírás', blank=True, null=True)
    nem_indul = models.BooleanField(default=False, verbose_name='nem indul')
    vizsgatipus = models.ManyToManyField(Vizsgatipus, blank=True, verbose_name='vizsgatípus')
    oktato = models.ManyToManyField(Oktato, blank=True, related_name='targymunkarendoktato', verbose_name='kurzusoktató')
    belso_megjegyzes = models.CharField(max_length=300, verbose_name='belső megjegyzés', blank=True, null=True)

    class Meta:
        verbose_name = 'tárgy kurzus'
        verbose_name_plural = 'tárgyak kurzusai'

    def __str__(self):
        return '%s --- %s' % (self.targy, self.kurzuskod)

    def get_absolute_url(self):
        return "/mintatantervek/kurzusok/%i/" % self.id

class TargyOktato(models.Model):
    targy = models.ForeignKey(Targy, on_delete=models.CASCADE, verbose_name='tárgy')
    oktato = models.ForeignKey(Oktato, on_delete=models.CASCADE, verbose_name='tárgyoktató')
    oktato_tipus = models.ForeignKey(Oktatotipus, on_delete=models.CASCADE, verbose_name='oktató típus')

    class Meta:
        verbose_name = 'tárgy oktató'
        verbose_name_plural = 'tárgyak oktatói'
        unique_together = ('targy', 'oktato', 'oktato_tipus')

    def __str__(self):
        return '%s --- %s --- %s' % (self.targy, self.oktato, self.oktato_tipus)

class Mintatanterv(models.Model):
    kod = models.CharField(max_length=10, unique='True', verbose_name='kód')
    nev = models.CharField(max_length=200, verbose_name='név')
    szakirany = models.ManyToManyField(Szakirany, blank=True, related_name='mintatantervszakirany', verbose_name='szakirány')
    specializacio = models.ManyToManyField(Specializacio, blank=True, related_name='mintatantervspecializacio', verbose_name='specializáció')
    szak = models.ManyToManyField(Szak, blank=True, related_name='mintatantervszak', verbose_name='szak')
    targy = models.ManyToManyField(Targy, through='MintatantervTargy', blank=True, verbose_name='tárgy', related_name='mintatantervtargyai')
    aktualis = models.BooleanField(default=False, verbose_name='aktuális', help_text='Az itt kijelölt mintatantervek tárgyainak kurzusai jelennek meg az oktatók őszi és tavaszi kurzuslistáiban.')

    class Meta:
        verbose_name = 'mintatanterv'
        verbose_name_plural = 'mintatantervek'
        ordering = ['kod']

    def __str__(self):
        return '%s - %s' % (self.kod, self.nev)

    def get_absolute_url(self):
        return "/mintatantervek/%i/" % self.id

class FelvetelTipusa(models.Model):
    nev = models.CharField(max_length=50, unique='True', verbose_name='név')

    class Meta:
        verbose_name = 'felvétel típusa'
        verbose_name_plural = 'felvétel típusai'

    def __str__(self):
        return self.nev

class MintatantervTargy(models.Model):
    mintatanterv = models.ForeignKey(Mintatanterv, on_delete=models.CASCADE, verbose_name='mintatanterv')
    targy = models.ForeignKey(Targy, on_delete=models.CASCADE, verbose_name='tárgy')
    felev = models.IntegerField(verbose_name='félév')
    kredit = models.IntegerField(blank=True, null=True, verbose_name='kredit')
    felvetel_tipusa = models.ForeignKey(FelvetelTipusa, on_delete=models.CASCADE, verbose_name='felvétel típusa')
    oszi_tavaszi = models.BooleanField(default=False, verbose_name='őszi és tavaszi félévben is indul')
    elofeltetel_targy = models.ManyToManyField(Targy, symmetrical=False, blank=True, related_name='ezenmintatantervtargyakelofeltetele', verbose_name='előfeltétel tárgy')
    elofeltetel_targy_tipussal = models.ManyToManyField(Targy, through='ElofeltetelMintatantervben', symmetrical=False, blank=True, verbose_name='előfeltétel tárgy típussal', related_name='ezenmintatantervtargyakelofelteteletipussal')

    class Meta:
        verbose_name = 'mintatanterv tárgy'
        verbose_name_plural = 'mintatantervek tárgyai'
        unique_together = ('mintatanterv', 'targy')

    def __str__(self):
        return '%s --- %s' % (self.mintatanterv, self.targy)

class Felev(models.Model):
    felev = models.CharField(max_length=9, unique=True, verbose_name='félév')
    aktualis = models.BooleanField(default=False, verbose_name='aktuális')

    class Meta:
        verbose_name = 'félév'
        verbose_name_plural = 'félévek'

    def __str__(self):
        return '%s --- aktuális: %s' % (self.felev, self.aktualis)

class Elofeltetel(models.Model):
    targy = models.ForeignKey(Targy, on_delete=models.CASCADE, verbose_name='tárgy', related_name='fotargy')
    elofeltetel_targy = models.ForeignKey(Targy, on_delete=models.CASCADE, verbose_name='előfeltétel tárgy', related_name='elofelteteltargy')
    eros_elofeltetel = models.BooleanField(default=False, verbose_name='erős előfeltétel')

    class Meta:
        verbose_name = 'előfeltétel'
        verbose_name_plural = 'előfeltételek'
        unique_together = ('targy', 'elofeltetel_targy')

    def __str__(self):
        return '%s --- előfeltétel: %s --- erős: %s' % (self.targy, self.elofeltetel_targy, self.eros_elofeltetel)

class ElofeltetelMintatantervben(models.Model):
    targy = models.ForeignKey(MintatantervTargy, on_delete=models.CASCADE, verbose_name='mintatantervtárgy', related_name='fotargymintatantervben')
    elofeltetel_targy = models.ForeignKey(Targy, on_delete=models.CASCADE, verbose_name='előfeltétel tárgy', related_name='elofelteteltargymintatantervben')
    eros_elofeltetel = models.BooleanField(default=False, verbose_name='erős előfeltétel')

    class Meta:
        verbose_name = 'előfeltétel mintatantervben'
        verbose_name_plural = 'előfeltételek mintatantervben'
        unique_together = ('targy', 'elofeltetel_targy')

    def __str__(self):
        return '%s --- előfeltétel: %s --- erős: %s' % (self.targy, self.elofeltetel_targy, self.eros_elofeltetel)