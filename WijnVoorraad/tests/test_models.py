"""
Unit tests for the WijnVoorraad Django models.

This module covers model creation, string representations, constraints,
ordering, validation, and custom methods for all main models in the app.
"""

# pylint: disable=no-member
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import datetime

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

# Import the models to be tested
from WijnVoorraad.models import (
    AIUsage,
    Bestelling,
    BestellingRegel,
    Deelnemer,
    DruivenSoort,
    Locatie,
    Ontvangst,
    Vak,
    VoorraadMutatie,
    Wijn,
    WijnDruivensoort,
    WijnSoort,
)


class TestLocatie(TestCase):
    def test_create_locatie(self):
        locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=3)
        locatie2 = Locatie.objects.create(omschrijving="Zolder")
        self.assertEqual(locatie.omschrijving, "Kelder")
        self.assertEqual(locatie.aantal_kolommen, 3)
        self.assertEqual(locatie2.omschrijving, "Zolder")
        self.assertEqual(locatie2.aantal_kolommen, 1)

    def test_str_returns_omschrijving(self):
        locatie = Locatie.objects.create(omschrijving="Garage")
        self.assertEqual(str(locatie), "Garage")

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


class TestWijnSoort(TestCase):
    # def setUp(self) :
    #     defaultProcedure = Procedure.objects.create(title="procedure one", step=1)
    #     CheckItem.objects.create(item="item one", procedure = defaultProcedure , step=3)
    # #    CheckItem.objects.create(item="item two", procedure = defaultProcedure , step=1)
    #     CheckItem.objects.create(item="item three", procedure = defaultProcedure , step=5)

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


class TestDruivenSoort(TestCase):
    # def setUp(self) :
    #     defaultProcedure = Procedure.objects.create(title="procedure one", step=1)
    #     CheckItem.objects.create(item="item one", procedure = defaultProcedure , step=3)
    # #    CheckItem.objects.create(item="item two", procedure = defaultProcedure , step=1)
    #     CheckItem.objects.create(item="item three", procedure = defaultProcedure , step=5)

    def test_druivensoort_not_longer_than_200(self):
        with self.assertRaises(ValidationError) as exc:
            druivensoort = DruivenSoort.objects.create(omschrijving="abc" * 100)
            druivensoort.full_clean()
        self.assertIn("200", str(exc.exception))

    def test_druivensoort_200_should_fit(self):
        druivensoort = DruivenSoort.objects.create(omschrijving="ab" * 100)
        druivensoort.full_clean()
        self.assertEqual(len(druivensoort.omschrijving), 200)

    def test_str_returns_omschrijving(self):
        druivensoort = DruivenSoort.objects.create(omschrijving="Precies Dit")
        self.assertEqual(str(druivensoort), "Precies Dit")


class TestVak(TestCase):
    def setUp(self):
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=2)

    def test_create_vak(self):
        vak = Vak.objects.create(locatie=self.locatie, code="A1", capaciteit=10)
        self.assertEqual(vak.locatie, self.locatie)
        self.assertEqual(vak.code, "A1")
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
        Vak.objects.create(locatie=self.locatie, code="A1", capaciteit=1)
        vakken = list(Vak.objects.all())
        sorted_vakken = sorted(vakken, key=lambda v: (v.locatie.omschrijving, v.code))
        self.assertEqual(vakken, sorted_vakken)


class TestDeelnemer(TestCase):
    def setUp(self):
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=2)
        self.user = get_user_model().objects.create(username="testuser")

    def test_create_deelnemer(self):
        deelnemer = Deelnemer.objects.create(naam="Jan", standaardLocatie=self.locatie)
        self.assertEqual(deelnemer.naam, "Jan")
        self.assertEqual(deelnemer.standaardLocatie, self.locatie)

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


class TestWijn(TestCase):
    """Unit tests for the Wijn model."""

    def setUp(self):
        """Set up a WijnSoort for use in tests."""
        self.wijnsoort = WijnSoort.objects.create(omschrijving="Rood")
        self.druif1 = DruivenSoort.objects.create(omschrijving="Merlot")
        self.druif2 = DruivenSoort.objects.create(omschrijving="Cabernet Sauvignon")

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


