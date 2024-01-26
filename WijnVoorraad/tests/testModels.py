# pylint: disable=no-member
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
from django.core.exceptions import ValidationError
from django.test import TestCase

from WijnVoorraad.models import DruivenSoort, WijnSoort


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

        for wijnsoort in WijnSoort.objects.all().first:
            print(wijnsoort)


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
