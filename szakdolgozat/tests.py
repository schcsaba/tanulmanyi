from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from szakdolgozat.models import ErdemJegy, HallgatoKepzesTema, Tema, Temavezeto
from tanulmanyi.testing import SzakdolgozatAdatok, create_users


def lekerdezesek_szama(client, url):
    with CaptureQueriesContext(connection) as ctx:
        response = client.get(url)
    assert response.status_code == 200, (url, response.status_code)
    return len(ctx.captured_queries)


class SzakdolgozatTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = create_users()
        cls.adatok = SzakdolgozatAdatok()
        cls.adatok.temavezetok_hozzaadasa(8)

    def setUp(self):
        self.client.force_login(self.users['oktato'])

    def assert_lekerdezesek_nem_nonek(self, url):
        """Adding more data must not add queries (no per-row queries)."""
        elotte = lekerdezesek_szama(self.client, url)
        self.adatok.temavezetok_hozzaadasa(5)
        self.assertEqual(lekerdezesek_szama(self.client, url), elotte)


class AktivTemavezetokTests(SzakdolgozatTestCase):
    url = reverse('aktiv_temavezetok')

    def test_csak_aktiv_temavezetok_nev_szerint(self):
        temavezetok = self.client.get(self.url).context['aktiv_temavezetok']
        self.assertEqual(temavezetok, list(Temavezeto.objects.filter(inaktiv=False)))

    def test_szamlalok_egyeznek_a_soronkenti_szamitassal(self):
        response = self.client.get(self.url)
        osszes = 0
        for tv in response.context['aktiv_temavezetok']:
            hkt = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto=tv,
                                                    szakdolgozat_targyat_felvett=True)
            self.assertEqual(tv.szakd_targyat_felvett, hkt.count())
            self.assertEqual(tv.ma_szakdolgozatok_szama, hkt.filter(hallgato_kepzes__kepzes__kepzes_kod='MTN').count())
            self.assertEqual(tv.foglalt_helyek, Tema.foglalt.filter(temavezeto_temakor__temavezeto=tv).count())
            self.assertEqual(tv.szabad_helyek, tv.max_letszam - hkt.count() - tv.ma_szakdolgozatok_szama)
            osszes += max(tv.szabad_helyek, 0)
            self.assertEqual(tv.valaszthato_temakorok_lista, list(tv.valaszthato_temakorok()))
            for tt in tv.valaszthato_temakorok_lista:
                self.assertEqual(tt.nem_megirt_temak_lista, list(tt.nem_megirt_temak()))
                self.assertEqual(tt.szabad_plusz_temak_lista, list(tt.szabad_plusz_temak()))
                self.assertEqual(tt.foglalt_temak_lista, list(tt.foglalt_temak()))
        self.assertEqual(response.context['osszes_szabad_hely'], osszes)

    def test_hallgatok_megjelennek(self):
        hkt = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto__inaktiv=False,
                                                tema__temavezeto_temakor__rejtett=False,
                                                tema__tema_statusz__in=[1, 2, 4, 6]).first()
        self.assertContains(self.client.get(self.url), str(hkt.hallgato_kepzes))

    def test_lekerdezesek_szama_nem_no(self):
        self.assert_lekerdezesek_nem_nonek(self.url)

    def test_bejelentkezes_kell(self):
        self.client.logout()
        self.assertRedirects(self.client.get(self.url), '/accounts/login/?next=' + self.url,
                             fetch_redirect_response=False)


class TemavezetokTests(SzakdolgozatTestCase):
    url = reverse('temavezetok')

    def test_valaszthato_temavezetok_szamlaloi(self):
        response = self.client.get(self.url)
        temavezetok = response.context['temavezetok']
        self.assertEqual(temavezetok, list(Temavezeto.objects.filter(valaszthato=True)))
        for tv in temavezetok:
            felvett = HallgatoKepzesTema.objects.filter(tema__temavezeto_temakor__temavezeto=tv,
                                                        szakdolgozat_targyat_felvett=True).count()
            self.assertEqual(tv.szabad_helyek, tv.max_letszam - felvett)
            self.assertEqual(tv.cimbejelento, Tema.cimbejelento.filter(temavezeto_temakor__temavezeto=tv).count())
            for tt in tv.valaszthato_temakorok_lista:
                self.assertEqual(tt.szabad_plusz_cimbejelento_temak_lista, list(tt.szabad_plusz_cimbejelento_temak()))
        self.assertEqual(response.context['osszes_szabad_hely'], sum(tv.szabad_helyek for tv in temavezetok))

    def test_lekerdezesek_szama_nem_no(self):
        self.assert_lekerdezesek_nem_nonek(self.url)

    def test_hallgato_nezet(self):
        self.client.force_login(self.users['student'])
        self.assert_lekerdezesek_nem_nonek(self.url)