class TestWijnDruivensoort(TestCase):
    """Unit tests for the WijnDruivensoort model."""

    def setUp(self):
        self.wijnsoort = WijnSoort.objects.create(omschrijving="Rood")
        self.druif = DruivenSoort.objects.create(omschrijving="Merlot")
        self.druif2 = DruivenSoort.objects.create(omschrijving="Cabernet")
        self.wijn = Wijn.objects.create(
            domein="Test", naam="TestWijn", wijnsoort=self.wijnsoort
        )

    def test_create_wijndruivensoort(self):
        """Test that a WijnDruivensoort instance can be created."""
        wd = WijnDruivensoort.objects.create(wijn=self.wijn, druivensoort=self.druif)
        self.assertEqual(wd.wijn, self.wijn)
        self.assertEqual(wd.druivensoort, self.druif)

    def test_str_returns_expected(self):
        """Test that __str__ returns the correct string."""
        wd = WijnDruivensoort.objects.create(wijn=self.wijn, druivensoort=self.druif)
        expected = f"{self.wijn.volle_naam} - {self.druif.omschrijving}"
        self.assertEqual(str(wd), expected)

    def test_unique_constraint(self):
        """Test that the unique constraint on (wijn, druivensoort) is enforced."""
        WijnDruivensoort.objects.create(wijn=self.wijn, druivensoort=self.druif)
        with self.assertRaises(IntegrityError):
            WijnDruivensoort.objects.create(wijn=self.wijn, druivensoort=self.druif)

    def test_ordering(self):
        """Test that ordering is by wijn and druivensoort."""
        WijnDruivensoort.objects.create(wijn=self.wijn, druivensoort=self.druif2)
        WijnDruivensoort.objects.create(wijn=self.wijn, druivensoort=self.druif)
        wijndruiven = list(WijnDruivensoort.objects.all())
        sorted_wijndruiven = sorted(
            wijndruiven,
            key=lambda wd: (wd.wijn.volle_naam, wd.druivensoort.omschrijving),
        )
        self.assertEqual(wijndruiven, sorted_wijndruiven)


class TestOntvangst(TestCase):
    """Unit tests for the Ontvangst model."""

    def setUp(self):
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=1)
        self.deelnemer = Deelnemer.objects.create(
            naam="Jan", standaardLocatie=self.locatie
        )
        self.wijnsoort = WijnSoort.objects.create(omschrijving="Rood")
        self.wijn = Wijn.objects.create(
            domein="DomeinX", naam="WijnX", wijnsoort=self.wijnsoort
        )

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
        """Test that the opmerking field has a max length of 200 characters."""
        with self.assertRaises(ValidationError) as exc:
            ontvangst = Ontvangst(
                deelnemer=self.deelnemer,
                wijn=self.wijn,
                opmerking="O" * 201,  # 201 characters
            )
            ontvangst.full_clean()
        self.assertIn("200", str(exc.exception))

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
        expected = f"{self.deelnemer.naam} - {self.wijn.volle_naam} - {ontvangst.datumOntvangst.strftime('%d-%m-%Y')}"
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
        ontvangst1 = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date() - datetime.timedelta(days=2),
        )
        ontvangst2 = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date() - datetime.timedelta(days=1),
        )

        ontvangst3 = Ontvangst.objects.create(
            deelnemer=deelnemer_kees,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date(),
        )
        ontvangst4 = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date(),
        )
        ontvangst5 = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=wijn_a,
            datumOntvangst=timezone.now().date(),
        )

        ontvangsten = list(Ontvangst.objects.all())

        self.assertEqual(ontvangsten[0], ontvangst5)
        self.assertEqual(ontvangsten[1], ontvangst4)
        self.assertEqual(ontvangsten[2], ontvangst3)
        self.assertEqual(ontvangsten[3], ontvangst2)
        self.assertEqual(ontvangsten[4], ontvangst1)


