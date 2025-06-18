""" "Test cases for the AIUsage model in WijnVoorraad.
This module contains unit tests for the AIUsage model, which tracks AI interactions with users.
"""

from django.contrib.auth import get_user_model

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from WijnVoorraad.models import AIUsage


class TestAIUsage(TestCase):
    """Test cases for the AIUsage model.
    This class contains tests to verify the correct behavior of the AIUsage model, including:
    - Creation of AIUsage instances with and without a user.
    - Prevention of user deletion if AIUsage instances exist.
    - Validation of the model field length.
    """

    def setUp(self):
        self.user = get_user_model().objects.create(username="aiuser")

    def test_create_aiusage_with_user(self):
        """Test that AIUsage can be created with a real user."""
        usage = AIUsage.objects.create(
            user=self.user,
            model="gpt-4",
            response_time=timezone.now(),
            response_content="Test response",
            response_tokens_used=42,
        )
        self.assertEqual(usage.user, self.user)
        self.assertEqual(usage.model, "gpt-4")

    def test_create_aiusage_without_user(self):
        """Test that AIUsage can not be created without  user."""

        with self.assertRaises(IntegrityError):
            AIUsage.objects.create(
                user=None,
                model="gpt-4",
                response_time=timezone.now(),
                response_content="Test response",
                response_tokens_used=42,
            )

    def test_user_delete_prevented_if_aiusage_exists(self):
        """Test that a user cannot be deleted if there is an AIUsage object."""
        usage = AIUsage.objects.create(
            user=self.user,
            model="gpt-4",
            response_time=timezone.now(),
            response_content="Test response",
            response_tokens_used=42,
        )
        with self.assertRaises(IntegrityError):
            self.user.delete()
        # Ensure the AIUsage instance still exists
        self.assertTrue(AIUsage.objects.filter(pk=usage.pk).exists())

    def test_model_longer_than_200_raises_error(self):
        """Test that model longer than 200 characters raises ValidationError."""
        usage = AIUsage(
            user=self.user,
            model="a" * 201,
            response_time=timezone.now(),
            response_content="Test response",
            response_tokens_used=42,
        )
        with self.assertRaises(ValidationError):
            usage.full_clean()

    def test_str_method(self):
        """Test the __str__ method of AIUsage."""
        usage = AIUsage.objects.create(
            user=self.user,
            model="gpt-4",
            response_time=timezone.now(),
            response_content="Test response",
            response_tokens_used=42,
        )
        expected_str = f"{self.user.username} - {usage.response_time.strftime('%d-%m-%Y %H:%M:%S')}"
        self.assertEqual(str(usage), expected_str)
