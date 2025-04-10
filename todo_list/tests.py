from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from todo_list.models import ToDo, Team
from django.utils import timezone
import datetime

# ------------------------------
# Landing Page Tests
# ------------------------------
class LandingPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )

    def test_app_name_and_about_link(self):  # T1
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'DePaul ToDo App')
        self.assertContains(response, 'About')

    def test_logo_displayed(self):  # T2
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'depaul_logo.png')  # ensures that the DePaul logo is rendered

    def test_email_shown_for_logged_in_user(self):  # T3
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('landing'))
        self.assertContains(response, self.user.email)

    def test_login_button_for_anonymous_user(self):  # T4
        response = self.client.get(reverse('landing'))
        self.assertContains(response, 'Login')

    def test_login_button_redirect(self):  # T5
        response = self.client.get('/login/', follow=True)
        self.assertIn(response.status_code, [200, 302])

# ------------------------------
# Registration Page Tests
# ------------------------------
class RegistrationPageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_renders(self):  # T1
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")

    def test_registration_form_fields_present(self):  # T3: Input fields for Email, Password1, and Password2 are present.
        response = self.client.get(reverse('register'))
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_successful_registration(self):  # T7: Valid input allows successful registration.
        response = self.client.post(reverse('register'), {
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        })
        # On success, registration redirects to the login page.
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_registration_with_mismatched_passwords(self):  # T6: Mismatched passwords should display an error.
        response = self.client.post(reverse('register'), {
            'email': 'failuser@example.com',
            'password1': 'password123',
            'password2': 'differentpassword',
        })
        # Expecting an error message in the rendered form.
        self.assertContains(response, "password")
        self.assertFalse(User.objects.filter(email='failuser@example.com').exists())

# ------------------------------
# Login Page Tests
# ------------------------------
class LoginPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Ensure username and email are set correctly
        self.user = User.objects.create_user(
            username='testuser',  # Using 'testuser' as the username
            email='test@example.com',
            password='testpass'
        )

    def test_login_page_renders(self):  # T1 for login page
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
        self.assertContains(response, "Forgot Password?")

    def test_successful_login(self):  # T7: Valid login should redirect to the dashboard.
        # Updated to use the username 'testuser' since that's what was created in setUp.
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass'
        }, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertContains(response, self.user.email)

    def test_invalid_login(self):  # T6: Invalid credentials should display an error.
        response = self.client.post(reverse('login'), {
            'username': 'wrong@example.com',
            'password': 'wrongpass'
        })
        self.assertContains(response, "Invalid email or password")

# ------------------------------
# Dashboard Page Tests
# ------------------------------
class DashboardPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.client.login(username='testuser', password='testpass')

    def test_dashboard_access_requires_login(self):  # T1: Dashboard requires a logged-in user.
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_empty_dashboard(self):  # T2: If no todos exist, "No ToDo's" is shown.
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "No ToDo's")

    def test_dashboard_with_todos(self):  # T4: A todo assigned to the user appears in the dashboard.
        todo = ToDo.objects.create(
            user=self.user,
            name="Test Todo",
            description="A test todo item",
            status="Not Started"
        )
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "Test Todo")
        self.assertContains(response, "Start")  # 'Start' button for Not Started todos

    def test_in_progress_todo_buttons(self):  # T7: In Progress todo should display "Pause" and "Stop" buttons.
        todo = ToDo.objects.create(
            user=self.user,
            name="In Progress Todo",
            description="In progress",
            status="In Progress",
            start_time=timezone.now(),
            elapsed_time=timezone.timedelta(0)
        )
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, "Pause")
        self.assertContains(response, "Stop")