class TestVoorraadMutatie(TestCase):
    """Unit tests for the VoorraadMutatie model."""

    def setUp(self):
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=1)
        self.vak_a1 = Vak.objects.create(locatie=self.locatie, code="A1", capaciteit=5)
        self.vak_a2 = Vak.objects.create(locatie=self.locatie, code="A2", capaciteit=10)

        self.deelnemer = Deelnemer.objects.create(
            naam="Jan", standaardLocatie=self.locatie
        )
        self.wijnsoort = WijnSoort.objects.create(omschrijving="Rood")
        self.wijn = Wijn.objects.create(
            domein="DomeinX", naam="WijnX", wijnsoort=self.wijnsoort
        )
        self.ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=self.wijn,
            datumOntvangst=timezone.now().date(),
        )

    def test_ontvangst_can_not_be_deleted_if_linked_to_voorraad_mutatie(self):
        """Test that an Ontvangst cannot be deleted if it has related VoorraadMutatie instances."""

        # Create a VoorraadMutatie linked to the Ontvangst
        VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        with self.assertRaises(IntegrityError):
            self.ontvangst.delete()
        # Ensure the Ontvangst instance still exists
        self.assertTrue(Ontvangst.objects.filter(pk=self.ontvangst.pk).exists())

    def test_locatie_can_not_be_deleted_if_linked_to_voorraad_mutatie(self):
        """Test that a Locatie cannot be deleted if it has related VoorraadMutatie instances."""
        locatie = Locatie.objects.create(omschrijving="Zolder", aantal_kolommen=1)
        # Create a VoorraadMutatie linked to the Locatie
        VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=locatie,
        )
        with self.assertRaises(IntegrityError):
            locatie.delete()
        # Ensure the Locatie instance still exists
        self.assertTrue(Locatie.objects.filter(pk=locatie.pk).exists())

    def test_in_uit_can_only_have_i_or_u(self):
        """Test that in_uit can only be 'i' or 'u'."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            in_uit="x",  # Invalid action
            datum=timezone.now().date(),
            locatie=self.locatie,
        )

        with self.assertRaises(ValidationError) as exc:
            voorraad_mutatie.full_clean()
        self.assertIn("Waarde 'x'", str(exc.exception))

    def test_actie_can_only_have_predefined_values(self):
        """Test that actie can only be one of the predefined values."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="onbekend",  # Invalid action
            datum=timezone.now().date(),
            locatie=self.locatie,
        )

        with self.assertRaises(ValidationError) as exc:
            voorraad_mutatie.full_clean()
        self.assertIn("Waarde 'onbekend'", str(exc.exception))

    def test_omschrijving_can_not_be_longer_then_200(self):
        """Test that omschrijving cannot be longer than 200 characters."""
        with self.assertRaises(ValidationError) as exc:
            voorraad_mutatie = VoorraadMutatie(
                ontvangst=self.ontvangst,
                aantal=10,
                actie="toevoegen",
                datum=timezone.now().date(),
                locatie=self.locatie,
                omschrijving="a" * 201,  # 201 characters
            )
            voorraad_mutatie.full_clean()
        self.assertIn("200", str(exc.exception))

    def test_string_should_contain_wijn_deelnemer_inuit_datum_and_pk(self):
        """Test that __str__ returns a string containing wijn, deelnemer, in/uit, datum, and pk."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        expected = (
            f"{self.wijn.volle_naam} - "
            f"{self.deelnemer.naam} - "
            f"{voorraad_mutatie.in_uit} - "
            f"{voorraad_mutatie.datum.strftime('%d-%m-%Y')} - "
            f"{voorraad_mutatie.pk}"
        )
        self.assertEqual(str(voorraad_mutatie), expected)

    def test_clean_should_call_WijnVoorraad_check_voorraad_wijziging(self):
        """Test that clean method calls WijnVoorraad.check_voorraad_wijziging."""
        voorraad_mutatie = VoorraadMutatie(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        with patch(
            "WijnVoorraad.models.WijnVoorraad.check_voorraad_wijziging"
        ) as mock_check:
            voorraad_mutatie.clean()
            mock_check.assert_called_once_with(voorraad_mutatie, None)

    def test_save_should_call_WijnVoorraad_Bijwerken(self):
        """Test that save method calls WijnVoorraad.Bijwerken."""
        voorraad_mutatie = VoorraadMutatie(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        with patch("WijnVoorraad.models.WijnVoorraad.Bijwerken") as mock_bijwerken:
            voorraad_mutatie.save()
            mock_bijwerken.assert_called_once_with(voorraad_mutatie, None)

    def test_save_should_call_WijnVoorraad_Bijwerken_with_old_mutatie(self):
        """Test that save method calls WijnVoorraad.Bijwerken with old_mutatie."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )

        voorraad_mutatie.save()
        with patch("WijnVoorraad.models.WijnVoorraad.Bijwerken") as mock_bijwerken:
            voorraad_mutatie.aantal = 20
            voorraad_mutatie.save()
            mock_bijwerken.assert_called_once_with(voorraad_mutatie, voorraad_mutatie)

    def test_delete_should_call_wijnvoorraad_check_voorraad_wijziging(self):
        """Test that delete method calls WijnVoorraad.check_voorraad_wijziging."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        voorraad_mutatie.refresh_from_db()  # Ensure the instance is saved and has an ID
        saved_mutatie = VoorraadMutatie.objects.get(pk=voorraad_mutatie.id)

        voorraad_mutatie.aantal = 20  # Change the aantal to trigger a change

        with patch(
            "WijnVoorraad.models.WijnVoorraad.check_voorraad_wijziging"
        ) as mock_check:
            voorraad_mutatie.delete()
            mock_check.assert_called_once_with(None, saved_mutatie)

    def test_delete_should_call_wijnVoorraad_bijwerken(self):
        """Test that delete method calls WijnVoorraad.Bijwerken."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        voorraad_mutatie.refresh_from_db()  # Ensure the instance is saved and has an ID
        saved_mutatie = VoorraadMutatie.objects.get(pk=voorraad_mutatie.id)
        voorraad_mutatie.aantal = 20
        with patch("WijnVoorraad.models.WijnVoorraad.Bijwerken") as mock_bijwerken:
            voorraad_mutatie.delete()
            mock_bijwerken.assert_called_once_with(None, saved_mutatie)

    def test_drinken_should_create_and_save_u_mutatie_with_action_d_now_aantal_1(self):
        """Test that drinken creates a 'U' mutatie with action 'D', date now, and aantal 1."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        with patch("WijnVoorraad.models.WijnVoorraad.Bijwerken") as mock_bijwerken:
            voorraad_mutatie.drinken(self.ontvangst, self.locatie)
            # Check that a new VoorraadMutatie was created
            self.assertEqual(VoorraadMutatie.objects.count(), 2)
            new_mutatie = VoorraadMutatie.objects.last()
            self.assertEqual(new_mutatie.in_uit, "U")
            self.assertEqual(new_mutatie.actie, "D")
            self.assertEqual(new_mutatie.aantal, 1)
            self.assertEqual(new_mutatie.datum, timezone.now().date())
            mock_bijwerken.assert_called_once_with(new_mutatie, None)

    def test_voorraad_plus_1_should_create_and_save_i_mutatie_with_action_k_now_aantal_1(
        self,
    ):
        """Test that voorraad_plus_1 creates an 'I' mutatie with action 'K', date now, and aantal 1."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        with patch("WijnVoorraad.models.WijnVoorraad.Bijwerken") as mock_bijwerken:
            voorraad_mutatie.voorraad_plus_1(self.ontvangst, self.locatie)
            # Check that a new VoorraadMutatie was created
            self.assertEqual(VoorraadMutatie.objects.count(), 2)
            new_mutatie = VoorraadMutatie.objects.last()
            self.assertEqual(new_mutatie.in_uit, "I")
            self.assertEqual(new_mutatie.actie, "K")
            self.assertEqual(new_mutatie.aantal, 1)
            self.assertEqual(new_mutatie.datum, timezone.now().date())
            mock_bijwerken.assert_called_once_with(new_mutatie, None)

    def test_verplaatsen_should_create_and_save_u_mutatie_with_action_v_now_aantal(
        self,
    ):
        """Test that verplaatsen creates an 'U' mutatie with
        action 'V', date now, and aantal as defined."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        voorraad_mutatie.verplaatsen(
            self.ontvangst,
            locatie_oud=self.locatie,
            aantal=2,
            vak_oud=self.vak_a1,
            locatie_nieuw=self.locatie,
            vak_nieuw=self.vak_a2,
        )
        # Check that a new VoorraadMutatie was created
        self.assertEqual(VoorraadMutatie.objects.count(), 3)
        # get the outgoing U mutatie
        try:
            new_mutatie = VoorraadMutatie.objects.get(
                in_uit="U", actie="V", aantal=2, locatie=self.locatie
            )
        except VoorraadMutatie.DoesNotExist:
            self.fail("No outgoing 'U' mutatie found with action 'V' and aantal 2")

        self.assertEqual(new_mutatie.in_uit, "U")
        self.assertEqual(new_mutatie.actie, "V")
        self.assertEqual(new_mutatie.aantal, 2)
        self.assertEqual(new_mutatie.datum, timezone.now().date())

        # get the outgoing I mutatie
        try:
            new_mutatie = VoorraadMutatie.objects.get(
                in_uit="I", actie="V", aantal=2, locatie=self.locatie
            )
        except VoorraadMutatie.DoesNotExist:
            self.fail("No incoming 'I' mutatie found with action 'V' and aantal 2")

        self.assertEqual(new_mutatie.in_uit, "I")
        self.assertEqual(new_mutatie.actie, "V")
        self.assertEqual(new_mutatie.aantal, 2)
        self.assertEqual(new_mutatie.datum, timezone.now().date())

    def test_afboeken_should_create_and_save_u_mutatie_with_action_a_now_aantal_1(self):
        """Test that afboeken creates an 'U' mutatie with action 'A', date now, and aantal 1."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        with (
            patch("WijnVoorraad.models.WijnVoorraad.Bijwerken") as mock_bijwerken,
            patch(
                "WijnVoorraad.models.WijnVoorraad.check_voorraad_wijziging",
                return_value=None,
            ),
        ):

            voorraad_mutatie.afboeken(self.ontvangst, self.locatie, aantal=1, vak=None)
            # Check that a new VoorraadMutatie was created
            self.assertEqual(VoorraadMutatie.objects.count(), 2)
            new_mutatie = VoorraadMutatie.objects.last()
            self.assertEqual(new_mutatie.in_uit, "U")
            self.assertEqual(new_mutatie.actie, "A")
            self.assertEqual(new_mutatie.aantal, 1)
            self.assertEqual(new_mutatie.datum, timezone.now().date())
            mock_bijwerken.assert_called_once_with(new_mutatie, None)


