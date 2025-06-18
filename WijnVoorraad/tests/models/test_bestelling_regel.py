from unittest.mock import patch
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


@patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_rsv", return_value=True)
class TestBestellingRegel(SharedTestDataMixin, TestCase):
    """Unit tests for the BestellingRegel model."""

    def test_bestelling_cannot_be_deleted_if_bestelling_regel_exists(self, _):
        """Test that a Bestelling cannot be deleted if it has related BestellingRegel instances."""
        bestelling = self.create_bestelling()
        self.create_bestellingregel(bestelling=bestelling)

        with self.assertRaises(IntegrityError):
            bestelling.delete()

    def test_ontvangst_cannot_be_deleted_if_bestelling_regel_exists(self, _):
        """Test that a Bestelling cannot be deleted if it has related BestellingRegel instances."""
        bestelling = self.create_bestelling()
        self.create_bestellingregel(bestelling=bestelling)

        with self.assertRaises(IntegrityError):
            self.ontvangst.delete()

    def test_vak_cannot_be_deleted_if_bestelling_regel_exists(self, _):
        """Test that a Bestelling cannot be deleted if it has related BestellingRegel instances."""
        bestelling = self.create_bestelling()
        self.create_bestellingregel(bestelling=bestelling, vak=self.vak_a1)

        with self.assertRaises(IntegrityError):
            self.vak_a1.delete()

    def test_opmerking_should_be_limited_to_4000(self, _):
        """Test that the opmerking field is limited to 4000 characters."""
        bestelling = self.create_bestelling()
        long_opmerking = "a" * 4001
        regel = self.create_bestellingregel(
            bestelling=bestelling, opmerking=long_opmerking
        )
        with self.assertRaises(ValidationError):
            regel.full_clean()
