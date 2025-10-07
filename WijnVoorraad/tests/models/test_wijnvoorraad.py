from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError
from WijnVoorraad.models import (
    VoorraadMutatie,
    WijnSoort,
    WijnVoorraad,
    Wijn,
    Deelnemer,
    Ontvangst,
    Locatie,
    Vak,
)


class TestWijnVoorraad(TestCase):
    def setUp(self):
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=1)
        self.deelnemer = Deelnemer.objects.create(
            naam="Jan", standaardLocatie=self.locatie
        )
        self.wijnsoort = WijnSoort.objects.create(omschrijving="Rood")
        self.wijn = Wijn.objects.create(
            domein="DomeinX", naam="WijnX", wijnsoort=self.wijnsoort
        )
        self.ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer, wijn=self.wijn, datumOntvangst="2024-01-01"
        )
        self.vak = Vak.objects.create(locatie=self.locatie, code="A1", capaciteit=10)

    def test_delete_wijn_prevented_if_connected_to_wijnvoorraad(self):
        """Test that deleting a Wijn linked to WijnVoorraad raises an IntegrityError."""

        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        with self.assertRaises(ProtectedError):
            self.wijn.delete()

    def test_delete_deelnemer_prevented_if_connected_to_wijnvoorraad(self):
        """Test that deleting a Deelnemer linked to WijnVoorraad raises an IntegrityError."""
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        with self.assertRaises(ProtectedError):
            self.deelnemer.delete()

    def test_delete_ontvangst_prevented_if_connected_to_wijnvoorraad(self):
        """Test that deleting an Ontvangst linked to WijnVoorraad raises an IntegrityError."""
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        with self.assertRaises(ProtectedError):
            self.ontvangst.delete()

    def test_delete_locatie_prevented_if_connected_to_wijnvoorraad(self):
        """Test that deleting a Locatie linked to WijnVoorraad raises an IntegrityError."""
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        with self.assertRaises(ProtectedError):
            self.locatie.delete()

    def test_delete_vak_prevented_if_connected_to_wijnvoorraad(self):
        """Test that deleting a Vak linked to WijnVoorraad raises an IntegrityError."""
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        with self.assertRaises(ProtectedError):
            self.vak.delete()

    def test_str_with_vak(self):
        """Test the __str__ method of WijnVoorraad with vak."""
        wijnvoorraad = WijnVoorraad(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        expected = f"{self.wijn.volle_naam} - {self.deelnemer.naam} - {self.locatie.omschrijving} ({self.vak.code})"
        self.assertEqual(str(wijnvoorraad), expected)

    def test_str_without_vak(self):
        """Test the __str__ method of WijnVoorraad without vak."""

        wijnvoorraad = WijnVoorraad(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=None,
        )
        expected = f"{self.wijn.volle_naam} - {self.deelnemer.naam} - {self.locatie.omschrijving}"
        self.assertEqual(str(wijnvoorraad), expected)

    @patch("WijnVoorraad.models.VoorraadMutatie.drinken")
    def test_drinken_calls_voorraadmutatie_drinken(self, mock_drinken):
        """Test that the drinken method calls VoorraadMutatie.drinken."""
        wijnvoorraad = WijnVoorraad(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        wijnvoorraad.drinken()
        mock_drinken.assert_called_once_with(self.ontvangst, self.locatie, self.vak)

    def test_check_fuzzy_selectie_lazy_true_on_wijn(self):
        """Test that check_fuzzy_selectie returns True if wijn matches.
        and Ontvangst is not called.
        """
        # create a WijnVoorraad instance
        wijnvoorraad = WijnVoorraad(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        # setup mocks

        wijnvoorraad.wijn.check_fuzzy_selectie = MagicMock(return_value=True)
        wijnvoorraad.ontvangst.check_fuzzy_selectie = MagicMock()
        wijnvoorraad.wijn.check_fuzzy_selectie.return_value = True

        # Call the method under test
        result = wijnvoorraad.check_fuzzy_selectie("foo")
        self.assertTrue(result)
        wijnvoorraad.ontvangst.check_fuzzy_selectie.assert_not_called()

    def test_check_fuzzy_selectie_true_on_ontvangst(self):
        wijnvoorraad = WijnVoorraad(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        wijnvoorraad.wijn.check_fuzzy_selectie = MagicMock(return_value=False)
        wijnvoorraad.ontvangst.check_fuzzy_selectie = MagicMock(return_value=True)

        result = wijnvoorraad.check_fuzzy_selectie("foo")
        self.assertTrue(result)
        wijnvoorraad.ontvangst.check_fuzzy_selectie.assert_called_once_with("foo")

    def test_check_fuzzy_selectie_false_on_both(self):
        wijnvoorraad = WijnVoorraad(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        wijnvoorraad.wijn.check_fuzzy_selectie = MagicMock(return_value=False)
        wijnvoorraad.ontvangst.check_fuzzy_selectie = MagicMock(return_value=False)

        result = wijnvoorraad.check_fuzzy_selectie("foo")
        self.assertFalse(result)
        wijnvoorraad.ontvangst.check_fuzzy_selectie.assert_called_once_with("foo")

    def test_check_fuzzy_selectie_true_on_empty_param(self):
        wijnvoorraad = WijnVoorraad(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
        )
        result = wijnvoorraad.check_fuzzy_selectie("")
        self.assertTrue(result)


class TestWijnVoorraadBijwerken(TestCase):
    """Test the WijnVoorraad.Bijwerken method to ensure it calls the correct helper methods."""

    def setUp(self):
        # Only setup what is needed for Bijwerken tests
        self.mutatie_in = MagicMock()
        self.mutatie_in.in_uit = "I"
        self.mutatie_uit = MagicMock()
        self.mutatie_uit.in_uit = "U"

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_IN")
    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_UIT")
    def test_bijwerken_only_new_mutatie_in_calls_in(self, mock_uit, mock_in):
        """Bijwerken with only new_mutatie (in_uit='I') calls Bijwerken_mutatie_IN."""
        WijnVoorraad.Bijwerken(self.mutatie_in, None)
        mock_in.assert_called_once_with(self.mutatie_in)
        mock_uit.assert_not_called()

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_IN")
    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_UIT")
    def test_bijwerken_only_new_mutatie_uit_calls_uit(self, mock_uit, mock_in):
        """Bijwerken with only new_mutatie (in_uit='U') calls Bijwerken_mutatie_UIT."""
        WijnVoorraad.Bijwerken(self.mutatie_uit, None)
        mock_uit.assert_called_once_with(self.mutatie_uit)
        mock_in.assert_not_called()

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_IN")
    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_UIT")
    def test_bijwerken_only_old_mutatie_in_calls_uit(self, mock_uit, mock_in):
        """Bijwerken with only old_mutatie (in_uit='I') calls Bijwerken_mutatie_UIT."""
        WijnVoorraad.Bijwerken(None, self.mutatie_in)
        mock_uit.assert_called_once_with(self.mutatie_in)
        mock_in.assert_not_called()

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_IN")
    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_UIT")
    def test_bijwerken_only_old_mutatie_uit_calls_in(self, mock_uit, mock_in):
        """Bijwerken with only old_mutatie (in_uit='U') calls Bijwerken_mutatie_IN."""
        WijnVoorraad.Bijwerken(None, self.mutatie_uit)
        mock_in.assert_called_once_with(self.mutatie_uit)
        mock_uit.assert_not_called()

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_IN")
    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_UIT")
    def test_bijwerken_both_in_calls_in_and_uit(self, mock_uit, mock_in):
        """Bijwerken with both new and old (both in_uit='I') calls UIT for old, IN for new."""
        WijnVoorraad.Bijwerken(self.mutatie_in, self.mutatie_in)
        mock_uit.assert_called_once_with(self.mutatie_in)
        mock_in.assert_called_once_with(self.mutatie_in)

    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_IN")
    @patch("WijnVoorraad.models.WijnVoorraad.Bijwerken_mutatie_UIT")
    def test_bijwerken_both_uit_calls_in_and_uit(self, mock_uit, mock_in):
        """Bijwerken with both new and old (both in_uit='U') calls IN for old, UIT for new."""
        WijnVoorraad.Bijwerken(self.mutatie_uit, self.mutatie_uit)
        mock_in.assert_called_once_with(self.mutatie_uit)
        mock_uit.assert_called_once_with(self.mutatie_uit)


class TestWijnVoorraadMutatieMethods(TestCase):
    def setUp(self):
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=1)
        self.deelnemer = Deelnemer.objects.create(
            naam="Jan", standaardLocatie=self.locatie
        )
        self.wijnsoort = WijnSoort.objects.create(omschrijving="Rood")
        self.wijn = Wijn.objects.create(domein="DomeinX", naam="WijnX", wijnsoort_id=1)
        self.ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer, wijn=self.wijn, datumOntvangst="2024-01-01"
        )
        self.vak = Vak.objects.create(locatie=self.locatie, code="A1", capaciteit=10)

    @patch("WijnVoorraad.models.Wijn.check_afsluiten")
    def test_bijwerken_mutatie_in_updates_existing(self, mock_check_afsluiten):
        """IN: voorraad found, updated, check_afsluiten called."""
        # create existing WijnVoorraad
        vrd = WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
        )
        # create a mock mutatie
        mutatie = MagicMock()
        mutatie.ontvangst = self.ontvangst
        mutatie.locatie = self.locatie
        mutatie.vak = self.vak
        mutatie.aantal = 3
        mutatie.ontvangst.wijn = self.wijn
        mutatie.ontvangst.deelnemer = self.deelnemer

        WijnVoorraad.Bijwerken_mutatie_IN(mutatie)
        vrd.refresh_from_db()
        # voorraad should be updated
        self.assertEqual(vrd.aantal, 8)
        # check_afsluiten should be called
        mock_check_afsluiten.assert_called_once_with()

    @patch("WijnVoorraad.models.Wijn.check_afsluiten")
    def test_bijwerken_mutatie_in_creates_new(self, mock_check_afsluiten):
        """IN: voorraad not found, new record created, check_afsluiten called."""
        mutatie = MagicMock()
        mutatie.ontvangst = self.ontvangst
        mutatie.locatie = self.locatie
        mutatie.vak = self.vak
        mutatie.aantal = 4
        mutatie.ontvangst.wijn = self.wijn
        mutatie.ontvangst.deelnemer = self.deelnemer

        WijnVoorraad.Bijwerken_mutatie_IN(mutatie)
        vrd = WijnVoorraad.objects.get(
            ontvangst=self.ontvangst, locatie=self.locatie, vak=self.vak
        )
        self.assertEqual(vrd.aantal, 4)
        mock_check_afsluiten.assert_called_once_with()

    def test_bijwerken_mutatie_in_deletes_on_zero(self):
        """IN: voorraad updated to 0, record deleted"""
        vrd = WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=-2,
        )
        mutatie = MagicMock()
        mutatie.ontvangst = self.ontvangst
        mutatie.locatie = self.locatie
        mutatie.vak = self.vak
        mutatie.aantal = 2
        mutatie.ontvangst.wijn = self.wijn
        mutatie.ontvangst.deelnemer = self.deelnemer

        WijnVoorraad.Bijwerken_mutatie_IN(mutatie)
        self.assertFalse(WijnVoorraad.objects.filter(pk=vrd.pk).exists())

    # We do not need to check mock_check_afsluiten here, was already tested above

    @patch("WijnVoorraad.models.Wijn.check_afsluiten")
    def test_bijwerken_mutatie_uit_updates_existing(self, mock_check_afsluiten):
        """UIT: voorraad found, updated, check_afsluiten called."""
        vrd = WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=10,
        )
        mutatie = MagicMock()
        mutatie.ontvangst = self.ontvangst
        mutatie.locatie = self.locatie
        mutatie.vak = self.vak
        mutatie.aantal = 4
        mutatie.ontvangst.wijn = self.wijn
        mutatie.ontvangst.deelnemer = self.deelnemer

        WijnVoorraad.Bijwerken_mutatie_UIT(mutatie)
        vrd.refresh_from_db()
        self.assertEqual(vrd.aantal, 6)
        mock_check_afsluiten.assert_called_once_with()

    @patch("WijnVoorraad.models.Wijn.check_afsluiten")
    def test_bijwerken_mutatie_uit_creates_new(self, mock_check_afsluiten):
        """UIT: voorraad not found, new record created with negative aantal, check_afsluiten called."""
        mutatie = MagicMock()
        mutatie.ontvangst = self.ontvangst
        mutatie.locatie = self.locatie
        mutatie.vak = self.vak
        mutatie.aantal = 3
        mutatie.ontvangst.wijn = self.wijn
        mutatie.ontvangst.deelnemer = self.deelnemer

        WijnVoorraad.Bijwerken_mutatie_UIT(mutatie)
        vrd = WijnVoorraad.objects.get(
            ontvangst=self.ontvangst, locatie=self.locatie, vak=self.vak
        )
        self.assertEqual(vrd.aantal, -3)
        mock_check_afsluiten.assert_called_once_with()

    def test_bijwerken_mutatie_uit_deletes_on_zero(self):
        """UIT: voorraad updated to 0, record deleted."""
        vrd = WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=2,
        )
        mutatie = MagicMock()
        mutatie.ontvangst = self.ontvangst
        mutatie.locatie = self.locatie
        mutatie.vak = self.vak
        mutatie.aantal = 2
        mutatie.ontvangst.wijn = self.wijn
        mutatie.ontvangst.deelnemer = self.deelnemer

        WijnVoorraad.Bijwerken_mutatie_UIT(mutatie)
        self.assertFalse(WijnVoorraad.objects.filter(pk=vrd.pk).exists())
        # no need to check check_afsluiten here, was already tested above

    # given an existing mutation (old_mutation), type I with amount 4 and for the same location, vak and ontvangst
    # is stock level 8, check_voorraad_wijziging without mutation should give no warning

    def test_check_voorraad_wijziging_remove_i_enough_stock(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=8,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "I"
        old_mutatie.aantal = 4
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            WijnVoorraad.check_voorraad_wijziging(None, old_mutatie)

    # given an existing mutation (old_mutation), type I with amount 8 and for the same location, vak and ontvangst
    # is stock level 6, check_voorraad_wijziging without mutation should raise validationError
    def test_check_voorraad_wijziging_remove_i_not_enough_stock_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=6,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "I"
        old_mutatie.aantal = 8
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_wijziging(None, old_mutatie)

    # given an existing mutation (old_mutation), type U with amount 4 and for the same location, vak and ontvangst
    # is stock level 0, aka non existing, check_voorraad_wijziging without mutation should give no warning

    def test_check_voorraad_wijziging_remove_u_no_stock(self):

        old_mutatie = MagicMock()
        old_mutatie.in_uit = "U"
        old_mutatie.aantal = 4
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            WijnVoorraad.check_voorraad_wijziging(None, old_mutatie)

    # given an existing mutation (old_mutation), type U with amount 4 and for the same location, vak and ontvangst
    # is stock level 2, check_voorraad_wijziging without mutation should give no warning

    def test_check_voorraad_wijziging_remove_u_enough_stock(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=2,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "U"
        old_mutatie.aantal = 4
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            WijnVoorraad.check_voorraad_wijziging(None, old_mutatie)

    # given an existing mutation (old_mutation), type U with amount 2 and for the same location, vak and ontvangst
    # is stock level -3, should not be possible, check_voorraad_wijziging without mutation should raise ValidationError

    def test_check_voorraad_wijziging_remove_u_not_enough_stock_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=-3,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "U"
        old_mutatie.aantal = 2
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_wijziging(None, old_mutatie)

    # For a given location, vak and ontvangst the stock level is 8
    # Add a new mutation (mutation), type I with amount 4 and for the same location, vak and ontvangst
    # check_voorraad_wijziging with mutation should give no warning
    def test_check_voorraad_wijziging_add_i_enough_stock(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=8,
        )
        new_mutatie = MagicMock()
        new_mutatie.in_uit = "I"
        new_mutatie.aantal = 4
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            WijnVoorraad.check_voorraad_wijziging(new_mutatie, None)

    # For a given location, vak and ontvangst the stock level is -4 (hypothetical)
    # Add a new mutation (mutation), type I with amount 2 and for the same location, vak and ontvangst
    # check_voorraad_wijziging with mutation should validationError
    def test_check_voorraad_wijziging_add_i_not_enough_stock_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=-4,
        )
        new_mutatie = MagicMock()
        new_mutatie.in_uit = "I"
        new_mutatie.aantal = 2
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_wijziging(new_mutatie, None)

    # For a given location, vak and ontvangst the stock level is 4
    # Add a new mutation (mutation), type U with amount 8 and for the same location, vak and ontvangst
    # check_voorraad_wijziging with mutation should validationError
    def test_check_voorraad_wijziging_add_u_not_enough_stock_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=4,
        )
        new_mutatie = MagicMock()
        new_mutatie.in_uit = "U"
        new_mutatie.aantal = 8
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_wijziging(new_mutatie, None)

    # For a given location, vak and ontvangst the stock level is 8
    # Add a new mutation (mutation), type U with amount 8 and for the same location, vak and ontvangst
    # check_voorraad_wijziging with mutation should give no warning
    def test_check_voorraad_wijziging_add_u_exact_enough_stock_raises_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=8,
        )
        new_mutatie = MagicMock()
        new_mutatie.in_uit = "U"
        new_mutatie.aantal = 8
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            WijnVoorraad.check_voorraad_wijziging(new_mutatie, None)

    # For a given location, vak and ontvangst the stock level is 8
    # there is an existing mutation (old_mutation), type I with amount 4 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but change vak to another vak
    # check_voorraad_wijziging should no error because the stock level for the old vak will be 4 after removing the old mutation
    # and for the new vak it will be 4 after adding the new mutation assuming there was no stock before
    def test_check_voorraad_wijziging_change_vak_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=8,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "I"
        old_mutatie.aantal = 4
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_vak = Vak.objects.create(locatie=self.locatie, code="B1", capaciteit=10)
        new_mutatie = MagicMock()
        new_mutatie.in_uit = "I"
        new_mutatie.aantal = 4
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = new_vak
        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)

    # For a given location, vak and ontvangst the stock level is 3
    # there is an existing mutation (old_mutation), type I with amount 4 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but change vak to another vak
    # check_voorraad_wijziging should raise validation error because the stock level for the old vak will be negative after removing the old mutation
    def test_check_voorraad_wijziging_change_vak_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=3,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "I"
        old_mutatie.aantal = 4
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_vak = Vak.objects.create(locatie=self.locatie, code="B1", capaciteit=10)
        new_mutatie = MagicMock()
        new_mutatie.in_uit = "I"
        new_mutatie.aantal = 4
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = new_vak
        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=False,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)

    # For a given location, vak and ontvangst the stock level is 4
    # there is an existing mutation (old_mutation), type I with amount 5 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but with amount 3
    # check_voorraad_wijziging should raise no error because the stock level will be 2 after removing the old mutation and adding the new one
    def test_check_voorraad_wijziging_less_amount_with_enough_stock(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=4,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "I"
        old_mutatie.aantal = 5
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_mutatie = MagicMock()
        new_mutatie.in_uit = "I"
        new_mutatie.aantal = 3
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)

    # For a given location, vak and ontvangst the stock level is 5
    # there is an existing mutation (old_mutation), type I with amount 3 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but with amount 5
    # check_voorraad_wijziging should not error because the stock level will be 7 after removing the old mutation and adding the new one
    def test_check_voorraad_wijziging_change_amount_add_more(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "I"
        old_mutatie.aantal = 3
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_mutatie = MagicMock()
        new_mutatie.in_uit = "I"
        new_mutatie.aantal = 5
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)

    # For a given location, vak and ontvangst the stock level is 2
    # there is an existing mutation (old_mutation), type U with amount 3 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but with amount 5
    # check_voorraad_wijziging should raise no error because the stock level will be 0 after removing the old mutation and adding the new one
    def test_check_voorraad_wijziging_change_amount_remove_more(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=2,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "U"
        old_mutatie.aantal = 3
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_mutatie = MagicMock()
        new_mutatie.in_uit = "U"
        new_mutatie.aantal = 5
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)

    # For a given location, vak and ontvangst the stock level is 1
    # there is an existing mutation (old_mutation), type U with amount 3 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but with amount 5
    # check_voorraad_wijziging should raise error because the stock level will be -1 after removing the old mutation and adding the new one
    def test_check_voorraad_wijziging_change_amount_remove_too_much_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=1,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "U"
        old_mutatie.aantal = 3
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_mutatie = MagicMock()
        new_mutatie.in_uit = "U"
        new_mutatie.aantal = 5
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)

    # For a given location, vak and ontvangst the stock level is 0
    # there is an existing mutation (old_mutation), type U with amount 5 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but with amount 3
    # check_voorraad_wijziging should raise no error because the stock level will be 2 after removing the old mutation and adding the new one
    def test_check_voorraad_wijziging_change_amount_add_enough(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=0,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "U"
        old_mutatie.aantal = 5
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_mutatie = MagicMock()
        new_mutatie.in_uit = "U"
        new_mutatie.aantal = 3
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)

    # For a given location, vak and ontvangst the stock level is 5
    # there is an existing mutation (old_mutation), type I with amount 4 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but with amount 4 and type U
    # check_voorraad_wijziging should raise error because the stock level will be -3 after removing the old mutation and adding the new one
    def test_check_voorraad_wijziging_in_to_out_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "I"
        old_mutatie.aantal = 4
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_mutatie = MagicMock()
        new_mutatie.in_uit = "U"
        new_mutatie.aantal = 4
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)

    # For a given location, vak and ontvangst the stock level is -2
    # there is an existing mutation (old_mutation), type U with amount 7 and for the same location, vak and ontvangst
    # add a new mutation (mutation), based on the old one, but with amount 4 and type I
    # check_voorraad_wijziging should not raise error because the stock level will be +9 after removing the old mutation and adding the new one
    def test_check_voorraad_wijziging_out_to_in_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=-2,
        )
        old_mutatie = MagicMock()
        old_mutatie.in_uit = "U"
        old_mutatie.aantal = 7
        old_mutatie.ontvangst = self.ontvangst
        old_mutatie.locatie = self.locatie
        old_mutatie.vak = self.vak

        new_mutatie = MagicMock()
        new_mutatie.in_uit = "I"
        new_mutatie.aantal = 4
        new_mutatie.ontvangst = self.ontvangst
        new_mutatie.locatie = self.locatie
        new_mutatie.vak = self.vak

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            WijnVoorraad.check_voorraad_wijziging(new_mutatie, old_mutatie)
