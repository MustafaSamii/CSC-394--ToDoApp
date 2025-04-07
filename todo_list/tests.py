from django.test import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class LandingPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')

    def test_app_name_and_about_link(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'DePaul ToDo App')
        self.assertContains(response, 'About')

    def test_logo_displayed(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'depaul_logo.png')  # ensures that the depaul logo is rendered

    def test_email_shown_for_logged_in_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('landing'))
        self.assertContains(response, self.user.email)

    def test_login_button_for_anonymous_user(self):
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'Login')

    def test_login_button_redirect(self):
        response = self.client.get('/login/', follow=True)
        self.assertIn(response.status_code, [200, 302])  # allow both success and redirect