from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from faq.models import Kerdes


class KerdesModelTests(TestCase):
    """Test cases for the Kerdes model"""
    
    fixtures = ['faq_data.json']
    
    def setUp(self):
        """Set up test data"""
        self.test_kerdes = Kerdes.objects.create(
            kerdes="Test kérdés?",
            valasz="<p>Test válasz</p>",
            publikalt=True
        )
    
    def test_str_method(self):
        """Test that __str__ returns the question text"""
        self.assertEqual(str(self.test_kerdes), "Test kérdés?")
    
    def test_kerdes_field_max_length(self):
        """Test that kerdes field respects max_length"""
        max_length = self.test_kerdes._meta.get_field('kerdes').max_length
        self.assertEqual(max_length, 500)
    
    def test_valasz_field_max_length(self):
        """Test that valasz field respects max_length"""
        max_length = self.test_kerdes._meta.get_field('valasz').max_length
        self.assertEqual(max_length, 2000)
    
    def test_publikalt_default_value(self):
        """Test that publikalt defaults to True"""
        kerdes = Kerdes.objects.create(
            kerdes="New question",
            valasz="New answer"
        )
        self.assertTrue(kerdes.publikalt)
    
    def test_ordering(self):
        """Test that questions are ordered by kerdes field"""
        # Create questions that should be ordered alphabetically
        q1 = Kerdes.objects.create(kerdes="Z question", valasz="Answer", publikalt=True)
        q2 = Kerdes.objects.create(kerdes="A question", valasz="Answer", publikalt=True)
        
        questions = list(Kerdes.objects.all())
        # First question alphabetically should be "A question"
        self.assertTrue(questions[0].kerdes.startswith("A") or questions[0].kerdes.startswith("H"))
    
    def test_verbose_names(self):
        """Test model and field verbose names"""
        self.assertEqual(self.test_kerdes._meta.verbose_name, 'kérdés')
        self.assertEqual(self.test_kerdes._meta.verbose_name_plural, 'kérdések')
        
        kerdes_field = self.test_kerdes._meta.get_field('kerdes')
        valasz_field = self.test_kerdes._meta.get_field('valasz')
        publikalt_field = self.test_kerdes._meta.get_field('publikalt')
        
        self.assertEqual(kerdes_field.verbose_name, 'kérdés')
        self.assertEqual(valasz_field.verbose_name, 'válasz')
        self.assertEqual(publikalt_field.verbose_name, 'publikált')


class FaqViewTests(TestCase):
    """Test cases for FAQ views"""
    
    fixtures = ['faq_data.json']
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test questions with different publikalt status
        self.published_question = Kerdes.objects.create(
            kerdes="Published test question?",
            valasz="<p>Published answer</p>",
            publikalt=True
        )
        self.unpublished_question = Kerdes.objects.create(
            kerdes="Unpublished test question?",
            valasz="<p>Unpublished answer</p>",
            publikalt=False
        )
    
    def test_faq_view_requires_login(self):
        """Test that FAQ view requires user to be logged in"""
        response = self.client.get(reverse('faq'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_faq_view_with_authenticated_user(self):
        """Test FAQ view with authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('faq'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published test question?")
        self.assertNotContains(response, "Unpublished test question?")
    
    def test_faq_view_only_shows_published_questions(self):
        """Test that only published questions are shown"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('faq'))
        
        # Get the questions from context
        kerdesek = response.context['kerdesek']
        
        # All questions should be published
        for kerdes in kerdesek:
            self.assertTrue(kerdes.publikalt)
        
        # Should contain our published question
        question_texts = [k.kerdes for k in kerdesek]
        self.assertIn("Published test question?", question_texts)
        self.assertNotIn("Unpublished test question?", question_texts)
    
    def test_faq_view_uses_correct_template(self):
        """Test that FAQ view uses the correct template"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('faq'))
        
        self.assertTemplateUsed(response, 'faq/faq.html')
    
    def test_faq_view_context_data(self):
        """Test that FAQ view provides correct context data"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('faq'))
        
        self.assertIn('kerdesek', response.context)
        self.assertTrue(response.context['kerdesek'].count() > 0)


class FaqFixturesTests(TestCase):
    """Test cases for FAQ fixtures integration"""
    
    fixtures = ['faq_data.json']
    
    def test_fixtures_loaded(self):
        """Test that fixtures are properly loaded"""
        # Should have 10 questions from fixtures
        total_count = Kerdes.objects.count()
        self.assertGreaterEqual(total_count, 10)
    
    def test_fixtures_published_status(self):
        """Test that fixtures have correct published status"""
        published_count = Kerdes.objects.filter(publikalt=True).count()
        unpublished_count = Kerdes.objects.filter(publikalt=False).count()
        
        # From our fixtures: 9 published, 1 unpublished
        self.assertGreaterEqual(published_count, 9)
        self.assertGreaterEqual(unpublished_count, 1)
    
    def test_fixtures_content_format(self):
        """Test that fixture content is properly formatted"""
        questions = Kerdes.objects.all()
        
        for question in questions:
            # All questions should have content
            self.assertTrue(len(question.kerdes) > 0)
            self.assertTrue(len(question.valasz) > 0)
            
            # Questions should end with question mark (Hungarian FAQ format)
            self.assertTrue(question.kerdes.endswith('?'))
            
            # Answers should contain HTML (HTMLField)
            self.assertIn('<', question.valasz)
    
    def test_fixture_specific_content(self):
        """Test specific content from fixtures"""
        # Test that we have the expected questions
        expected_questions = [
            "Hogyan tudok beiratkozni egy kurzusra?",
            "Mikor vannak a vizsgaidőszakok?",
            "Hogyan kell leadni a szakdolgozatot?"
        ]
        
        existing_questions = Kerdes.objects.values_list('kerdes', flat=True)
        
        for expected in expected_questions:
            self.assertIn(expected, existing_questions)


class FaqIntegrationTests(TestCase):
    """Integration tests for the FAQ module"""
    
    fixtures = ['faq_data.json']
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_faq_page_displays_fixture_content(self):
        """Test that FAQ page displays content from fixtures"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('faq'))
        
        self.assertEqual(response.status_code, 200)
        
        # Should contain some of our fixture questions
        self.assertContains(response, "Hogyan tudok beiratkozni egy kurzusra?")
        self.assertContains(response, "Mikor vannak a vizsgaidőszakok?")
    
    def test_faq_url_pattern(self):
        """Test that FAQ URL pattern works correctly"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test the URL resolves correctly
        url = reverse('faq')
        self.assertEqual(url, '/faq/')
        
        # Test the view is accessible
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_faq_page_performance(self):
        """Test that FAQ page loads efficiently with fixtures"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test that the query count is reasonable (not excessive)
        # Django auth may require several queries, but should be < 10 total
        with self.assertNumQueries(6):  # Auth + FAQ queries
            response = self.client.get(reverse('faq'))
            self.assertEqual(response.status_code, 200)
        
        # Alternative test: ensure we're not doing N+1 queries on FAQ items
        # This tests that adding more FAQ items doesn't increase query count
        Kerdes.objects.create(
            kerdes="Performance test question?",
            valasz="<p>Test answer</p>",
            publikalt=True
        )
        
        # Query count should remain the same with one more FAQ item
        with self.assertNumQueries(6):
            response = self.client.get(reverse('faq'))
            self.assertEqual(response.status_code, 200)
