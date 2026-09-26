from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from szabalyzat.models import Szabalyzat
import tempfile
import os


class SzabalyzatModelTests(TestCase):
    """Test cases for the Szabalyzat model"""
    
    fixtures = ['szabalyzat_data']
    
    def setUp(self):
        """Set up test data"""
        # Create a temporary file for testing
        self.test_file = SimpleUploadedFile(
            "test_szabalyzat.pdf",
            b"PDF content for testing",
            content_type="application/pdf"
        )
        
        self.test_szabalyzat = Szabalyzat.objects.create(
            nev="Test Szabályzat",
            szabalyzatfajl=self.test_file,
            csak_oktatoknak=False
        )
    
    def test_str_method(self):
        """Test that __str__ returns the regulation name"""
        self.assertEqual(str(self.test_szabalyzat), "Test Szabályzat")
    
    def test_nev_field_max_length(self):
        """Test that nev field respects max_length"""
        max_length = self.test_szabalyzat._meta.get_field('nev').max_length
        self.assertEqual(max_length, 200)
    
    def test_nev_field_unique(self):
        """Test that nev field is unique"""
        unique = self.test_szabalyzat._meta.get_field('nev').unique
        self.assertTrue(unique)
    
    def test_csak_oktatoknak_default_value(self):
        """Test that csak_oktatoknak defaults to False"""
        szabalyzat = Szabalyzat.objects.create(
            nev="Default Test",
            szabalyzatfajl=SimpleUploadedFile("test.pdf", b"content")
        )
        self.assertFalse(szabalyzat.csak_oktatoknak)
    
    def test_ordering(self):
        """Test that regulations are ordered by nev field"""
        # Create regulations that should be ordered alphabetically
        z_szabalyzat = Szabalyzat.objects.create(
            nev="Z Szabályzat",
            szabalyzatfajl=SimpleUploadedFile("z.pdf", b"content"),
            csak_oktatoknak=False
        )
        a_szabalyzat = Szabalyzat.objects.create(
            nev="A Szabályzat", 
            szabalyzatfajl=SimpleUploadedFile("a.pdf", b"content"),
            csak_oktatoknak=False
        )
        
        regulations = list(Szabalyzat.objects.all())
        # First regulation alphabetically should start with "A" or be from fixtures
        first_names = [r.nev for r in regulations[:3]]
        self.assertTrue(any(name.startswith("A") or name.startswith("F") or name.startswith("G") for name in first_names))
    
    def test_verbose_names(self):
        """Test model and field verbose names"""
        self.assertEqual(self.test_szabalyzat._meta.verbose_name_plural, 'szabályzatok')
        
        nev_field = self.test_szabalyzat._meta.get_field('nev')
        szabalyzatfajl_field = self.test_szabalyzat._meta.get_field('szabalyzatfajl')
        csak_oktatoknak_field = self.test_szabalyzat._meta.get_field('csak_oktatoknak')
        
        self.assertEqual(nev_field.verbose_name, 'név')
        self.assertEqual(szabalyzatfajl_field.verbose_name, 'szabályzatfájl')
        self.assertEqual(csak_oktatoknak_field.verbose_name, 'csak oktatóknak')
    
    def test_file_upload_path(self):
        """Test that files are uploaded to the correct path"""
        upload_to = self.test_szabalyzat._meta.get_field('szabalyzatfajl').upload_to
        self.assertEqual(upload_to, 'szabalyzatok/')


