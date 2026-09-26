from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from mintatanterv.models import TargyMunkarend
from tanulmanyi.testing import MintatantervAdatok, SzakdolgozatAdatok, create_users


class BejelentkezesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('valaki', password='jelszo123')

    def test_sikeres(self):
        response = self.client.post(reverse('auth_view'), {'username': 'valaki', 'password': 'jelszo123'})
        self.assertRedirects(response, '/accounts/loggedin', fetch_redirect_response=False)

    def test_hibas_jelszo(self):
        response = self.client.post(reverse('auth_view'), {'username': 'valaki', 'password': 'rossz'})
        self.assertRedirects(response, '/accounts/invalid', fetch_redirect_response=False)

    def test_inaktiv_felhasznalo(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse('auth_view'), {'username': 'valaki', 'password': 'jelszo123'})
        self.assertRedirects(response, '/accounts/invalid', fetch_redirect_response=False)

    def test_csak_post(self):
        self.assertEqual(self.client.get(reverse('auth_view')).status_code, 405)


class MenuTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users = create_users()

    def test_oktatoi_menupontok(self):
        self.client.force_login(self.users['oktato'])
        self.assertContains(self.client.get('/'), 'Jegyzetfelelősök')
        self.client.force_login(self.users['student'])
        self.assertNotContains(self.client.get('/'), 'Jegyzetfelelősök')


class AdminTests(TestCase):
    """Every admin list and add page renders, with the test data in place."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin', password='x')
        SzakdolgozatAdatok().temavezetok_hozzaadasa(4)
        MintatantervAdatok()

    def setUp(self):
        self.client.force_login(self.admin)

    def test_listak_es_urlapok(self):
        for model in admin.site._registry:
            info = model._meta.app_label, model._meta.model_name
            for view in ('changelist', 'add'):
                with self.subTest(model=model.__name__, view=view):
                    self.assertEqual(self.client.get(reverse('admin:%s_%s_%s' % (info + (view,)))).status_code, 200)

    def test_letszam_akciok(self):
        url = reverse('admin:mintatanterv_targymunkarend_changelist')
        response = self.client.get(url)
        self.assertContains(response, 'Állítsd a kiválasztott kurzusok maximális létszámát 20-ra')
        self.assertContains(response, 'Állítsd a kiválasztott kurzusok maximális létszámát 25-re')
        kurzusok = TargyMunkarend.objects.order_by('pk')[:2]
        response = self.client.post(url, {'action': 'max_letszam_20', '_selected_action': [k.pk for k in kurzusok]},
                                    follow=True)
        self.assertContains(response, '2 kurzus létszáma lett 20-ra állítva.')
        self.assertEqual({k.max_letszam for k in TargyMunkarend.objects.filter(pk__in=[k.pk for k in kurzusok])}, {20})
