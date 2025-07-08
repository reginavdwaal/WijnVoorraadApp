"""unit tests for the Bestelling model."""

import datetime
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from WijnVoorraad.models import Bestelling, Deelnemer, Locatie
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


class TestBestelling(SharedTestDataMixin, TestCase):
    """Unit tests for the Bestelling model.
    This class tests the creation, validation, and behavior of Bestelling instances.
    It ensures that Bestelling instances can be created with valid data,
    that they enforce integrity constraints, and that they behave correctly
    when interacting with related models such as Deelnemer and Locatie."""

    def test_valid_bestelling_can_be_created(self):
        """Test that a Bestelling instance can be created with valid data."""
        bestelling = self.create_bestelling(opmerking="Test bestelling")

        self.assertEqual(bestelling.deelnemer, self.deelnemer)
        self.assertEqual(bestelling.vanLocatie, self.locatie)
        self.assertEqual(bestelling.opmerking, "Test bestelling")
        self.assertIsNotNone(bestelling.datumAangemaakt)

    def test_bestelling_without_deelnemer_raises_error(self):
        """Test that a Bestelling cannot be created without a deelnemer."""
        with self.assertRaises(IntegrityError):
            Bestelling.objects.create(
                vanLocatie=self.locatie,
                datumAangemaakt=timezone.now().date(),
                opmerking="Test bestelling zonder deelnemer",
            )

    def test_bestelling_without_van_locatie_raises_error(self):
        """Test that a Bestelling cannot be created without a vanLocatie."""
        with self.assertRaises(IntegrityError):
            Bestelling.objects.create(
                deelnemer=self.deelnemer,
                datumAangemaakt=timezone.now().date(),
                opmerking="Test bestelling zonder vanLocatie",
            )

    def test_bestelling_without_datum_aangemaakt_uses_today(self):
        """Test that a Bestelling without datumAangemaakt uses today's date."""
        bestelling = self.create_bestelling()

        self.assertEqual(bestelling.datumAangemaakt, timezone.now().date())

    def test_deelnemer_delete_prevented_if_bestelling_exists(self):
        """Test that a Deelnemer cannot be deleted if there is a Bestelling object."""
        bestelling = self.create_bestelling()

        with self.assertRaises(IntegrityError):
            self.deelnemer.delete()
        # Ensure the Bestelling instance still exists
        self.assertTrue(Bestelling.objects.filter(pk=bestelling.pk).exists())

    def test_locatie_delete_prevented_if_bestelling_exists(self):
        """Test that a Locatie cannot be deleted if there is a Bestelling object."""
        bestelling = self.create_bestelling()

        with self.assertRaises(IntegrityError):
            self.locatie.delete()
        # Ensure the Bestelling instance still exists
        self.assertTrue(Bestelling.objects.filter(pk=bestelling.pk).exists())

    def test_str_returns_deelnemer_date_location(self):
        """Test that __str__ returns the correct string."""
        bestelling = self.create_bestelling(opmerking="Test bestelling")
        expected = (
            f"{self.deelnemer.naam} - "
            f"{bestelling.datumAangemaakt.strftime('%d-%m-%Y')} - "
            f"{self.locatie.omschrijving} "
        )
        self.assertEqual(str(bestelling), expected)

    def test_afboeken_calls_afboeken_for_all_regels_verzameld(self):
        """Test that afboeken calls afboeken for all regels in the bestelling."""
        bestelling = self.create_bestelling(opmerking="Test bestelling")

        # Create some regels for the bestelling
        with (
            patch("WijnVoorraad.models.BestellingRegel.afboeken") as mock_afboeken,
            patch(
                "WijnVoorraad.models.WijnVoorraad.Bijwerken_rsv_erbij",
                return_value=None,
            ),
        ):
            # Create some regels for the bestelling (mock is active here)
            self.create_bestellingregel(
                bestelling, ontvangst=self.ontvangst, aantal=2, is_verzameld=True
            )
            self.create_bestellingregel(
                bestelling, ontvangst=self.ontvangst, aantal=4, is_verzameld=True
            )
            self.create_bestellingregel(
                bestelling, ontvangst=self.ontvangst, aantal=2, is_verzameld=False
            )
            self.create_bestellingregel(
                bestelling,
                ontvangst=self.ontvangst,
                aantal=4,
                is_verzameld=True,
                verwerkt="A",
            )

            # Call afboeken on the bestelling
            bestelling.afboeken()
            # Check that afboeken was called for each regel
            self.assertEqual(mock_afboeken.call_count, 2)

    def test_bestellingen_with_regels_are_ordered(self):
        """Test that Bestellingen with regels are ordered by datumAangemaakt,
        deelnemer and vanLocatie."""

        locatie_elders = Locatie.objects.create(
            omschrijving="Elders", aantal_kolommen=1
        )
        deelnemer_anders = Deelnemer.objects.create(naam="Andere Deelnemer")

        best_2_days_ago = self.create_bestelling(
            datum_aangemaakt=timezone.now().date() - datetime.timedelta(days=2)
        )
        best_1_day_ago = self.create_bestelling(
            datum_aangemaakt=timezone.now().date() - datetime.timedelta(days=1)
        )
        # defaults: Deelnemer= Test Deelnemer, Locatie= Kelder
        best_today_default = self.create_bestelling(
            datum_aangemaakt=timezone.now().date()
        )
        best_today_andere_deelnemer = self.create_bestelling(
            deelnemer=deelnemer_anders,
            datum_aangemaakt=timezone.now().date(),
        )
        best_today_elders = self.create_bestelling(
            van_locatie=locatie_elders,
            datum_aangemaakt=timezone.now().date(),
        )

        # Get all bestellingen and check the order
        bestellingen = list(Bestelling.objects.all())

        # Check the order of bestellingen
        # The expected order is based on the date and then by deelnemer and vanLocatie
        # based on meta of model Bestelling
        expected_order = [
            best_today_andere_deelnemer,
            best_today_elders,
            best_today_default,
            best_1_day_ago,
            best_2_days_ago,
        ]
        self.assertEqual(bestellingen, expected_order)

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_rsv_erbij", return_value=True)
    def test_afsluiten_should_set_date_if_no_lines_not_verwerkt(self, _):
        """Test that afsluiten sets datumAfgesloten if no lines are not
        verwerkt."""
        bestelling = self.create_bestelling(opmerking="Test afsluiten")

        # Initially, datumAfgesloten should be None
        self.assertIsNone(bestelling.datumAfgesloten)

        # Call afsluiten
        bestelling.check_afsluiten()

        # Check that datumAfgesloten is set to today
        self.assertEqual(bestelling.datumAfgesloten, timezone.now().date())

        self.create_bestellingregel(
            bestelling,
            ontvangst=self.ontvangst,
            aantal=2,
            is_verzameld=False,
            verwerkt="N",
        )

        # Call afsluiten
        bestelling.check_afsluiten()

        # Check that datumAfgesloten is set to None
        self.assertIsNone(bestelling.datumAfgesloten)

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_rsv_erbij", return_value=True)
    def test_afsluiten_should_not_date_if_some_lines_not_verwerkt(self, _):
        """Test that afsluiten does not set datumAfgesloten if some lines are not verwerkt."""
        bestelling = self.create_bestelling(opmerking="Test afsluiten")

        # Create a regel that is not verzameld and not verwerkt
        self.create_bestellingregel(
            bestelling,
            ontvangst=self.ontvangst,
            aantal=2,
            is_verzameld=False,
            verwerkt="N",
        )
        self.create_bestellingregel(
            bestelling,
            ontvangst=self.ontvangst,
            aantal=2,
            is_verzameld=False,
            verwerkt="V",
        )

        # Initially, datumAfgesloten should be None
        self.assertIsNone(bestelling.datumAfgesloten)

        # Call afsluiten
        bestelling.check_afsluiten()

        # Check that datumAfgesloten is still None
        self.assertIsNone(bestelling.datumAfgesloten)

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_rsv_erbij", return_value=True)
    def test_afsluiten_should_set_date_if_lines_verwerkt(self, _):
        # Test that afsluiten does set datumAfgesloten if all lines are verwerkt

        bestelling = self.create_bestelling(opmerking="Test afsluiten")

        # Initially, datumAfgesloten should be None
        self.assertIsNone(bestelling.datumAfgesloten)

        # Create a regel that is not verzameld and not verwerkt
        self.create_bestellingregel(
            bestelling,
            ontvangst=self.ontvangst,
            aantal=2,
            is_verzameld=True,
            verwerkt="A",
        )

        self.create_bestellingregel(
            bestelling,
            ontvangst=self.ontvangst,
            aantal=2,
            is_verzameld=False,
            verwerkt="A",
        )

        # Call afsluiten
        bestelling.check_afsluiten()

        # Check that datumAfgesloten is set to today
        self.assertEqual(bestelling.datumAfgesloten, timezone.now().date())
