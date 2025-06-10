"""
Unit tests for the WijnVoorraad Django models.

This module covers model creation, string representations, constraints,
ordering, validation, and custom methods for all main models in the app.
"""

# pylint: disable=no-member
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from django.core.exceptions import ValidationError
from django.test import TestCase

# Import the models to be tested
from WijnVoorraad.models import (
    WijnSoort,
)


class TestWijnSoort(TestCase):

    def test_wijn_soort_not_longer_then_200(self):
        with self.assertRaises(ValidationError) as exc:
            wijnsoort = WijnSoort.objects.create(omschrijving="abc" * 100)
            wijnsoort.full_clean()
        self.assertIn("200", str(exc.exception))

    def test_wijn_soort_200_should_fit(self):
        wijnsoort = WijnSoort.objects.create(omschrijving="ab" * 100)
        wijnsoort.full_clean()
        self.assertEqual(len(wijnsoort.omschrijving), 200)

    def test_wijn_as_str_should_return_omschrijving(self):
        wijnsoort = WijnSoort.objects.create(omschrijving="Precies Dit")
        self.assertEqual(str(wijnsoort), "Precies Dit")

    def test_wijnsoort_order(self):
        WijnSoort.objects.create(omschrijving="B.Rood")
        WijnSoort.objects.create(omschrijving="A.Rood")
        WijnSoort.objects.create(omschrijving="C.Rood")

        # check if the order is correct
        self.assertEqual(
            list(WijnSoort.objects.all().order_by("omschrijving")),
            list(WijnSoort.objects.all()),
        )
