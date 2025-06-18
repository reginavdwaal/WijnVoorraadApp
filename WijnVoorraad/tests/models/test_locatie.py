"""
Unit tests for the WijnVoorraad Django models.

This module covers model creation, string representations, constraints,
ordering, validation, and custom methods for all main models in the app.
"""

# pylint: disable=no-member
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from django.db.utils import IntegrityError
from django.test import TestCase

# Import the models to be tested
from WijnVoorraad.models import (
    Locatie,
)
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


class TestLocatie(SharedTestDataMixin, TestCase):
    def test_create_locatie(self):
        # locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=3)
        locatie2 = Locatie.objects.create(omschrijving="Zolder")
        self.assertEqual(self.locatie.omschrijving, "Kelder")
        self.assertEqual(self.locatie.aantal_kolommen, 3)
        self.assertEqual(locatie2.omschrijving, "Zolder")
        self.assertEqual(locatie2.aantal_kolommen, 1)

    def test_str_returns_omschrijving(self):

        self.assertEqual(str(self.locatie), "Kelder")

    def test_unique_omschrijving_constraint(self):
        Locatie.objects.create(omschrijving="Zolder")
        with self.assertRaises(IntegrityError):
            Locatie.objects.create(omschrijving="Zolder")

    def test_ordering(self):
        Locatie.objects.create(omschrijving="Bergkast")
        Locatie.objects.create(omschrijving="Achterkamer")
        Locatie.objects.create(omschrijving="Zijkamer")
        omschrijvingen = list(Locatie.objects.values_list("omschrijving", flat=True))
        self.assertEqual(omschrijvingen, sorted(omschrijvingen))
