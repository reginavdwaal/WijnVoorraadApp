# pylint: disable=no-member
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model

# Import the models to be tested
from WijnVoorraad.models import Deelnemer, DruivenSoort, WijnSoort, Vak, Locatie


# Create your tests here.
class testWijnSoort(TestCase):
    # def setUp(self) :
    #     defaultProcedure = Procedure.objects.create(title="procedure one", step=1)
    #     CheckItem.objects.create(item="item one", procedure = defaultProcedure , step=3)
    # #    CheckItem.objects.create(item="item two", procedure = defaultProcedure , step=1)
    #     CheckItem.objects.create(item="item three", procedure = defaultProcedure , step=5)

    def test_WijnSoortNotLongerThen200(self):
        with self.assertRaises(ValidationError) as exc:
            wijnsoort = WijnSoort.objects.create(omschrijving="abc" * 100)
            wijnsoort.full_clean()
        self.assertIn("200", str(exc.exception))

    def test_WijnSoort200ShouldFit(self):
        wijnsoort = WijnSoort.objects.create(omschrijving="ab" * 100)
        wijnsoort.full_clean()
        self.assertEqual(len(wijnsoort.omschrijving), 200)

    def test_WijnAsStrShouldReturnOmschrijving(self):
        wijnsoort = WijnSoort.objects.create(omschrijving="Precies Dit")
        self.assertEqual(str(wijnsoort), "Precies Dit")

    def test_WijnSoort_order(self):
        WijnSoort.objects.create(omschrijving="B.Rood")
        WijnSoort.objects.create(omschrijving="A.Rood")
        WijnSoort.objects.create(omschrijving="C.Rood")

        # check if the order is correct
        self.assertEqual(
            list(WijnSoort.objects.all().order_by("omschrijving")),
            list(WijnSoort.objects.all()),
        )


class testDruivenSoort(TestCase):
    # def setUp(self) :
    #     defaultProcedure = Procedure.objects.create(title="procedure one", step=1)
    #     CheckItem.objects.create(item="item one", procedure = defaultProcedure , step=3)
    # #    CheckItem.objects.create(item="item two", procedure = defaultProcedure , step=1)
    #     CheckItem.objects.create(item="item three", procedure = defaultProcedure , step=5)

    def test_DruivenSoortNotLongerThen200(self):
        with self.assertRaises(ValidationError) as exc:
            druivensoort = DruivenSoort.objects.create(omschrijving="abc" * 100)
            druivensoort.full_clean()
        self.assertIn("200", str(exc.exception))

    def test_WijnSoort200ShouldFit(self):
        druivensoort = DruivenSoort.objects.create(omschrijving="ab" * 100)
        druivensoort.full_clean()
        self.assertEqual(len(druivensoort.omschrijving), 200)

    def test_WijnAsStrShouldReturnOmschrijving(self):
        druivensoort = DruivenSoort.objects.create(omschrijving="Precies Dit")
        self.assertEqual(str(druivensoort), "Precies Dit")


class testVak(TestCase):
    def setUp(self):
        self.locatie = Locatie.objects.create(omschrijving="Kelder", aantal_kolommen=2)

    def test_create_vak(self):
        vak = Vak.objects.create(locatie=self.locatie, code="A1", capaciteit=10)
        self.assertEqual(vak.locatie, self.locatie)
        self.assertEqual(vak.code, "A1")
        self.assertEqual(vak.capaciteit, 10)

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


class testDeelnemer(TestCase):
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
        self.assertIn(self.user, deelnemer.users.all())

    def test_ordering(self):
        Deelnemer.objects.create(naam="Bert")
        Deelnemer.objects.create(naam="Anna")
        Deelnemer.objects.create(naam="Chris")
        namen = list(Deelnemer.objects.values_list("naam", flat=True))
        self.assertEqual(namen, sorted(namen))
