import io
import re
import zipfile

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from mintatanterv.models import MintatantervTargy, Mintatanterv, Munkarend, TargyMunkarend
from mintatanterv.views import FELEVEK, XLSX_FEJLEC, _felev_kurzusai, _neptun_mintatanterv_kod
from tanulmanyi.testing import MintatantervAdatok, create_users


def lekerdezesek_szama(client, url):
    with CaptureQueriesContext(connection) as ctx:
        response = client.get(url)
    assert response.status_code == 200, (url, response.status_code)
    return len(ctx.captured_queries)


def xlsx_sorok(content):
    """Reads the first sheet of an XlsxWriter file into a list of rows (lists of cell strings)."""
    z = zipfile.ZipFile(io.BytesIO(content))
    strings = re.findall(r'<si><t[^>]*>(.*?)</t></si>', z.read('xl/sharedStrings.xml').decode())
    sorok = []
    for sor in re.findall(r'<row [^>]*>(.*?)</row>', z.read('xl/worksheets/sheet1.xml').decode()):
        cellak = re.findall(r'<c ([^>]*)>(?:<v>(.*?)</v>)?</c>', sor)
        sorok.append([strings[int(v)] if 't="s"' in attrs else v for attrs, v in cellak])
    return sorok


class MintatantervTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = create_users()
        cls.adatok = MintatantervAdatok()

    def setUp(self):
        self.client.force_login(self.users['staff'])


class MintatantervOldalTests(MintatantervTestCase):
    def test_targyak_sorrendje_es_kreditek(self):
        tanterv = self.adatok.mintatantervek[0]
        response = self.client.get(reverse('mintatanterv', args=[tanterv.pk]))
        mtts = response.context['mintatantervtargyak']
        self.assertEqual([(m.felvetel_tipusa_id, m.targy_id) for m in mtts],
                         sorted((m.felvetel_tipusa_id, m.targy_id) for m in tanterv.mintatantervtargy_set.all()))
        for felev in response.context['felevek']:
            kotelezo = [m for m in mtts if m.felev == felev and m.felvetel_tipusa_id == 1]
            self.assertEqual(response.context['felev_kreditek'][felev],
                             sum(m.kredit or m.targy.kredit for m in kotelezo))

    def test_mely_targyaknak_elofeltetele(self):
        for tanterv in self.adatok.mintatantervek:
            response = self.client.get(reverse('mintatanterv', args=[tanterv.pk]))
            for mtt in response.context['mintatantervtargyak']:
                targy = mtt.targy
                self.assertEqual(mtt.melytargyelofeltetele,
                                 list(targy.ezentargyakelofelteteletipussal.filter(mintatanterv=tanterv)))
                self.assertEqual(sorted(m.pk for m in mtt.melymintatantervtargyelofeltetele),
                                 sorted(m.pk for m in targy.ezenmintatantervtargyakelofelteteletipussal
                                        .filter(mintatanterv=tanterv)))

    def test_lekerdezesek_szama_nem_no(self):
        tanterv = self.adatok.mintatantervek[0]
        url = reverse('mintatanterv', args=[tanterv.pk])
        elotte = lekerdezesek_szama(self.client, url)
        self.adatok.mintatantervbe(tanterv, self.adatok.targyak_hozzaadasa(10))
        self.assertEqual(lekerdezesek_szama(self.client, url), elotte)

    def test_mintatantervek_listaja(self):
        response = self.client.get(reverse('mintatantervek'))
        for tanterv in self.adatok.mintatantervek:
            self.assertContains(response, 'href="%s"' % tanterv.get_absolute_url())
        szak = response.context['kepzesek'][0].szakok[0]
        self.assertEqual(szak.mintatantervek, list(Mintatanterv.objects.filter(szak=szak)))


