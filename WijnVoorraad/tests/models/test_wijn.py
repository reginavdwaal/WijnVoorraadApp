"""
Unit tests for the Wijn model in the WijnVoorraad application."""

from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from WijnVoorraad.models import Wijn
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


class TestWijn(SharedTestDataMixin, TestCase):
    """Unit tests for the Wijn model."""

    def test_create_wijn(self):
        """Test that a Wijn instance can be created with valid data."""
        wijn = Wijn.objects.create(
            domein="DomeinX", naam="WijnX", wijnsoort=self.wijnsoort
        )
        self.assertEqual(wijn.domein, "DomeinX")
        self.assertEqual(wijn.naam, "WijnX")
        self.assertEqual(wijn.wijnsoort, self.wijnsoort)

    def test_str_returns_volle_naam(self):
        """Test that __str__ returns the correct full name."""
        wijn = Wijn.objects.create(
            domein="Chateaux", naam="BeauVive", wijnsoort=self.wijnsoort, jaar=2020
        )
        self.assertEqual(str(wijn), "2020 Chateaux - BeauVive")

    def test_validate_jaartal_valid(self):
        """Test that a valid year passes validation."""
        wijn = Wijn(domein="DomeinZ", naam="WijnZ", wijnsoort=self.wijnsoort, jaar=2021)
        try:
            wijn.full_clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for valid year.")

    def test_validate_jaartal_invalid(self):
        """Test that an invalid year raises a ValidationError."""
        wijn = Wijn(domein="DomeinZ", naam="WijnZ", wijnsoort=self.wijnsoort, jaar=1800)
        with self.assertRaises(ValidationError):
            wijn.full_clean()

    # skip this test for now, as it requires a WijnVoorraad model

    def test_unique_constraint(self):
        """Test that the unique constraint on (naam, domein, jaar) is enforced."""
        Wijn.objects.create(
            domein="DomeinA", naam="WijnA", wijnsoort=self.wijnsoort, jaar=2022
        )
        with self.assertRaises(IntegrityError):
            Wijn.objects.create(
                domein="DomeinA", naam="WijnA", wijnsoort=self.wijnsoort, jaar=2022
            )

    def test_volle_naam_without_jaar(self):
        """Test that volle_naam omits year if jaar is None."""
        wijn = Wijn.objects.create(
            domein="DomeinB", naam="WijnB", wijnsoort=self.wijnsoort
        )
        self.assertEqual(wijn.volle_naam, "DomeinB - WijnB")

    def test_check_unique_true(self):
        """Test that check_unique returns True for a unique combination."""
        wijn = Wijn(domein="DomeinC", naam="WijnC", wijnsoort=self.wijnsoort, jaar=2023)
        self.assertTrue(wijn.check_unique())

    def test_check_unique_false(self):
        """Test that check_unique returns False for a duplicate combination."""
        Wijn.objects.create(
            domein="DomeinD", naam="WijnD", wijnsoort=self.wijnsoort, jaar=2024
        )
        wijn = Wijn(domein="DomeinD", naam="WijnD", wijnsoort=self.wijnsoort, jaar=2024)
        self.assertFalse(wijn.check_unique())

    def test_create_copy_creates_complete_instance(self):
        """Test that create_copy creates a new Wijn instance with a modified name."""
        wijn = Wijn.objects.create(
            domein="DomeinE", naam="WijnE", wijnsoort=self.wijnsoort, jaar=2025
        )
        wijn.wijnDruivensoorten.set([self.druif1, self.druif2])

        old_id = wijn.id
        # beaware the create_copy changes the wijn variable to the new instance
        new_id = wijn.create_copy()

        self.assertNotEqual(old_id, new_id)
        self.assertTrue(Wijn.objects.filter(pk=new_id).exists())

        new_wijn = Wijn.objects.get(pk=new_id)
        self.assertIn("Copy", new_wijn.naam)
        self.assertEqual(new_wijn.wijnsoort, self.wijnsoort)
        # druivensoorten should be copied as well.
        self.assertEqual(new_wijn.wijnDruivensoorten.count(), 2)
        self.assertIn(self.druif1, new_wijn.wijnDruivensoorten.all())
        self.assertIn(self.druif2, new_wijn.wijnDruivensoorten.all())

    def test_create_copy_unique_name(self):
        """Test that create_copy generates a unique name for the copy."""
        wijn = Wijn.objects.create(
            domein="DomeinF", naam="WijnF", wijnsoort=self.wijnsoort, jaar=2026
        )
        old_id = wijn.id

        # Create multiple copies to test unique naming
        for _ in range(3):
            new_id = wijn.create_copy()
            self.assertNotEqual(old_id, new_id)
            old_id = new_id

        # Check that the last copy has a unique name
        new_wijn = Wijn.objects.get(pk=new_id)
        self.assertTrue(new_wijn.naam.startswith("WijnF - Copy"))

    def test_create_copy_too_many_copies(self):
        """Test that create_copy raises ValidationError after too many copies."""
        wijn = Wijn.objects.create(
            domein="DomeinG", naam="WijnG", wijnsoort=self.wijnsoort, jaar=2027
        )
        orginal_id = wijn.id
        # Create 16 copies to reach the limit
        for _ in range(15):
            # need to get the original instance again, as create_copy changes the instance
            # and we want to copy the original instance each time
            wijn = Wijn.objects.get(pk=orginal_id)
            wijn.create_copy()

        # The next copy should raise a ValidationError
        with self.assertRaises(ValidationError):
            wijn = Wijn.objects.get(pk=orginal_id)
            wijn.create_copy()

    def test_check_afsluiten_sets_datum_afgesloten(self):
        """Test that check_afsluiten sets datumAfgesloten when no voorraad exists, using a mock."""
        wijn = Wijn.objects.create(
            domein="DomeinH", naam="WijnH", wijnsoort=self.wijnsoort, jaar=2028
        )
        # Patch the aggregate method to simulate no voorraad
        with patch("WijnVoorraad.models.WijnVoorraad.objects.filter") as mock_filter:
            mock_filter.return_value.aggregate.return_value = {"aantal": None}
            wijn.check_afsluiten()
            self.assertIsNotNone(wijn.datumAfgesloten)

    def test_check_afsluiten_unsets_datum_afgesloten(self):
        """Test that check_afsluiten unsets datumAfgesloten when voorraad exists, using a mock."""
        wijn = Wijn.objects.create(
            domein="DomeinI",
            naam="WijnI",
            wijnsoort=self.wijnsoort,
            jaar=2029,
            datumAfgesloten="2024-01-01",
        )
        with patch("WijnVoorraad.models.WijnVoorraad.objects.filter") as mock_filter:
            mock_filter.return_value.aggregate.return_value = {"aantal": 5}
            wijn.check_afsluiten()
            self.assertIsNone(wijn.datumAfgesloten)

    def test_check_fuzzy_selectie_various_fields(self):
        """Test that check_fuzzy_selectie returns True if the search string
        matches any relevant field."""
        wijn = Wijn.objects.create(
            domein="Chateau Test",
            naam="Testwijn",
            wijnsoort=self.wijnsoort,
            jaar=2021,
            land="Frankrijk",
            streek="Bordeaux",
            classificatie="AOC",
            opmerking="Zeer fruitig",
        )
        # druif = DruivenSoort.objects.create(omschrijving="Merlot")
        wijn.wijnDruivensoorten.add(self.druif)

        # Should match on naam
        self.assertTrue(wijn.check_fuzzy_selectie("testwijn"))
        # Should match on domein
        self.assertTrue(wijn.check_fuzzy_selectie("chateau"))
        # Should match on wijnsoort
        self.assertTrue(wijn.check_fuzzy_selectie(self.wijnsoort.omschrijving.lower()))
        # Should match on jaar
        self.assertTrue(wijn.check_fuzzy_selectie("2021"))
        # Should match on land
        self.assertTrue(wijn.check_fuzzy_selectie("frankrijk"))
        # Should match on streek
        self.assertTrue(wijn.check_fuzzy_selectie("bordeaux"))
        # Should match on classificatie
        self.assertTrue(wijn.check_fuzzy_selectie("aoc"))
        # Should match on opmerking
        self.assertTrue(wijn.check_fuzzy_selectie("fruitig"))
        # Should match on druivensoort
        self.assertTrue(wijn.check_fuzzy_selectie("merlot"))
        # Should return True if fuzzy_selectie is empty
        self.assertTrue(wijn.check_fuzzy_selectie(""))
        # Should return False for non-matching string
        self.assertFalse(wijn.check_fuzzy_selectie("nonexistent"))

        # Should be able to handle None values gracefully
        wijn.classificatie = None
        self.assertFalse(wijn.check_fuzzy_selectie("abc"))

        # Should be able to handle empty values gracefully
        wijn.classificatie = ""
        self.assertFalse(wijn.check_fuzzy_selectie("abc"))

        # should return true if search query is empty
        self.assertTrue(wijn.check_fuzzy_selectie(""))
