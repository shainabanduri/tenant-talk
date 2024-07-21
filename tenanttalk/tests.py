from django.test import Client, TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from . import views
from .urls import urlpatterns
from django.utils import timezone
from .models import Report
from unittest.mock import patch
import tempfile
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth import get_user_model


# from django.test import override_settings
# @override_settings(STATICFILES_STORAGE='django.core.files.storage.FileSystemStorage')
class FirstTestCase(TestCase):
    def test_one(self):
        self.assertIs(True, True)

class ReportViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='testpassword'
        )

        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staffuser@example.com',
            password='testpassword',
            is_staff=True
        )

        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regularuser@example.com',
            password='testpassword'
        )
        
        self.client = Client()

    def test_home_page(self):
        # Test accessing the home page
        url = reverse('home')
        self.assertIs(url, "/")
        

    def test_account_page(self):
        url = reverse('myaccount')
        self.assertEqual(url, '/myaccount/')

    def test_report_page(self):
        url = reverse('report')
        self.assertEqual(url, '/report/')
        


class ReportModelTestCase(TestCase):
    def test_report_creation(self):
        report = Report.objects.create(
            post_title="Test Post",
            building_address="123 Test St",
            landlord_name="John Doe",
            report="Test report content",
            time_stamp=timezone.now(),
            status="NEW",
            feedback="Test feedback",
            user="Test User"
        )
        self.assertIsInstance(report, Report)
        self.assertEqual(report.post_title, "Test Post")
        self.assertEqual(report.building_address, "123 Test St")
        self.assertEqual(report.landlord_name, "John Doe")
        self.assertEqual(report.report, "Test report content")
        self.assertIsNotNone(report.time_stamp)
        self.assertEqual(report.status, "NEW")
        self.assertEqual(report.feedback, "Test feedback")
        self.assertEqual(report.user, "Test User")

    def test_str_method(self):
        report = Report.objects.create(
            post_title="Test Post",
            building_address="123 Test St",
            landlord_name="John Doe",
            report="Test report content",
            time_stamp=timezone.now(),
            status="NEW",
            feedback="Test feedback",
            user="Test User"
        )
        self.assertEqual(str(report), "Test Post")

    def test_report_creation_without_feedback(self):
        report = Report.objects.create(
            post_title="Default Status Post",
            building_address="789 Default Status St",
            landlord_name="Bob Johnson",
            report="Default status report content",
            time_stamp=timezone.now(),
            status="NEW",
            feedback="",
            user="Test User"
        )
        self.assertIsInstance(report, Report)
        self.assertEqual(report.post_title, "Default Status Post")
        self.assertEqual(report.building_address, "789 Default Status St")
        self.assertEqual(report.landlord_name, "Bob Johnson")
        self.assertEqual(report.report, "Default status report content")
        self.assertIsNotNone(report.time_stamp)
        self.assertEqual(report.status, "NEW")


    def test_report_creation_in_progress(self):
        report = Report.objects.create(
            post_title="Another Test Post",
            building_address="456 Another Test St",
            landlord_name="Jane Smith",
            report="Another test report content",
            time_stamp=timezone.now(),
            status="IN_PROGRESS",
            feedback="feedback",
            user="Test User"
        )
        self.assertIsInstance(report, Report)
        self.assertEqual(report.post_title, "Another Test Post")
        self.assertEqual(report.building_address, "456 Another Test St")
        self.assertEqual(report.landlord_name, "Jane Smith")
        self.assertEqual(report.report, "Another test report content")
        self.assertIsNotNone(report.time_stamp)
        self.assertEqual(report.status, "IN_PROGRESS")

    def test_report_creation_resolved(self):
        report = Report.objects.create(
            post_title="Another Test Post",
            building_address="456 Another Test St",
            landlord_name="Jane Smith",
            report="Another test report content",
            time_stamp=timezone.now(),
            status="RESOLVED",
            feedback="feedback",
            user="Test User"
        )
        self.assertIsInstance(report, Report)
        self.assertEqual(report.post_title, "Another Test Post")
        self.assertEqual(report.building_address, "456 Another Test St")
        self.assertEqual(report.landlord_name, "Jane Smith")
        self.assertEqual(report.report, "Another test report content")
        self.assertIsNotNone(report.time_stamp)
        self.assertEqual(report.status, "RESOLVED")
        
    def test_report_creation_new(self):
        report = Report.objects.create(
            post_title="Another Test Post",
            building_address="456 Another Test St",
            landlord_name="Jane Smith",
            report="Another test report content",
            time_stamp=timezone.now(),
            status="NEW",
            feedback="feedback",
            user="Test User"
        )
        self.assertIsInstance(report, Report)
        self.assertEqual(report.post_title, "Another Test Post")
        self.assertEqual(report.building_address, "456 Another Test St")
        self.assertEqual(report.landlord_name, "Jane Smith")
        self.assertEqual(report.report, "Another test report content")
        self.assertIsNotNone(report.time_stamp)
        self.assertEqual(report.status, "NEW")
        
         



class MyAccountViewTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staffuser@example.com',
            password='testpassword',
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regularuser@example.com',
            password='testpassword'
        )
        
        self.client = Client()

User = get_user_model()

class UserRegistrationFormTestCase(TestCase):
    def test_valid_form(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_invalid_form(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'invalidemail',  # Invalid email format
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_save_method(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = UserRegistrationForm(data=form_data)
        user = form.save()
        self.assertIsInstance(user, User)
        
