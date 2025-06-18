from unittest.mock import patch
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import models
from WijnVoorraad.models import BestellingRegel
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

    def test_is_verzameld_default_false(self, _):
        """Test that isVerzameld defaults to False."""
        bestelling = self.create_bestelling()
        regel = BestellingRegel.objects.create(
            bestelling=bestelling,
            ontvangst=self.ontvangst,
            vak=self.vak_a1,
            aantal=1,
            opmerking="",
        )
        self.assertFalse(regel.isVerzameld)

    def test_verwerkt_default_n(self, _):
        """Test that verwerkt defaults to 'N'."""
        bestelling = self.create_bestelling()
        regel = BestellingRegel.objects.create(
            bestelling=bestelling,
            ontvangst=self.ontvangst,
            vak=self.vak_a1,
            aantal=1,
            opmerking="",
        )
        self.assertEqual(regel.verwerkt, "N")

    def test_verwerkt_can_be_set_to_a_v(self, _):
        """Test that verwerkt can be set to 'A' or 'V' not other."""
        bestelling = self.create_bestelling()
        regel = BestellingRegel.objects.create(
            bestelling=bestelling,
            ontvangst=self.ontvangst,
            vak=self.vak_a1,
            aantal=1,
            opmerking="",
        )
        regel.verwerkt = "A"
        regel.full_clean()
        self.assertEqual(regel.verwerkt, "A")

        regel.verwerkt = "V"
        regel.full_clean()
        self.assertEqual(regel.verwerkt, "V")

        regel.verwerkt = "X"
        with self.assertRaises(ValidationError):

            regel.full_clean()  # Should raise ValidationError for invalid value

    def test_str_returns_bestelling_wijn(self, _):
        """Test that the __str__ method returns the correct string representation."""
        bestelling = self.create_bestelling()
        regel = self.create_bestellingregel(bestelling=bestelling)
        expected_str = f"{bestelling} - {regel.ontvangst.wijn}"
        self.assertEqual(str(regel), expected_str)

    @patch("WijnVoorraad.models.WijnVoorraad.check_voorraad_rsv", return_value=True)
    def test_clean_should_reload_from_db(self, mock_check_voorraad, _):
        """Test that clean methdef test_clean_should_reloadod reloads the instance from the database."""
        bestelling = self.create_bestelling()
        regel = self.create_bestellingregel(bestelling=bestelling, aantal=5)

        old_regel = BestellingRegel.objects.get(id=regel.id)
        regel.aantal = 10
        # mock specifically the bijwerken_rsv method
        # with patch WijnVoorraad.check_voorraad_rsv
        regel.clean()
        mock_check_voorraad.assert_called_once_with(regel, old_regel)

    @patch("WijnVoorraad.models.WijnVoorraad.check_voorraad_rsv")
    def test_clean_should_check_voorraad_with_new_regel(self, mock_check_voorraad, _):
        """Test that clean method checks voorraad with the new regel."""
        bestelling = self.create_bestelling()
        regel = BestellingRegel(
            bestelling=bestelling,
            ontvangst=self.ontvangst,
            vak=self.vak_a1,
            aantal=5,
            opmerking="",
        )

        regel.clean()
        mock_check_voorraad.assert_called_once_with(regel, None)

    def test_clean_should_call_super_validate(self, _):
        """Test that clean method calls the superclass clean method."""
        bestelling = self.create_bestelling()
        regel = BestellingRegel(
            bestelling=bestelling,
            ontvangst=self.ontvangst,
            vak=self.vak_a1,
            aantal=1,
            # set opmerking to 5000 length
            opmerking="a" * 5000,
        )

        with patch.object(models.Model, "clean") as mock_super_clean:
            regel.clean()
            # Check that the super clean method was called
            mock_super_clean.assert_called_once()
