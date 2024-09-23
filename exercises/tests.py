from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Exercise, Comment, ContactMessage, CommentReport
from .forms import CommentForm, ContactMessageForm, ReportCommentForm

#
# Model Tests
#


class ExerciseModelTest(TestCase):
    """
    Tests for the Exercise model.

    Methods:
        setUp: Creates a test user and a test exercise for use in the tests.
        test_exercise_creation: Validates the creation of an exercise.
        test_exercise_default_status: Checks that the default status of a
        newly created exercise is 'Draft'.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.exercise = Exercise.objects.create(
            title="Test Exercise",
            description="This is a test exercise.",
            author=self.user,
            status=1,
        )

    def test_exercise_creation(self):
        self.assertEqual(self.exercise.title, "Test Exercise")
        self.assertEqual(str(self.exercise), "Test Exercise")

    def test_exercise_default_status(self):
        exercise = Exercise.objects.create(
            title="Another Exercise",
            description="This is another test exercise.",
            author=self.user,
        )
        self.assertEqual(exercise.status, 0)


class CommentModelTest(TestCase):
    """
    Tests for the Comment model.

    Methods:
        setUp: Creates a test user, author, exercise,
        and comment for use in the tests.
        test_comment_creation: Validates the creation of a comment.
        test_comment_str_length: Ensures the string representation
        of a comment is within the expected length.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.author = User.objects.create_user(
            username="authoruser", password="12345"
        )
        self.exercise = Exercise.objects.create(
            title="Test Exercise", author=self.author
        )
        self.comment = Comment.objects.create(
            body="This is a test comment.",
            user=self.user,
            exercise=self.exercise,
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.body, "This is a test comment.")
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.exercise, self.exercise)

    def test_comment_str_length(self):
        self.assertTrue(len(str(self.comment)) <= 100)


class ContactMessageModelTest(TestCase):
    """
    Tests for the ContactMessage model.

    Methods:
        test_contact_message_creation: Validates the
        creation of a contact message.
        test_invalid_email: Tests that the contact
        message form rejects invalid email addresses.
    """
    def test_contact_message_creation(self):
        contact_message = ContactMessage.objects.create(
            name="Test User",
            email="test@example.com",
            message="This is a test message.",
        )
        self.assertEqual(
            str(contact_message),
            f"Message from {contact_message.name} at
            {contact_message.created_at}",
        )

    def test_invalid_email(self):
        form_data = {
            "name": "Test User",
            "email": "not-an-email",
            "message": "This is a test message.",
        }
        form = ContactMessageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class CommentReportModelTest(TestCase):
    """
    Tests for the CommentReport model.

    Methods:
        setUp: Creates a test user, exercise, and comment for use in the tests.
        test_comment_report_creation: Validates
        the creation of a comment report.
        test_report_comment_with_long_reason:
        Tests that a comment report can be created with a long reason.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.exercise = Exercise.objects.create(
            title="Test Exercise",
            description="This is a test exercise.",
            author=self.user,
            status=1,
        )
        self.comment = Comment.objects.create(
            exercise=self.exercise,
            user=self.user,
            body="This is a test comment.",
        )

    def test_comment_report_creation(self):
        report = CommentReport.objects.create(
            user=self.user, comment=self.comment, reason="Spam"
        )
        self.assertEqual(report.reason, "Spam")

    def test_report_comment_with_long_reason(self):
        long_reason = "x" * 1000
        report = CommentReport.objects.create(
            user=self.user, comment=self.comment, reason=long_reason
        )
        self.assertEqual(report.reason, long_reason)


#
# Form Tests
#

class ContactMessageFormTest(TestCase):
    """
    Tests for the ContactMessageForm.

    Methods:
        test_contact_message_form: Validates
        that the contact message form works correctly with valid data.
        test_contact_message_form_invalid_email: Ensures the
        form rejects invalid email addresses.
    """
    def test_contact_message_form(self):
        form_data = {
            "name": "Test Name",
            "email": "test@example.com",
            "message": "This is a test message.",
        }
        form = ContactMessageForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_message_form_invalid_email(self):
        form_data = {
            "name": "Test Name",
            "email": "invalid-email",
            "message": "This is a test message.",
        }
        form = ContactMessageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class ReportCommentFormTest(TestCase):
    """
    Tests for the ReportCommentForm.

    Methods:
        setUp: Creates a test user, exercise, and comment for use in the tests.
        test_report_comment_form: Validates that the report
        comment form works correctly with valid data.
        test_report_comment_form_missing_reason: Ensures the
        form rejects submissions with missing reasons.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.exercise = Exercise.objects.create(
            title="Test Exercise",
            description="Test description",
            author=self.user,
            status=1,
        )
        self.comment = Comment.objects.create(
            exercise=self.exercise, user=self.user, body="Test comment"
        )

    def test_report_comment_form(self):
        form_data = {
            "reason": "Spam",
            "comment_id": self.comment.id,
            "comment_text": self.comment.body,
        }
        form = ReportCommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_report_comment_form_missing_reason(self):
        form_data = {
            "comment_id": self.comment.id,
            "comment_text": self.comment.body,
        }
        form = ReportCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("reason", form.errors)


#
# View Tests
#

