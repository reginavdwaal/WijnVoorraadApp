import unittest
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

    def test_delete_should_remove(self, _):
        """Test that delete method reloads the instance from the database."""
        bestelling = self.create_bestelling()
        regel = self.create_bestellingregel(bestelling=bestelling)

        regel_id = regel.id
        regel.delete()

        # Reload from the database to ensure it was deleted
        with self.assertRaises(BestellingRegel.DoesNotExist):
            BestellingRegel.objects.get(id=regel_id)

    @patch("WijnVoorraad.models.WijnVoorraad.check_voorraad_rsv")
    def test_delete_should_call_check_voorraad_rsv_whith_db_instance(
        self, mock_check_voorraad_rsv, _
    ):
        """Test that delete method calls check_voorraad_rsv with the database instance."""
        bestelling = self.create_bestelling()
        regel = self.create_bestellingregel(bestelling=bestelling)
        # get the current regel from the database
        old_regel = BestellingRegel.objects.get(id=regel.id)
        regel.aantal = 10

        regel.delete()

        # Check that check_voorraad_rsv was called with the database instance
        mock_check_voorraad_rsv.assert_called_once_with(None, old_regel)

    def test_delete_should_call_bijwerken_voorraad_with_db_instance(
        self, bijwerken_rsv
    ):
        """Test that delete method calls Bijwerken_rsv with the database instance."""
        bestelling = self.create_bestelling()
        regel = self.create_bestellingregel(bestelling=bestelling)

        bijwerken_rsv.reset_mock()  # Reset the mock to ensure it only counts this call
        old_regel = BestellingRegel.objects.get(id=regel.id)
        regel.aantal = 10

        regel.delete()

        bijwerken_rsv.assert_called_once_with(None, old_regel)

    def test_delete_should_call_bestelling_check_afsluiten(self, _):
        """Test that delete method calls check_afsluiten on the bestelling."""
        bestelling = self.create_bestelling()
        regel = self.create_bestellingregel(bestelling=bestelling)

        # Mock the check_afsluiten method
        with patch.object(bestelling, "check_afsluiten") as mock_check_afsluiten:
            regel.delete()
            mock_check_afsluiten.assert_called_once()

    def test_delete_on_non_existing_instance_should_raise_error(self, _):
        """Test that delete on a non-existing instance raises DoesNotExist."""
        bestelling = self.create_bestelling()
        # Create a BestellingRegel instance without saving it to the database
        regel = BestellingRegel(
            bestelling=bestelling,
            ontvangst=self.ontvangst,
            vak=self.vak_a1,
            aantal=1,
            opmerking="",
        )
        regel.save()
        # regel = self.create_bestellingregel(bestelling=bestelling)

        regel_id = regel.id
        regel.delete()

        # Attempt to delete again should raise NonExistError
        with self.assertRaises(BestellingRegel.DoesNotExist):
            BestellingRegel.objects.get(id=regel_id).delete()

    def test_afboeken_should_ignore_if_verwerkt_is_not_n(self, _):
        """Test that afboeken does nothing if verwerkt is not 'N'."""
        bestelling = self.create_bestelling()
        regel = self.create_bestellingregel(
            bestelling=bestelling, aantal=5, verwerkt="A"
        )

        # Mock the afboeken method
        with patch.object(regel, "save") as mock_save:
            regel.afboeken()
            mock_save.assert_not_called()

    def test_afboeken_should_call_mutatie_afboeken_with_aantal_and_set_verwerkt_to_v(
        self, _
    ):
        """Test that afboeken decreases aantal and sets verwerkt to 'V'."""
        bestelling = self.create_bestelling()
        regel = self.create_bestellingregel(bestelling=bestelling, aantal=5)

        with patch("WijnVoorraad.models.VoorraadMutatie.afboeken") as mock_afboeken:
            regel.afboeken()

            # Check that afboeken was called with the correct aantal
            mock_afboeken.assert_called_once_with(
                regel.ontvangst, regel.bestelling.vanLocatie, regel.vak, 5
            )

        # Check that aantal is decreased by 1 and verwerkt is set to 'V'
        regel.refresh_from_db()

        self.assertEqual(regel.verwerkt, "A")

    def test_afboeken_should_use_correctie_if_aantal_correctie_is_not_none(self, _):
        """Test that afboeken uses aantal_correctie if it is not None."""
        bestelling = self.create_bestelling()
        correctie_aantal = 2
        regel = self.create_bestellingregel(
            bestelling=bestelling, aantal=5, aantal_correctie=correctie_aantal
        )

        with patch("WijnVoorraad.models.VoorraadMutatie.afboeken") as mock_afboeken:
            regel.afboeken()

            # Check that afboeken was called with the correct aantal_correctie
            mock_afboeken.assert_called_once_with(
                regel.ontvangst,
                regel.bestelling.vanLocatie,
                regel.vak,
                correctie_aantal,
            )

        # Check that verwerkt is set to 'V'
        regel.refresh_from_db()
        self.assertEqual(regel.verwerkt, "A")

    # igonre test, not needed
    @unittest.skip("Not implemented yet")
    def test_expected_result_when_delete_regel_does_not_exist(self, _):
        """Delete throws exception, None statement is not needed."""
        self.assertFalse("This test is not implemented yet.")
