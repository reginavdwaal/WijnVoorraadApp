"""Test cases for the access control on AIview.

AIview triggers paid OpenAI calls, so the important guarantee is not just that an
anonymous request is refused, but that it is refused *before* any request reaches
OpenAI. These tests therefore assert on the OpenAI client mock as well as on the
status code.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from WijnVoorraad.models import AIUsage


def _image():
    """A minimal fake upload; the tests never let it reach OpenAI."""
    return SimpleUploadedFile("label.jpg", b"not-a-real-image", content_type="image/jpeg")


class TestAIviewAuthentication(TestCase):
    """AIview must be reachable for logged in users only."""

    def setUp(self):
        self.url = reverse("WijnVoorraad:AI-zoeken")
        self.user = get_user_model().objects.create_user(
            username="wijnliefhebber", password="geheim123"
        )

    @patch("WijnVoorraad.views.OpenAI")
    def test_anonymous_post_is_refused(self, mock_openai):
        """An anonymous POST gets 401 and never reaches OpenAI."""
        response = self.client.post(self.url, {"image": _image()})

        self.assertEqual(response.status_code, 401)
        mock_openai.assert_not_called()

    @patch("WijnVoorraad.views.OpenAI")
    def test_anonymous_post_returns_json_not_a_redirect(self, mock_openai):
        """The refusal is JSON, so fetch() can read it instead of following a redirect."""
        response = self.client.post(self.url, {"image": _image()})

        self.assertEqual(response["Content-Type"], "application/json")
        payload = response.json()
        self.assertIn("message", payload)
        self.assertIn("/accounts/login/", payload["login_url"])
        mock_openai.assert_not_called()

    @patch("WijnVoorraad.views.OpenAI")
    def test_anonymous_post_records_no_usage(self, mock_openai):
        """No AIUsage row is written, because no paid call was made."""
        self.client.post(self.url, {"image": _image()})

        self.assertEqual(AIUsage.objects.count(), 0)
        mock_openai.assert_not_called()

    @patch("WijnVoorraad.views.AIview.searchwine")
    def test_logged_in_user_is_allowed_through(self, mock_searchwine):
        """A logged in user passes the auth check and reaches the search logic."""
        mock_searchwine.return_value = '{"name": "Chateau Test"}'
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"image": _image()})

        self.assertEqual(response.status_code, 200)
        mock_searchwine.assert_called_once()

    @patch("WijnVoorraad.views.OpenAI")
    def test_logged_in_post_without_image_is_rejected(self, mock_openai):
        """The existing 'no image' guard still applies and costs nothing."""
        self.client.force_login(self.user)

        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 400)
        mock_openai.assert_not_called()