class ExerciseViewTest(TestCase):
    """
    Tests for the Exercise views.

    Methods:
        setUp: Creates a test client, user, and exercise for use in the tests.
        test_exercise_list_view: Validates the
        exercise list view response and content.
        test_exercise_detail_view: Validates the
        exercise detail view response and content.
        test_add_comment_view: Tests adding a comment as an authenticated user.
        test_add_comment_view_unauthenticated: Tests adding a
        comment when the user is not authenticated.
        test_edit_comment_view: Tests editing a comment as
        an authenticated user.
        test_delete_comment_view: Tests deleting a comment as
        an authenticated user.
        test_delete_comment_view_unauthenticated: Tests deleting a
        comment when the user is not authenticated.
        test_contact_form_view: Tests the contact form submission.
        test_contact_form_view_invalid: Tests the contact form when
        submitted with invalid data.
        test_report_comment_view: Tests reporting a comment as an
        authenticated user.
        test_report_comment_view_invalid: Tests reporting a comment
        with missing data.
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.exercise = Exercise.objects.create(
            title="Test Exercise",
            description="This is a test exercise.",
            author=self.user,
            status=1,
        )

    def test_exercise_list_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Exercise")

    def test_exercise_detail_view(self):
        response = self.client.get(
            reverse("exercise_detail", args=[self.exercise.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Exercise")

    def test_add_comment_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("add_comment", args=[self.exercise.pk]),
            {
                "body": "This is a new comment.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Comment.objects.filter(body="This is a new comment.").exists()
        )

    def test_add_comment_view_unauthenticated(self):
        response = self.client.post(
            reverse("add_comment", args=[self.exercise.pk]),
            {
                "body": "This is a new comment.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_edit_comment_view(self):
        comment = Comment.objects.create(
            exercise=self.exercise,
            user=self.user,
            body="This is a test comment.",
        )
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("edit_comment", args=[self.exercise.pk, comment.id]),
            {
                "body": "Updated comment.",
            },
        )
        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertEqual(comment.body, "Updated comment.")

    def test_delete_comment_view(self):
        comment = Comment.objects.create(
            exercise=self.exercise,
            user=self.user,
            body="This is a test comment.",
        )
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("delete_comment", args=[self.exercise.pk, comment.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

    def test_delete_comment_view_unauthenticated(self):
        comment = Comment.objects.create(
            exercise=self.exercise,
            user=self.user,
            body="This is a test comment.",
        )
        response = self.client.post(
            reverse("delete_comment", args=[self.exercise.pk, comment.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_contact_form_view(self):
        response = self.client.post(
            reverse("contact_form"),
            {
                "name": "Test Name",
                "email": "test@example.com",
                "message": "This is a test message.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ContactMessage.objects.filter(email="test@example.com").exists()
        )

    def test_contact_form_view_invalid(self):
        response = self.client.post(
            reverse("contact_form"),
            {
                "name": "",
                "email": "test@example.com",
                "message": "This is a test message.",
            },
        )
        if response.context and "form" in response.context:
            form_errors = response.context["form"].errors.as_data()
            print("Form errors:", form_errors)
        self.assertContains(
            response, "This field is required.", status_code=200
        )

    def test_report_comment_view(self):
        self.client.login(username="testuser", password="password")
        comment = Comment.objects.create(
            exercise=self.exercise,
            user=self.user,
            body="This is a test comment.",
        )
        response = self.client.post(
            reverse("report_comment", args=[comment.id]),
            {
                "reason": "Spam",
                "comment_text": comment.body,
            },
        )

        if response.status_code == 200:
            print("Form errors:", response.context["form"].errors)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CommentReport.objects.filter(
                comment=comment, user=self.user
            ).exists()
        )

    def test_report_comment_view_invalid(self):
        self.client.login(username="testuser", password="password")
        comment = Comment.objects.create(
            exercise=self.exercise,
            user=self.user,
            body="This is a test comment.",
        )
        response = self.client.post(
            reverse("report_comment", args=[comment.id]),
            {
                "comment_text": comment.body,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")


#
# URL Tests
#

class URLTests(TestCase):
    """
    Tests for the URL patterns in the application.

    Methods:
        setUp: Creates a test client for use in the tests.
        test_home_url: Validates that the home URL
        returns a successful response.
        test_exercise_detail_url: Validates that the exercise detail
        URL returns a successful response.
        test_add_comment_url: Validates that the add comment URL returns a
        successful response when accessed as an authenticated user.
        test_contact_form_url: Validates that the contact form URL returns
        a successful response.
        test_report_comment_url: Validates that the report comment URL returns
        a successful response.
        test_invalid_url: Validates that an invalid URL
        returns a 404 status code.
    """
    def setUp(self):
        self.client = Client()

    def test_home_url(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_exercise_detail_url(self):
        user = User.objects.create_user(
            username="testuser", password="password"
        )
        exercise = Exercise.objects.create(
            title="Test Exercise",
            description="This is a test exercise.",
            author=user,
            status=1,
        )
        response = self.client.get(
            reverse("exercise_detail", args=[exercise.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_add_comment_url(self):
        user = User.objects.create_user(
            username="testuser", password="password"
        )
        exercise = Exercise.objects.create(
            title="Test Exercise",
            description="This is a test exercise.",
            author=user,
            status=1,
        )
        self.client.login(username="testuser", password="password")
        response = self.client.post(
            reverse("add_comment", args=[exercise.pk]),
            {
                "body": "This is a test comment.",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_contact_form_url(self):
        response = self.client.get(reverse("contact_form"))
        self.assertEqual(response.status_code, 200)

    def test_report_comment_url(self):
        user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.client.login(username="testuser", password="password")

        exercise = Exercise.objects.create(
            title="Test Exercise",
            description="This is a test exercise.",
            author=user,
            status=1,
        )

        comment = Comment.objects.create(
            exercise=exercise, user=user, body="This is a test comment."
        )

        response = self.client.post(
            reverse("report_comment", args=[comment.id]),
            {
                "reason": "Spam",
                "comment_text": comment.body,
            },
        )

        if response.status_code == 200:
            print("Form errors:", response.context["form"].errors)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CommentReport.objects.filter(comment=comment, user=user).exists()
        )

    def test_invalid_url(self):
        response = self.client.get("/invalid-url/")
        self.assertEqual(response.status_code, 404)