# ------------------------------
# Create ToDo Page Tests
# ------------------------------
class CreateToDoPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.client.login(username='testuser', password='testpass')

    def test_create_todo_page_renders(self):  # T1: Create ToDo page renders correctly.
        response = self.client.get(reverse('create_todo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create a New ToDo")

    def test_create_todo_success(self):  # T10: Valid input creates a new ToDo and redirects.
        post_data = {
            'name': 'New Todo',
            'description': 'Testing create',
            'status': 'Not Started',
            'category': 'Test',
            'due_date': '2030-01-01',  # valid date
            'team': ''  # optional field left blank
        }
        response = self.client.post(reverse('create_todo'), post_data, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertContains(response, "New Todo")

# ------------------------------
# Update ToDo Page Tests
# ------------------------------
class UpdateToDoPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.client.login(username='testuser', password='testpass')
        self.todo = ToDo.objects.create(
            user=self.user,
            name="Original Todo",
            description="Original description",
            status="Not Started"
        )

    def test_update_todo_page_renders(self):  # T1: Update ToDo page renders with existing ToDo data.
        response = self.client.get(reverse('update_todo', args=[self.todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit ToDo")
        self.assertContains(response, "Original Todo")

    def test_update_todo_success(self):  # T10: Successful update saves changes.
        post_data = {
            'name': 'Updated Todo',
            'description': 'Updated description',
            'status': 'Not Started',
            'category': self.todo.category or '',
            'due_date': self.todo.due_date.strftime('%Y-%m-%d') if self.todo.due_date else '',
            'team': self.todo.team.id if self.todo.team else ''
        }
        response = self.client.post(reverse('update_todo', args=[self.todo.id]), post_data, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.name, 'Updated Todo')

# ------------------------------
# About Page Tests
# ------------------------------
class AboutPageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_about_page_renders(self):  # T1: About page renders and shows "About Us".
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About Us")

    def test_team_cards_present(self):  # T4: Profile cards for each team member are present.
        response = self.client.get(reverse('about'))
        self.assertContains(response, "Lulu")
        self.assertContains(response, "Dhruv")
        self.assertContains(response, "Sami")
        self.assertContains(response, "Amir")

# ------------------------------
# Password Reset Pages Tests
# ------------------------------
class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_password_reset_page_renders(self):  # T1: Password Reset page renders.
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password Reset")

    def test_password_reset_done_page_renders(self):  # T2: Password Reset Done page renders.
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password Reset Sent")

    def test_password_reset_confirm_page_renders(self):  # T3: Password Reset Confirm page renders.
        url = reverse('password_reset_confirm', args=['dummy', 'dummy-token'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set New Password")

    def test_password_reset_complete_page_renders(self):  # T4: Password Reset Complete page renders.
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password Reset Complete")

# ------------------------------
# Team Details Page Tests
# ------------------------------
class TeamDetailsPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', email='other@example.com', password='otherpass'
        )
        self.team = Team.objects.create(name="Alpha Team", description="Team description")
        self.team.members.add(self.user)
        self.client.login(username='testuser', password='testpass')

    def test_team_details_page_renders(self):  # T1: Team Details page renders correctly.
        response = self.client.get(reverse('team_details', args=[self.team.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Team: Alpha Team")
        self.assertContains(response, "Team description")

    def test_edit_team_form_hidden_by_default(self):
        response = self.client.get(reverse('team_details', args=[self.team.id]))
        # Check that the edit form <div> has the correct style to keep it hidden.
        self.assertContains(response, 'id="editForm" style="display: none;"')

    def test_team_member_removal(self):  # T6: Removing a team member works.
        post_data = {
            'remove_member': self.user.id,
        }
        response = self.client.post(reverse('team_details', args=[self.team.id]), post_data, follow=True)
        self.assertRedirects(response, reverse('team_details', args=[self.team.id]))
        self.assertNotIn(self.user, self.team.members.all())

    def test_add_team_member(self):  # T6: Adding a new team member works.
        post_data = {
            'new_member': self.other_user.email,
        }
        response = self.client.post(reverse('team_details', args=[self.team.id]), post_data, follow=True)
        self.assertRedirects(response, reverse('team_details', args=[self.team.id]))
        self.assertIn(self.other_user, self.team.members.all())

# ------------------------------
# Teams List Page Tests
# ------------------------------
class TeamsListPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.team1 = Team.objects.create(name="Team One", description="Desc One")
        self.team2 = Team.objects.create(name="Team Two", description="Desc Two")
        self.client.login(username='testuser', password='testpass')

    def test_teams_list_page_renders(self):  # T1: Teams List page renders with team names and a "Create New Team" link.
        response = self.client.get(reverse('teams_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teams")
        self.assertContains(response, "Team One")
        self.assertContains(response, "Team Two")
        self.assertContains(response, "Create New Team")

    def test_teams_list_no_teams(self):  # If no teams exist, a message is shown.
        Team.objects.all().delete()
        response = self.client.get(reverse('teams_list'))
        self.assertContains(response, "No teams available.")

# ------------------------------
# Create Team Page Tests
# ------------------------------
class CreateTeamPageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.client.login(username='testuser', password='testpass')

    def test_create_team_page_renders(self):  # T1: Create Team page renders.
        response = self.client.get(reverse('create_team'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Team")

    def test_create_team_success(self):  # T7: Valid team details create a team successfully.
        post_data = {
            'name': 'Beta Team',
            'description': 'Beta team description'
        }
        response = self.client.post(reverse('create_team'), post_data, follow=True)
        # Should redirect to the team details page.
        team = Team.objects.get(name='Beta Team')
        self.assertRedirects(response, reverse('team_details', args=[team.id]))
        self.assertContains(response, "Beta Team")

# ------------------------------
# End of tests
# ------------------------------

