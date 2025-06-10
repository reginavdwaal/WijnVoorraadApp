"""module for unit test of ontvangst class"""

import datetime
from unittest.mock import patch

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from WijnVoorraad.models import Deelnemer, Ontvangst, Wijn
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


class TestOntvangst(SharedTestDataMixin, TestCase):
    """Unit tests for the Ontvangst model."""

    def test_delete_wijn_prevented_if_ontvangst_contains_wijn(self):
        """Test that a Wijn cannot be deleted if it has related Ontvangst instances."""
        ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date(),
        )
        with self.assertRaises(IntegrityError):
            self.wijn.delete()
        # Ensure the Ontvangst instance still exists
        self.assertTrue(Ontvangst.objects.filter(pk=ontvangst.pk).exists())

    def test_delete_deelnemer_prevented_if_ontvangst_contains_deelnemer(self):
        """Test that a Deelnemer cannot be deleted if it has related Ontvangst instances."""
        ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date(),
        )
        with self.assertRaises(IntegrityError):
            self.deelnemer.delete()
        # Ensure the Ontvangst instance still exists
        self.assertTrue(Ontvangst.objects.filter(pk=ontvangst.pk).exists())

    def test_create_ontvangst(self):
        """Test that an Ontvangst instance can be created."""
        ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            leverancier="LeverancierX",
            website="https://example.com",
            prijs=12.50,
            opmerking="Testopmerking",
        )
        ontvangst = Ontvangst.objects.get(pk=ontvangst.pk)
        self.assertEqual(ontvangst.deelnemer, self.deelnemer)
        self.assertEqual(ontvangst.wijn, self.wijn)
        self.assertEqual(ontvangst.leverancier, "LeverancierX")
        self.assertEqual(ontvangst.website, "https://example.com")
        self.assertEqual(ontvangst.prijs, 12.50)
        self.assertEqual(ontvangst.opmerking, "Testopmerking")
        # Ensure the date is set to today
        self.assertEqual(ontvangst.datumOntvangst, datetime.date.today())

    def test_ontvangst_leverancier_max_length(self):
        """Test that the leverancier field has a max length of 200 characters."""
        with self.assertRaises(ValidationError) as exc:
            ontvangst = Ontvangst(
                deelnemer=self.deelnemer,
                wijn=self.wijn,
                leverancier="L" * 201,  # 201 characters
            )
            ontvangst.full_clean()
        self.assertIn("200", str(exc.exception))

    def test_ontvangst_opmerkingen_max_length(self):
        """Test that the opmerking field has a max length of 4000 characters."""
        with self.assertRaises(ValidationError) as exc:
            ontvangst = Ontvangst(
                deelnemer=self.deelnemer,
                wijn=self.wijn,
                opmerking="O" * 4001,  # 4001 characters
            )
            ontvangst.full_clean()
        self.assertIn("4000", str(exc.exception))

    def test_ontvangst_website_max_length(self):
        """Test that the website field has a max length of 200 characters."""
        with self.assertRaises(ValidationError) as exc:
            ontvangst = Ontvangst(
                deelnemer=self.deelnemer,
                wijn=self.wijn,
                website="https://example.com/" + "W" * 190,  # 200 characters total
            )
            ontvangst.full_clean()
        self.assertIn("200", str(exc.exception))

    def test_str_returns_expected(self):
        """Test that __str__ returns the correct string."""
        ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date(),
        )
        expected = (
            f"{self.deelnemer.naam} - {self.wijn.volle_naam} - "
            f"{ontvangst.datumOntvangst.strftime('%d-%m-%Y')}"
        )
        self.assertEqual(str(ontvangst), expected)

    def test_create_copy_creates_new_instance(self):
        """Test that create_copy creates a new Ontvangst instance with a new date."""
        ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            # set the datumOntvangst on last month
            datumOntvangst=timezone.now().date() - datetime.timedelta(days=30),
        )
        old_id = ontvangst.id
        new_id = ontvangst.create_copy()
        self.assertNotEqual(old_id, new_id)
        self.assertTrue(Ontvangst.objects.filter(pk=new_id).exists())
        new_ontvangst = Ontvangst.objects.get(pk=new_id)
        self.assertEqual(new_ontvangst.deelnemer, ontvangst.deelnemer)
        self.assertEqual(new_ontvangst.wijn, ontvangst.wijn)
        self.assertEqual(new_ontvangst.datumOntvangst, datetime.date.today())

    def test_multiple_ontvangsten_should_be_ordered(self):
        """Test that multiple Ontvangst instances are ordered by date."""
        deelnemer_kees = Deelnemer.objects.create(
            naam="Kees", standaardLocatie=self.locatie
        )
        wijn_a = Wijn.objects.create(
            domein="DomeinX", naam="WijnA", wijnsoort=self.wijnsoort
        )
        ontv_min_two_days = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date() - datetime.timedelta(days=2),
        )
        ontv_min_one_day = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date() - datetime.timedelta(days=1),
        )

        ontv_default_different_deelnemer = Ontvangst.objects.create(
            deelnemer=deelnemer_kees,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date(),
        )
        ontv_default = self.ontvangst

        ontv_default_different_wijn = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=wijn_a,
            datumOntvangst=timezone.now().date(),
        )

        ontvangsten = list(Ontvangst.objects.all())

        expected_order = [
            ontv_default_different_wijn,
            ontv_default,
            ontv_default_different_deelnemer,
            ontv_min_one_day,
            ontv_min_two_days,
        ]
        self.assertEqual(ontvangsten, expected_order)

    def test_check_fuzzy_selectie_various_fields(self):
        # Test that check_fuzzy_selectie returns True if the search string matches
        # leverancier, opmerking, or related wijn."""
        ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            leverancier="LeverancierX",
            opmerking="Speciale opmerking",
        )

        # Should match on leverancier
        self.assertTrue(ontvangst.check_fuzzy_selectie("leverancierx"))
        # Should match on opmerking
        self.assertTrue(ontvangst.check_fuzzy_selectie("speciale"))

        # Should return True if fuzzy_selectie is empty
        self.assertTrue(ontvangst.check_fuzzy_selectie(""))
        # Should return False for non-matching string
        self.assertFalse(ontvangst.check_fuzzy_selectie("nonexistent"))

    def test_check_fuzzy_selectie_leverancier_and_empty(self):
        """Test that check_fuzzy_selectie handles leverancier being None or empty string."""

        ontvangst_empty = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            leverancier="",
            opmerking="Nog een opmerking",
        )
        # Should not raise error and should match opmerking
        self.assertTrue(ontvangst_empty.check_fuzzy_selectie("nog"))
        # Should return False for non-matching string
        self.assertFalse(ontvangst_empty.check_fuzzy_selectie("nonexistent"))

    def test_check_fuzzy_selectie_should_call_wijn_check_fuzzy_selectie(self):
        """Test that check_fuzzy_selectie calls the related wijn's check_fuzzy_selectie."""

        # Mock the wijn's check_fuzzy_selectie method
        with patch("WijnVoorraad.models.Wijn.check_fuzzy_selectie") as mock_check:
            self.ontvangst.check_fuzzy_selectie("wijnnaam")
            # assert mock is called with the correct argument
            mock_check.assert_called_once_with("wijnnaam")

    def test_check_fuzzy_selectie_should_not_call_wijn_check_when_ontvangst_matches(
        self,
    ):
        # Test that check_fuzzy_selectie does not call the related wijn's check_fuzzy_selectie
        self.ontvangst.opmerking = "leverancierx"
        with patch("WijnVoorraad.models.Wijn.check_fuzzy_selectie") as mock_check:
            self.ontvangst.check_fuzzy_selectie("leverancierx")
            # assert mock is not called since the check should match on leverancier
            mock_check.assert_not_called()
