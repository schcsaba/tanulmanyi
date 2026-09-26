import shutil
import tempfile
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from orarend import views
from orarend.models import Beallitas, OrarendFajl
from tanulmanyi.testing import create_orarend, create_users

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class OrarendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = create_users()
        create_orarend(MEDIA_ROOT, hetek=3)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        views._feldolgoz.cache_clear()
        self.client.force_login(self.users['student'])

    def test_nevsorok(self):
        self.assertEqual(self.client.get(reverse('orarendi_oktatok')).context['oktato_nevek'], ['Tanár Anna', 'Tanár Béla'])
        self.assertEqual(self.client.get(reverse('evfolyamok')).context['evfolyam_nevek'], ['1. évfolyam', '2. évfolyam'])

    def test_oktato_orarendje(self):
        response = self.client.get(reverse('oktato_orarendje', args=[0]))
        self.assertEqual(response.context['oktato_neve'], 'Tanár Anna')
        orarendek = response.context['orarendek']
        self.assertEqual(len(orarendek), 3)
        for het, orarend in enumerate(orarendek, 1):
            self.assertIn('Mikro %d' % het, orarend)
            self.assertNotIn('<caption>', orarend)
            self.assertNotIn('studentsset', orarend)
            self.assertNotIn('Tanár Anna', orarend)
        # A szünet (2.) hét után a hetek számozása eggyel eltolódik.
        self.assertContains(response, '<h3>1. hét</h3>', html=True)
        self.assertContains(response, '<h3>3. hét</h3>', html=True)
        self.assertContains(response, '<h3>4. hét</h3>', html=True)

    def test_evfolyam_orarendje_megjegyzesekkel(self):
        response = self.client.get(reverse('evfolyam_orarendje', args=[0]))
        self.assertEqual(response.context['evfolyam_neve'], '1. évfolyam')
        self.assertIn('Megjegyzés 1', response.context['megjegyzesek'])

    def test_nem_letezo_index(self):
        self.assertEqual(self.client.get(reverse('oktato_orarendje', args=[5])).status_code, 404)

    def test_fajlonkent_egyszer_dolgozza_fel(self):
        with mock.patch.object(views, 'BeautifulSoup', wraps=views.BeautifulSoup) as soup:
            self.client.get(reverse('oktato_orarendje', args=[0]))
            self.client.get(reverse('oktato_orarendje', args=[1]))
            self.client.get(reverse('orarendi_oktatok'))
        self.assertEqual(soup.call_count, 3)

    def test_nincs_orarend(self):
        OrarendFajl.objects.update(aktiv=False)
        for url in (reverse('orarendi_oktatok'), reverse('evfolyam_orarendje', args=[0])):
            self.assertEqual(self.client.get(url).context['visszajelzes'], 'Az órarend még nem érhető el.')

    def test_nincs_szunet_beallitas(self):
        Beallitas.objects.filter(nev='Szünet').delete()
        response = self.client.get(reverse('oktato_orarendje', args=[0]))
        self.assertEqual(response.context['visszajelzes'], 'Az órarend még nem érhető el.')

    def test_naptarak(self):
        self.assertContains(self.client.get(reverse('osz')), 'spreadsheets/d/oszi-sheet-id/')
        Beallitas.objects.filter(nev='Tavasz').delete()
        self.assertEqual(self.client.get(reverse('tavasz')).context['visszajelzes'],
                         'Az oktatási naptár még nem érhető el.')