class TestAIUsage(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="aiuser")

    def test_create_aiusage_with_user(self):
        """Test that AIUsage can be created with a real user."""
        usage = AIUsage.objects.create(
            user=self.user,
            model="gpt-4",
            response_time=timezone.now(),
            response_content="Test response",
            response_tokens_used=42,
        )
        self.assertEqual(usage.user, self.user)
        self.assertEqual(usage.model, "gpt-4")

    def test_create_aiusage_without_user(self):
        """Test that AIUsage can not be created without  user."""

        with self.assertRaises(IntegrityError):
            AIUsage.objects.create(
                user=None,
                model="gpt-4",
                response_time=timezone.now(),
                response_content="Test response",
                response_tokens_used=42,
            )

    def test_user_delete_prevented_if_aiusage_exists(self):
        """Test that a user cannot be deleted if there is an AIUsage object."""
        usage = AIUsage.objects.create(
            user=self.user,
            model="gpt-4",
            response_time=timezone.now(),
            response_content="Test response",
            response_tokens_used=42,
        )
        with self.assertRaises(IntegrityError):
            self.user.delete()
        # Ensure the AIUsage instance still exists
        self.assertTrue(AIUsage.objects.filter(pk=usage.pk).exists())

    def test_model_longer_than_200_raises_error(self):
        """Test that model longer than 200 characters raises ValidationError."""
        usage = AIUsage(
            user=self.user,
            model="a" * 201,
            response_time=timezone.now(),
            response_content="Test response",
            response_tokens_used=42,
        )
        with self.assertRaises(ValidationError):
            usage.full_clean()


