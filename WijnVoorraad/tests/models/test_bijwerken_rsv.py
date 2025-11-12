"""Tests for WijnVoorraad reservation updates triggered by BestellingRegel changes."""

from django.test import TestCase
from django.core.exceptions import ValidationError

from WijnVoorraad.models import (
    Bestelling,
    BestellingRegel,
    Deelnemer,
    Locatie,
    Ontvangst,
    Vak,
    Wijn,
    WijnVoorraad,
    WijnSoort,
)


class TestBijwerkenRsvMethods(TestCase):
    """TestCase verifying bijwerken_rsv_erbij and bijwerken_rsv_eraf behaviour and validation
    when voorraad is missing."""

    def setUp(self):
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=1)
        self.deelnemer = Deelnemer.objects.create(
            naam="Jan", standaardLocatie=self.locatie
        )
        self.wijnssoort = WijnSoort.objects.create(omschrijving="Rood", id=1)
        self.wijn = Wijn.objects.create(domein="DomeinX", naam="WijnX", wijnsoort_id=1)
        self.ontvangst = Ontvangst.objects.create(
            deelnemer=self.deelnemer, wijn=self.wijn, datumOntvangst="2024-01-01"
        )
        self.vak = Vak.objects.create(locatie=self.locatie, code="A1", capaciteit=10)
        self.bestelling = Bestelling.objects.create(
            deelnemer=self.deelnemer, vanLocatie=self.locatie
        )

    def test_bijwerken_rsv_erbij_updates_reservering_when_voorraad_exists(self):
        """Bijwerken_rsv_erbij should increase aantal_rsv when voorraad record exists."""
        vrd = WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=10,
            aantal_rsv=2,
        )
        BestellingRegel.objects.create(
            bestelling=self.bestelling,
            ontvangst=self.ontvangst,
            vak=self.vak,
            aantal=3,
        )
        # save calles Bijwerken_rsv_erbij

        vrd.refresh_from_db()
        self.assertEqual(vrd.aantal_rsv, 5)

    def test_bijwerken_rsv_eraf_updates_reservering_when_voorraad_exists(self):
        """Bijwerken_rsv_eraf should decrease aantal_rsv when voorraad record exists."""
        vrd = WijnVoorraad.objects.create(
            wijn=self.wijn,
            deelnemer=self.deelnemer,
            ontvangst=self.ontvangst,
            locatie=self.locatie,
            vak=self.vak,
            aantal=10,
            aantal_rsv=5,
        )
        regel = BestellingRegel.objects.create(
            bestelling=self.bestelling,
            ontvangst=self.ontvangst,
            vak=self.vak,
            aantal=2,
        )

        vrd.refresh_from_db()
        self.assertEqual(vrd.aantal_rsv, 7)
        regel.delete()  # this calls Bijwerken_rsv_eraf
        vrd.refresh_from_db()
        self.assertEqual(vrd.aantal_rsv, 5)

    def test_bijwerken_rsv_erbij_raises_when_no_voorraad_and_positive_amount(self):
        """Bijwerken_rsv_erbij should raise ValidationError when no voorraad exists
        and amount > 0."""
        # ensure no WijnVoorraad exists for this combinatie
        WijnVoorraad.objects.filter(
            ontvangst=self.ontvangst, locatie=self.locatie, vak=self.vak
        ).delete()

        with self.assertRaises(ValidationError):
            BestellingRegel.objects.create(
                bestelling=self.bestelling,
                ontvangst=self.ontvangst,
                vak=self.vak,
                aantal=2,
            )