class OktatoKurzusaiTests(MintatantervTestCase):
    def test_oktato_kurzusai(self):
        for felev in FELEVEK:
            for oktato in self.adatok.oktatok:
                response = self.client.get(reverse('oktato_kurzusai_' + felev, args=[oktato.pk]))
                vart = set(_felev_kurzusai(felev).exclude(kurzuskod__icontains='-KV').filter(oktato=oktato))
                megjelent = {k for t in response.context['targyak'] for k in t.felev_kurzusai}
                self.assertEqual(megjelent, vart)
                for targy in response.context['targyak']:
                    aktualis = [MintatantervTargy.objects.get(mintatanterv=m, targy=targy)
                                for m in targy.mintatanterv.filter(aktualis=True)]
                    self.assertEqual(targy.mintatantervek_felevekkel,
                                     ['%s: %s. félév' % (m.mintatanterv.kod, m.felev) for m in aktualis])

    def test_oktatok_listaja_es_linkek(self):
        response = self.client.get(reverse('oktatok_kurzusai_tavasz'))
        self.assertContains(response, 'A tavaszi félév kurzusainak oktatói')
        oktato = response.context['oktatok'][0]
        self.assertContains(response, 'href="/mintatantervek/tavaszi_kurzusok/%d/"' % oktato.pk)
        self.assertContains(response, 'href="/mintatantervek/tavaszi_kurzusok/letoltes/"')

    def test_lekerdezesek_szama_nem_no(self):
        oktato = self.adatok.oktatok[0]
        url = reverse('oktato_kurzusai_osz', args=[oktato.pk])
        elotte = lekerdezesek_szama(self.client, url)
        tanterv = self.adatok.mintatantervek[0]
        self.adatok.mintatantervbe(tanterv, self.adatok.targyak_hozzaadasa(12))
        self.assertEqual(lekerdezesek_szama(self.client, url), elotte)

    def test_hallgatonak_nem_elerheto(self):
        self.client.force_login(self.users['student'])
        self.assertEqual(self.client.get(reverse('oktatok_kurzusai_osz')).status_code, 302)
        self.assertEqual(self.client.get(reverse('jegyzetfelelosok')).status_code, 302)


class XlsxTests(MintatantervTestCase):
    def test_kurzuslista(self):
        for felev, munkalap in [('osz', 'oszi_kurzusok'), ('tavasz', 'tavaszi_kurzusok')]:
            response = self.client.get(reverse('xlsx_oktatok_kurzusai_' + felev))
            self.assertEqual(response['Content-Disposition'], 'attachment; filename=%s_listaja.xlsx' % munkalap)
            workbook = zipfile.ZipFile(io.BytesIO(response.content)).read('xl/workbook.xml').decode()
            self.assertIn('name="%s"' % munkalap, workbook)
            sorok = xlsx_sorok(response.content)
            self.assertEqual(sorok[0], XLSX_FEJLEC)
            vart = sum(k.targy.mintatanterv.filter(aktualis=True).count() * k.oktato.count()
                       for k in _felev_kurzusai(felev))
            self.assertEqual(len(sorok) - 1, vart)

    def test_lekerdezesek_szama_nem_no(self):
        url = reverse('xlsx_oktatok_kurzusai_osz')
        elotte = lekerdezesek_szama(self.client, url)
        self.adatok.mintatantervbe(self.adatok.mintatantervek[1], self.adatok.targyak_hozzaadasa(10))
        self.assertEqual(lekerdezesek_szama(self.client, url), elotte)

    def test_neptun_kodok(self):
        nappali, levelezo = Munkarend(nev='nappali'), Munkarend(nev='levelező')
        for kod, munkarend, vart in [('J14', nappali, 'JN14'), ('J14', levelezo, 'JL14'), ('MT17', levelezo, 'MTN17'),
                                     ('SZAJBA17', levelezo, 'SZAJBA17-L'), ('GM17', nappali, 'GM17')]:
            kurzus = TargyMunkarend(munkarend=munkarend)
            self.assertEqual(_neptun_mintatanterv_kod(Mintatanterv(kod=kod), kurzus), vart)

    def test_csak_munkatarsaknak(self):
        self.client.force_login(self.users['oktato'])
        self.assertEqual(self.client.get(reverse('xlsx_oktatok_kurzusai_osz')).status_code, 302)

    def test_naplo(self):
        kurzus = TargyMunkarend.objects.filter(orarend_oraszam__gt=0).order_by('pk').first()
        response = self.client.get(reverse('kurzus_naplo', args=[kurzus.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(kurzus.kurzuskod, response['Content-Disposition'])