class TestBestelling(TestCase):
    """Unit tests for the Bestelling model."""

    def setUp(self):
        """Set up a user and a standaardLocatie for use in tests."""
        self.user = get_user_model().objects.create(username="testuser")
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=1)
        self.deelnemer = Deelnemer.objects.create(
            naam="Test Deelnemer", standaardLocatie=self.locatie
        )
        self.ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer,
            wijn=Wijn.objects.create(
                domein="DomeinTest",
                naam="WijnTest",
                wijnsoort=WijnSoort.objects.create(omschrijving="Rood"),
            ),
            datumOntvangst=timezone.now().date(),
        )

    def create_bestelling(
        self, deelnemer=None, van_locatie=None, datum_aangemaakt=None, opmerking=None
    ):
        """
        Helper to create a Bestelling with optional parameters.
        """

        bestelling = Bestelling()
        if deelnemer:
            bestelling.deelnemer = deelnemer
        else:
            bestelling.deelnemer = self.deelnemer

        if van_locatie:
            bestelling.vanLocatie = van_locatie
        else:
            bestelling.vanLocatie = self.locatie

        if datum_aangemaakt:
            bestelling.datumAangemaakt = datum_aangemaakt
        if opmerking:
            bestelling.opmerking = opmerking

        bestelling.save()
        return bestelling

    def create_bestellingregel(
        self,
        bestelling,
        ontvangst=None,
        vak=None,
        aantal=1,
        opmerking="",
        isVerzameld=False,
        aantal_correctie=None,
        verwerkt="N",
    ):
        """
        Helper to create a BestellingRegel with default values unless specified.
        """
        regel = BestellingRegel.objects.create(
            bestelling=bestelling,
            ontvangst=ontvangst,
            vak=vak,
            aantal=aantal,
            opmerking=opmerking,
            isVerzameld=isVerzameld,
            aantal_correctie=aantal_correctie,
            verwerkt=verwerkt,
        )
        regel.save()
        return regel

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
                bestelling, ontvangst=self.ontvangst, aantal=2, isVerzameld=True
            )
            self.create_bestellingregel(
                bestelling, ontvangst=self.ontvangst, aantal=4, isVerzameld=True
            )
            self.create_bestellingregel(
                bestelling, ontvangst=self.ontvangst, aantal=2, isVerzameld=False
            )
            self.create_bestellingregel(
                bestelling,
                ontvangst=self.ontvangst,
                aantal=4,
                isVerzameld=True,
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

        bestelling1 = self.create_bestelling(
            datum_aangemaakt=timezone.now().date() - datetime.timedelta(days=2)
        )
        bestelling2 = self.create_bestelling(
            datum_aangemaakt=timezone.now().date() - datetime.timedelta(days=1)
        )
        bestelling3 = self.create_bestelling(datum_aangemaakt=timezone.now().date())
        bestelling4 = self.create_bestelling(
            deelnemer=deelnemer_anders,
            datum_aangemaakt=timezone.now().date(),
        )
        bestelling5 = self.create_bestelling(
            van_locatie=locatie_elders,
            datum_aangemaakt=timezone.now().date(),
        )

        # Get all bestellingen and check the order
        bestellingen = list(Bestelling.objects.all())
        self.assertEqual(bestellingen[0], bestelling4)
        self.assertEqual(bestellingen[1], bestelling5)
        self.assertEqual(bestellingen[2], bestelling3)

        self.assertEqual(bestellingen[3], bestelling2)
        self.assertEqual(bestellingen[4], bestelling1)