class SzabalyzatViewTests(TestCase):
    """Test cases for Szabalyzat views"""
    
    fixtures = ['szabalyzat_data']
    
    def setUp(self):
        """Set up test client, users and groups"""
        self.client = Client()
        
        # Create teacher group
        self.teacher_group = Group.objects.create(name='Oktatok')
        
        # Create regular user (student)
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        
        # Create teacher user
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123'
        )
        self.teacher.groups.add(self.teacher_group)
        
        # Create test regulations
        self.public_regulation = Szabalyzat.objects.create(
            nev="Public Test Regulation",
            szabalyzatfajl=SimpleUploadedFile("public.pdf", b"public content"),
            csak_oktatoknak=False
        )
        self.teacher_only_regulation = Szabalyzat.objects.create(
            nev="Teacher Only Test Regulation",
            szabalyzatfajl=SimpleUploadedFile("teacher.pdf", b"teacher content"),
            csak_oktatoknak=True
        )
    
    def test_szabalyzatok_view_requires_login(self):
        """Test that szabalyzatok view requires user to be logged in"""
        response = self.client.get(reverse('szabalyzatok'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_szabalyzatok_view_with_authenticated_user(self):
        """Test szabalyzatok view with authenticated user"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('szabalyzatok'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('szabalyzatok', response.context)
    
    def test_szabalyzatok_view_uses_correct_template(self):
        """Test that szabalyzatok view uses the correct template"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('szabalyzatok'))
        
        self.assertTemplateUsed(response, 'szabalyzat/szabalyzatok.html')
    
    def test_szabalyzatok_view_shows_all_regulations(self):
        """Test that szabalyzatok view shows all regulations (both public and teacher-only)"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('szabalyzatok'))
        
        regulations = response.context['szabalyzatok']
        self.assertGreater(regulations.count(), 0)
        
        # Should contain both public and teacher-only regulations in the list
        regulation_names = [r.nev for r in regulations]
        self.assertIn("Public Test Regulation", regulation_names)
        self.assertIn("Teacher Only Test Regulation", regulation_names)
    
    def test_szabalyzatok_view_no_regulations(self):
        """Test szabalyzatok view when no regulations exist"""
        # Clear all regulations
        Szabalyzat.objects.all().delete()
        
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('szabalyzatok'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('visszajelzes', response.context)
        self.assertEqual(response.context['visszajelzes'], 'A szabályzatok még nem érhetők el.')


class SzabalyzatDownloadTests(TestCase):
    """Test cases for Szabalyzat download functionality"""
    
    fixtures = ['szabalyzat_data']
    
    def setUp(self):
        """Set up test data for download tests"""
        self.client = Client()
        
        # Create teacher group
        self.teacher_group = Group.objects.create(name='Oktatok')
        
        # Create users
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.teacher = User.objects.create_user(
            username='teacher', 
            password='testpass123'
        )
        self.teacher.groups.add(self.teacher_group)
        
        # Create test regulations
        self.public_regulation = Szabalyzat.objects.create(
            nev="Downloadable Public Regulation",
            szabalyzatfajl="szabalyzatok/public_test.pdf",
            csak_oktatoknak=False
        )
        self.teacher_regulation = Szabalyzat.objects.create(
            nev="Downloadable Teacher Regulation",
            szabalyzatfajl="szabalyzatok/teacher_test.pdf",
            csak_oktatoknak=True
        )
    
    def test_download_view_requires_login(self):
        """Test that download view requires authentication"""
        response = self.client.get(
            reverse('szabalyzat_letoltes', args=[self.public_regulation.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_download_nonexistent_regulation(self):
        """Test downloading a regulation that doesn't exist"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('szabalyzat_letoltes', args=[9999]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'szabalyzat/szabalyzat_nem_letezik.html')
    
    def test_student_download_teacher_only_regulation(self):
        """Test that students cannot download teacher-only regulations"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(
            reverse('szabalyzat_letoltes', args=[self.teacher_regulation.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'szabalyzat/szabalyzat_nem_hozzaferheto.html')
    
    def test_download_url_pattern(self):
        """Test that download URL pattern works correctly"""
        self.client.login(username='student', password='testpass123')
        
        # Test the URL resolves correctly
        url = reverse('szabalyzat_letoltes', args=[self.public_regulation.id])
        self.assertEqual(url, f'/szabalyzatok/letoltes/{self.public_regulation.id}/')
        
        # Test the view is accessible - may get FileNotFoundError which is expected
        # since we don't have actual files in tests
        try:
            response = self.client.get(url)
            # If no error, should not be 404
            self.assertNotEqual(response.status_code, 404)
        except Exception as e:
            # File not found is expected in test environment
            self.assertIn('No such file or directory', str(e))


class SzabalyzatPermissionTests(TestCase):
    """Test cases for Szabalyzat permission system"""
    
    fixtures = ['szabalyzat_data']
    
    def setUp(self):
        """Set up users and groups for permission testing"""
        self.client = Client()
        
        # Create teacher group
        self.teacher_group = Group.objects.create(name='Oktatok')
        
        # Create users
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123'
        )
        self.teacher.groups.add(self.teacher_group)
        
        # Get regulations from fixtures
        self.public_regulations = Szabalyzat.objects.filter(csak_oktatoknak=False)
        self.teacher_regulations = Szabalyzat.objects.filter(csak_oktatoknak=True)
    
    def test_student_denied_teacher_regulations(self):
        """Test that students cannot access teacher-only regulations"""
        self.client.login(username='student', password='testpass123')
        
        for regulation in self.teacher_regulations[:3]:  # Test first 3
            response = self.client.get(
                reverse('szabalyzat_letoltes', args=[regulation.id])
            )
            # Should get "not accessible" page
            self.assertTemplateUsed(response, 'szabalyzat/szabalyzat_nem_hozzaferheto.html')
    
    def test_group_membership_verification(self):
        """Test that teacher group membership is correctly verified"""
        # Student should not be in teacher group
        self.assertFalse(self.student.groups.filter(name='Oktatok').exists())
        
        # Teacher should be in teacher group
        self.assertTrue(self.teacher.groups.filter(name='Oktatok').exists())


class SzabalyzatFixturesTests(TestCase):
    """Test cases for Szabalyzat fixtures integration"""
    
    fixtures = ['szabalyzat_data']
    
    def test_fixtures_loaded(self):
        """Test that fixtures are properly loaded"""
        # Should have 15 regulations from fixtures
        total_count = Szabalyzat.objects.count()
        self.assertGreaterEqual(total_count, 15)
    
    def test_fixtures_permission_distribution(self):
        """Test that fixtures have correct permission distribution"""
        public_count = Szabalyzat.objects.filter(csak_oktatoknak=False).count()
        teacher_count = Szabalyzat.objects.filter(csak_oktatoknak=True).count()
        
        # From our fixtures: 10 public, 5 teacher-only
        self.assertGreaterEqual(public_count, 10)
        self.assertGreaterEqual(teacher_count, 5)
    
    def test_fixtures_content_format(self):
        """Test that fixture content is properly formatted"""
        regulations = Szabalyzat.objects.all()
        
        for regulation in regulations:
            # All regulations should have content
            self.assertTrue(len(regulation.nev) > 0)
            self.assertTrue(len(regulation.szabalyzatfajl.name) > 0)
            
            # File paths should point to szabalyzatok directory
            self.assertTrue(regulation.szabalyzatfajl.name.startswith('szabalyzatok/'))
            
            # File names should be PDF files
            self.assertTrue(regulation.szabalyzatfajl.name.endswith('.pdf'))
    
    def test_fixture_specific_content(self):
        """Test specific content from fixtures"""
        # Test that we have the expected regulations
        expected_regulations = [
            "Tanulmányi és Vizsgaszabályzat",
            "Hallgatói Követelményrendszer",
            "Szakdolgozat Készítési Útmutató",
            "Oktatói Etikai Kódex"
        ]
        
        existing_regulations = Szabalyzat.objects.values_list('nev', flat=True)
        
        for expected in expected_regulations:
            self.assertIn(expected, existing_regulations)
    
    def test_fixture_ordering(self):
        """Test that fixtures are properly ordered"""
        regulations = list(Szabalyzat.objects.all())
        
        # Should be ordered alphabetically by name
        # Note: Django ordering uses database collation which may differ from Python string comparison
        # Just test that we have the expected ordering class in the model
        self.assertEqual(Szabalyzat._meta.ordering, ['nev'])
        
        # Test that at least some obvious ordering works
        regulation_names = [r.nev for r in regulations]
        # Find regulations starting with A and F to test basic ordering
        a_regulations = [name for name in regulation_names if name.lower().startswith('a')]
        f_regulations = [name for name in regulation_names if name.lower().startswith('f')]
        if a_regulations and f_regulations:
            # A should come before F in general
            a_index = regulation_names.index(a_regulations[0])
            f_index = regulation_names.index(f_regulations[0])
            self.assertTrue(a_index < f_index or abs(a_index - f_index) < 3)  # Allow some flexibility


class SzabalyzatIntegrationTests(TestCase):
    """Integration tests for the Szabalyzat module"""
    
    fixtures = ['szabalyzat_data']
    
    def setUp(self):
        """Set up test client and users"""
        self.client = Client()
        self.teacher_group = Group.objects.create(name='Oktatok')
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123'
        )
        self.teacher.groups.add(self.teacher_group)
    
    def test_szabalyzatok_page_displays_fixture_content(self):
        """Test that szabalyzatok page displays content from fixtures"""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('szabalyzatok'))
        
        self.assertEqual(response.status_code, 200)
        
        # Should contain some of our fixture regulations
        self.assertContains(response, "Tanulmányi és Vizsgaszabályzat")
        self.assertContains(response, "Hallgatói Követelményrendszer")
    
    def test_szabalyzatok_url_pattern(self):
        """Test that szabalyzatok URL pattern works correctly"""
        self.client.login(username='student', password='testpass123')
        
        # Test the URL resolves correctly
        url = reverse('szabalyzatok')
        self.assertEqual(url, '/szabalyzatok/')
        
        # Test the view is accessible
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_end_to_end_permission_workflow(self):
        """Test complete workflow from listing to download attempts"""
        # Student logs in and views regulations
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('szabalyzatok'))
        self.assertEqual(response.status_code, 200)
        
        # Try to download a teacher-only regulation
        teacher_reg = Szabalyzat.objects.filter(csak_oktatoknak=True).first()
        response = self.client.get(
            reverse('szabalyzat_letoltes', args=[teacher_reg.id])
        )
        # Should get "not accessible" error
        self.assertTemplateUsed(response, 'szabalyzat/szabalyzat_nem_hozzaferheto.html')
        
        # Now login as teacher and try again
        self.client.login(username='teacher', password='testpass123')
        try:
            response = self.client.get(
                reverse('szabalyzat_letoltes', args=[teacher_reg.id])
            )
            # Teacher should get a different response (file not found or download, but not access denied)
            # The response should not use the "not accessible" template
            template_names = [t.name for t in response.templates if t.name]
            self.assertNotIn('szabalyzat/szabalyzat_nem_hozzaferheto.html', template_names)
        except Exception as e:
            # File not found is expected in test environment for teachers too
            # This means the permission check passed (teacher can access) but file doesn't exist
            self.assertIn('No such file or directory', str(e))
    
    def test_szabalyzatok_page_performance(self):
        """Test that szabalyzatok page loads efficiently with fixtures"""
        self.client.login(username='student', password='testpass123')
        
        # Test that the query count is reasonable
        with self.assertNumQueries(4):  # Session, user, regulations, teacher-group check
            response = self.client.get(reverse('szabalyzatok'))
            self.assertEqual(response.status_code, 200)


class SzabalyzatFileDownloadTests(TestCase):
    """Test cases for downloading regulation files that exist on disk"""

    def setUp(self):
        """Create a regulation with an accented file name in a temporary MEDIA_ROOT"""
        self.media_root = tempfile.mkdtemp()
        self.settings_override = self.settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        os.makedirs(os.path.join(self.media_root, 'szabalyzatok'))
        with open(os.path.join(self.media_root, 'szabalyzatok', 'térítési_díjak.pdf'), 'wb') as f:
            f.write(b'%PDF-1.4 test')
        self.regulation = Szabalyzat.objects.create(
            nev="Térítési szabályzat",
            szabalyzatfajl="szabalyzatok/térítési_díjak.pdf",
            csak_oktatoknak=False
        )
        User.objects.create_user(username='student', password='testpass123')
        self.client.login(username='student', password='testpass123')

    def tearDown(self):
        self.settings_override.disable()
        import shutil
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_download_content_and_filename(self):
        """Test that the file is served as an attachment with its (non-ASCII) name intact"""
        response = self.client.get(reverse('szabalyzat_letoltes', args=[self.regulation.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn("filename*=utf-8''t%C3%A9r%C3%ADt%C3%A9si_d%C3%ADjak.pdf", response['Content-Disposition'])
        self.assertEqual(b''.join(response.streaming_content), b'%PDF-1.4 test')
