"""
Test suite for the Deelnemer model in the WijnVoorraad application."""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from WijnVoorraad.models import Deelnemer
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


class TestDeelnemer(SharedTestDataMixin, TestCase):
    """
    Test suite for the Deelnemer model.
    This class contains tests to verify the correct behavior of the Deelnemer model, including:
    """

    def test_str_returns_naam(self):
        deelnemer = Deelnemer.objects.create(naam="Piet")
        self.assertEqual(str(deelnemer), "Piet")

    def test_unique_naam_constraint(self):
        Deelnemer.objects.create(naam="Kees")
        with self.assertRaises(IntegrityError):
            Deelnemer.objects.create(naam="Kees")

    def test_many_to_many_users(self):
        deelnemer = Deelnemer.objects.create(naam="Lisa")
        deelnemer.users.add(self.user)
        second_user = get_user_model().objects.create(username="seconduser")
        deelnemer.users.add(second_user)
        self.assertIn(self.user, deelnemer.users.all())
        self.assertIn(second_user, deelnemer.users.all())
        self.assertEqual(deelnemer.users.count(), 2)

    # test that one user can be linked to multiple deelnemers
    def test_user_can_be_linked_to_multiple_deelnemers(self):
        deelnemer1 = Deelnemer.objects.create(naam="Mark")
        deelnemer2 = Deelnemer.objects.create(naam="Sophie")
        deelnemer1.users.add(self.user)
        deelnemer2.users.add(self.user)
        self.assertIn(self.user, deelnemer1.users.all())
        self.assertIn(self.user, deelnemer2.users.all())
        self.assertEqual(deelnemer1.users.count(), 1)
        self.assertEqual(deelnemer2.users.count(), 1)

    def test_ordering(self):
        Deelnemer.objects.create(naam="Bert")
        Deelnemer.objects.create(naam="Anna")
        Deelnemer.objects.create(naam="Chris")
        namen = list(Deelnemer.objects.values_list("naam", flat=True))
        self.assertEqual(namen, sorted(namen))
