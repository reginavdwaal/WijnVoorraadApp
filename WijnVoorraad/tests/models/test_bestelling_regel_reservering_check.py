"""Test class for WijnVoorraad.check_voorraad_rsv method.
This is effectively testing the reservation check logic when creating, updating or
deleting order lines (BestellingRegel)."""

from unittest.mock import MagicMock, patch
from django.core.exceptions import ValidationError
from django.test import TestCase

from WijnVoorraad.models import (
    Deelnemer,
    Locatie,
    Ontvangst,
    Vak,
    VoorraadMutatie,
    Wijn,
    WijnSoort,
    WijnVoorraad,
)


class TestWijnVoorraadRSV(TestCase):
    """Tests for WijnVoorraad.check_voorraad_rsv method."""

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

    def test_check_voorraad_rsv_too_much_reserved_raises_error(self):
        """If reserved amount exceeds stock, should raise ValidationError."""

        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        order_line = MagicMock()
        order_line.ontvangst = self.ontvangst
        order_line.bestelling = bestelling
        order_line.vak = self.vak
        order_line.aantal = 3
        order_line.aantal_correctie = None
        order_line.aantal_werkelijk = 3
        with self.assertRaises(ValidationError):
            WijnVoorraad.check_voorraad_rsv(order_line, None)

    def test_check_voorraad_rsv_enough_reserved_no_error(self):
        """If reserved amount does not exceed stock, should not raise."""
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        order_line = MagicMock()
        order_line.ontvangst = self.ontvangst
        order_line.bestelling = bestelling
        order_line.vak = self.vak
        order_line.aantal = 2
        order_line.aantal_correctie = None
        order_line.aantal_werkelijk = 2
        # Should not raise
        WijnVoorraad.check_voorraad_rsv(order_line, None)

    def test_check_voorraad_rsv_wrong_vak_raises_error(self):
        """If vak does not match, should raise error (no stock)."""
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        other_vak = Vak.objects.create(locatie=self.locatie, code="B1", capaciteit=10)
        order_line = MagicMock()
        order_line.ontvangst = self.ontvangst
        order_line.bestelling = bestelling
        order_line.vak = other_vak
        order_line.aantal = 1
        order_line.aantal_correctie = None
        order_line.aantal_werkelijk = 1
        with self.assertRaises(ValidationError):
            WijnVoorraad.check_voorraad_rsv(order_line, None)

    # given stock level 5 and reserved 3
    # given an existing order line (old_order_line) with amount 5 for the same  location,
    # vak and ontvangst
    # deleting this order line should not raise error while checking the voorraad_rsv
    # practically this means there is only an old order line with amount 5
    def test_check_voorraad_rsv_remove_order_line_to_much_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 5
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 5

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            # should not raise error
            WijnVoorraad.check_voorraad_rsv(None, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old_order_line) with amount 3 for the same  location,
    # vak and ontvangst
    # deleting this order line should not raise error while checking the voorraad_rsv
    # practically this means there is only an old order line with amount 3

    def test_check_voorraad_rsv_remove_order_line_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 5
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 5

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            # should not raise error
            WijnVoorraad.check_voorraad_rsv(None, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old_order_line) with amount 3 for the same  location,
    # vak and ontvangst
    # order line state is not N
    # deleting this order line should not raise error while checking the voorraad_rsv

    def test_check_voorraad_rsv_remove_not_processed_order_line_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 5
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 5
        old_order_line.verwerkt = "A"  # not N
        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            # should not raise error
            WijnVoorraad.check_voorraad_rsv(None, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old) with amount 2 for the same  location, vak and ontvangst
    # add a new order line (order_line), based on the old one, but with amount 1
    # both order lines have verwerkt state N
    # check_voorraad_rsv should raise no error
    def test_check_voorraad_rsv_change_amount_less_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 2
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 2
        old_order_line.verwerkt = "N"

        new_order_line = MagicMock()
        new_order_line.ontvangst = self.ontvangst
        new_order_line.bestelling = bestelling
        new_order_line.vak = self.vak
        new_order_line.aantal = 1
        new_order_line.aantal_correctie = None
        new_order_line.aantal_werkelijk = 1
        new_order_line.verwerkt = "N"

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            WijnVoorraad.check_voorraad_rsv(new_order_line, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old) with amount 2 for the same  location, vak and ontvangst
    # add a new order line (order_line), based on the old one, but with amount 5
    # both order lines have verwerkt state N
    # check_voorraad_rsv should raise validation error
    def test_check_voorraad_rsv_change_amount_more_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 2
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 2
        old_order_line.verwerkt = "N"

        new_order_line = MagicMock()
        new_order_line.ontvangst = self.ontvangst
        new_order_line.bestelling = bestelling
        new_order_line.vak = self.vak
        new_order_line.aantal = 5
        new_order_line.aantal_correctie = None
        new_order_line.aantal_werkelijk = 5
        new_order_line.verwerkt = "N"

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_rsv(new_order_line, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old) with amount 2 for the same  location, vak and ontvangst
    # add a new order line (order_line), based on the old one, but with amount 5
    # both order lines have verwerkt state A (afgeboekt)
    # check_voorraad_rsv should not raise error (but mutation will fail later on
    def test_check_voorraad_rsv_change_amount_more_afgeboekt_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 2
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 2
        old_order_line.verwerkt = "A"

        new_order_line = MagicMock()
        new_order_line.ontvangst = self.ontvangst
        new_order_line.bestelling = bestelling
        new_order_line.vak = self.vak
        new_order_line.aantal = 5
        new_order_line.aantal_correctie = None
        new_order_line.aantal_werkelijk = 5
        new_order_line.verwerkt = "A"

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            WijnVoorraad.check_voorraad_rsv(new_order_line, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old) with amount 2 for the same  location, vak and ontvangst
    # and verwerkt state N
    # add a new order line (order_line), based on the old one, but with amount 1
    # and verwerkt state A
    # check_voorraad_rsv should not raise error as we are actually taking less stock
    def test_check_voorraad_rsv_change_amount_less_afgeboekt_no_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 2
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 2
        old_order_line.verwerkt = "N"

        new_order_line = MagicMock()
        new_order_line.ontvangst = self.ontvangst
        new_order_line.bestelling = bestelling
        new_order_line.vak = self.vak
        new_order_line.aantal = 1
        new_order_line.aantal_correctie = None
        new_order_line.aantal_werkelijk = 1
        new_order_line.verwerkt = "A"

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            WijnVoorraad.check_voorraad_rsv(new_order_line, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old) with amount 2 for the same  location, vak and ontvangst
    # and verwerkt state N
    # add a new order line (order_line), based on the old one, but with amount 5
    # and verwerkt state A
    # check_voorraad_rsv should raise error as the delta is 3, with only 2 stock left
    def test_check_voorraad_rsv_change_amount_more_afgeboekt_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 2
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 2
        old_order_line.verwerkt = "N"

        new_order_line = MagicMock()
        new_order_line.ontvangst = self.ontvangst
        new_order_line.bestelling = bestelling
        new_order_line.vak = self.vak
        new_order_line.aantal = 5
        new_order_line.aantal_correctie = None
        new_order_line.aantal_werkelijk = 5
        new_order_line.verwerkt = "A"

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_rsv(new_order_line, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old) with amount 2 for the same  location, vak and ontvangst
    # and verwerkt state A
    # add a new order line (order_line), based on the old one, but with verwerkt state N
    # check_voorraad_rsv should raise error as we are actually taking less stock
    def test_check_voorraad_rsv_change_afgeboekt_to_new_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 2
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 2
        old_order_line.verwerkt = "A"

        new_order_line = MagicMock()
        new_order_line.ontvangst = self.ontvangst
        new_order_line.bestelling = bestelling
        new_order_line.vak = self.vak
        new_order_line.aantal = 2
        new_order_line.aantal_correctie = None
        new_order_line.aantal_werkelijk = 2
        new_order_line.verwerkt = "N"

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_rsv(new_order_line, old_order_line)

    # given stock level 5 and reserved 3
    # given an existing order line (old) with amount 2 for the same  location, vak and ontvangst
    # and verwerkt state V
    # add a new order line (order_line), based on the old one, but with verwerkt state N
    # check_voorraad_rsv should raise error as we are actually taking less stock
    def test_check_voorraad_rsv_change_verwerkt_to_new_raises_error(self):
        WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=5,
            aantal_rsv=3,
        )
        bestelling = MagicMock()
        bestelling.vanLocatie = self.locatie
        old_order_line = MagicMock()
        old_order_line.ontvangst = self.ontvangst
        old_order_line.bestelling = bestelling
        old_order_line.vak = self.vak
        old_order_line.aantal = 2
        old_order_line.aantal_correctie = None
        old_order_line.aantal_werkelijk = 2
        old_order_line.verwerkt = "V"

        new_order_line = MagicMock()
        new_order_line.ontvangst = self.ontvangst
        new_order_line.bestelling = bestelling
        new_order_line.vak = self.vak
        new_order_line.aantal = 2
        new_order_line.aantal_correctie = None
        new_order_line.aantal_werkelijk = 2
        new_order_line.verwerkt = "N"

        with patch.object(
            VoorraadMutatie,
            "mutation_refer_to_same_voorraad",
            return_value=True,
        ):
            with self.assertRaises(ValidationError):
                WijnVoorraad.check_voorraad_rsv(new_order_line, old_order_line)
