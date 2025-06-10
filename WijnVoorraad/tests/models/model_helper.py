"""
Shared test data and helper functions for WijnVoorraad model tests.

Provides a mixin with reusable setup and creation methods for test cases.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from WijnVoorraad.models import (
    Bestelling,
    BestellingRegel,
    Locatie,
    Deelnemer,
    Vak,
    WijnSoort,
    DruivenSoort,
    Wijn,
    Ontvangst,
)


class SharedTestDataMixin:
    """
    Mixin to provide shared test data for models in the WijnVoorraad application.
    This mixin sets up common test data that can be used across multiple test cases.
    """

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        cls.user = get_user_model().objects.create(username="testuser")
        cls.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=3)
        cls.deelnemer = Deelnemer.objects.create(
            naam="Jan", standaardLocatie=cls.locatie
        )
        cls.wijnsoort = WijnSoort.objects.create(omschrijving="Rood")
        cls.druif1 = DruivenSoort.objects.create(omschrijving="Merlot")
        cls.druif = cls.druif1
        cls.druif2 = DruivenSoort.objects.create(omschrijving="Cabernet Sauvignon")
        cls.wijn = Wijn.objects.create(
            domein="DomeinX", naam="WijnX", wijnsoort=cls.wijnsoort
        )
        cls.vak_a1 = Vak.objects.create(locatie=cls.locatie, code="A1", capaciteit=5)
        cls.vak_a2 = Vak.objects.create(locatie=cls.locatie, code="A2", capaciteit=10)

        cls.ontvangst = Ontvangst.objects.create(
            deelnemer=cls.deelnemer,
            wijn=cls.wijn,
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
        is_verzameld=False,
        aantal_correctie=None,
        verwerkt="N",
    ):
        """
        Helper to create a BestellingRegel with default values unless specified.
        """
        if not ontvangst:
            ontvangst = self.ontvangst

        regel = BestellingRegel.objects.create(
            bestelling=bestelling,
            ontvangst=ontvangst,
            vak=vak,
            aantal=aantal,
            opmerking=opmerking,
            isVerzameld=is_verzameld,
            aantal_correctie=aantal_correctie,
            verwerkt=verwerkt,
        )
        regel.save()
        return regel
