"""
Unit tests for the Vak model in the WijnVoorraad application.
Tested with a SharedTestDataMixin for common test data setup.
"""

from django.db import IntegrityError
from django.test import TestCase
from WijnVoorraad.models import Locatie, Vak
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


class TestVak(SharedTestDataMixin, TestCase):
    """
    Test suite for the Vak model.
    This class contains tests to verify the correct behavior of the Vak model, including:
    - Creation of Vak instances with required fields.
    - Enforcement of required 'locatie' field.
    - String representation of Vak instances.
    - Uniqueness constraint on 'code' within a given 'locatie'.
    - Correct ordering of Vak instances.
    Test Methods:
        - test_create_vak: Tests successful creation of a Vak instance.
        - test_vak_requires_locatie: Ensures Vak cannot be created without a 'locatie'.
        - test_vak_requires_locatie_no_create: Ensures a Vak without 'locatie' raises an error.
        - test_str_returns_combined_name: Checks the string representation of Vak.
        - test_unique_code_binnen_locatie: Verifies uniqueness of 'code' within the same 'locatie'.
        - test_ordering: Tests the default ordering of Vak instances.
    """

    def test_create_vak(self):
        vak = Vak.objects.create(locatie=self.locatie, code="B1", capaciteit=10)
        self.assertEqual(vak.locatie, self.locatie)
        self.assertEqual(vak.code, "B1")
        self.assertEqual(vak.capaciteit, 10)

    # test vak can not be created without a locatie
    def test_vak_requires_locatie(self):
        with self.assertRaises(IntegrityError):
            Vak.objects.create(code="B2", capaciteit=5)

    def test_vak_requires_locatie_no_create(self):
        with self.assertRaises(IntegrityError):
            vak = Vak()
            vak.code = "B2"
            vak.capaciteit = 5
            vak.save()  # This should raise an IntegrityError since locatie is required

    def test_str_returns_combined_name(self):
        vak = Vak.objects.create(locatie=self.locatie, code="B2", capaciteit=5)
        self.assertEqual(str(vak), "Kelder (B2)")

    def test_unique_code_binnen_locatie(self):
        Vak.objects.create(locatie=self.locatie, code="C3", capaciteit=3)

        with self.assertRaises(IntegrityError):
            Vak.objects.create(locatie=self.locatie, code="C3", capaciteit=7)

    def test_ordering(self):
        loc2 = Locatie.objects.create(omschrijving="Zolder", aantal_kolommen=1)
        Vak.objects.create(locatie=loc2, code="A1", capaciteit=1)
        Vak.objects.create(locatie=self.locatie, code="B1", capaciteit=1)
        Vak.objects.create(locatie=self.locatie, code="C1", capaciteit=1)
        vakken = list(Vak.objects.all())
        sorted_vakken = sorted(vakken, key=lambda v: (v.locatie.omschrijving, v.code))
        self.assertEqual(vakken, sorted_vakken)