class MegirtSzakdolgozatokTests(SzakdolgozatTestCase):
    def test_temavezetonkent(self):
        temavezetok = self.client.get(reverse('temavezetok_megirt')).context['temavezetok']
        self.assertEqual(temavezetok, list(Temavezeto.objects.all()))
        for tv in temavezetok:
            self.assertEqual(tv.megirt_temak_db, tv.megirt_temak_szama())
            for tt in tv.temakorok_lista:
                self.assertEqual(tt.megirt_temak_lista, list(tt.megirt_temak()))

    def test_erdemjegyenkent(self):
        response = self.client.get(reverse('megirtak_jegyenkent'))
        for jegy in response.context['erdemjegyek']:
            fresh = ErdemJegy.objects.get(pk=jegy.pk)
            self.assertEqual(list(jegy.hallgatokepzestema_set.all()), list(fresh.hallgatokepzestema_set.all()))

    def test_lekerdezesek_szama_nem_no(self):
        self.assert_lekerdezesek_nem_nonek(reverse('temavezetok_megirt'))
        self.assert_lekerdezesek_nem_nonek(reverse('megirtak_jegyenkent'))

    def test_hallgatonak_nem_elerheto(self):
        self.client.force_login(self.users['student'])
        for name in ('temavezetok_megirt', 'megirtak_jegyenkent'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 302)


class SzakdolgozatListaTests(SzakdolgozatTestCase):
    url = reverse('megirtesfolyamatban_pag_or_search')

    def test_lapozas(self):
        response = self.client.get(self.url, {'page': 2})
        self.assertEqual(response.context['paginatorpage'].number, 2)
        self.assertEqual(self.client.get(self.url, {'page': 'x'}).context['paginatorpage'].number, 1)
        utolso = response.context['paginator'].num_pages
        self.assertEqual(self.client.get(self.url, {'page': 999}).context['paginatorpage'].number, utolso)

    def test_tobb_szavas_kereses(self):
        response = self.client.get(self.url, {'cim': 'hosszú hosszú', 'hallgato': '', 'temavezeto': ''})
        talalatok = list(response.context['paginatorpage'])
        self.assertTrue(talalatok)
        self.assertTrue(all('hosszú hosszú' in hkt.tema.cim for hkt in talalatok))
        self.assertContains(response, 'value="hosszú hosszú"')
        self.assertEqual(response.context['kereses_query'], 'cim=hossz%C3%BA+hossz%C3%BA&hallgato=&temavezeto=')

    def test_hianyzo_kereso_parameterek(self):
        response = self.client.get(self.url, {'hallgato': 'H0001'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['paginator'].count)
        for hkt in response.context['paginatorpage']:
            self.assertIn('H0001', hkt.hallgato_kepzes.hallgato.neptun_kod)

    def test_repozitorium_csak_megvedett(self):
        response = self.client.get(reverse('szakdolgozatrepozitorium'))
        talalatok = list(response.context['paginatorpage'])
        self.assertTrue(talalatok)
        self.assertTrue(all(hkt.sikeres_vedes_datuma for hkt in talalatok))

    def test_lekerdezesek_szama_nem_no(self):
        self.assert_lekerdezesek_nem_nonek(self.url)
        self.assert_lekerdezesek_nem_nonek(reverse('szakdolgozatrepozitorium'))


class BeallitasOldalakTests(SzakdolgozatTestCase):
    def test_szovegek(self):
        self.assertContains(self.client.get(reverse('valaszthato_temavezetok')), '<p>Menet</p>', html=True)
        self.assertContains(self.client.get(reverse('szakdolgozat_kurzusok')), '<p>Kurzusok</p>', html=True)
        self.assertContains(self.client.get(reverse('zarovizsga_tetelek')), '<p>Tételek</p>', html=True)
