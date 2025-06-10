from django.test import TestCase
from django.core.exceptions import ValidationError

from WijnVoorraad.models import DruivenSoort


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
