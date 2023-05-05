from django.core.exceptions import ValidationError
from django.test import TestCase

from WijnVoorraad.models import Wijn, WijnSoort


# Create your tests here.
class testWijnSoort(TestCase):
    # def setUp(self) :
    #     defaultProcedure = Procedure.objects.create(title="procedure one", step=1)
    #     CheckItem.objects.create(item="item one", procedure = defaultProcedure , step=3)
    # #    CheckItem.objects.create(item="item two", procedure = defaultProcedure , step=1)
    #     CheckItem.objects.create(item="item three", procedure = defaultProcedure , step=5)

    def test_WijnNotLongerThen200(self):
        with self.assertRaises(ValidationError) as exc:
            wijnsoort = WijnSoort.objects.create(omschrijving="abc" * 100)
            wijnsoort.full_clean()
        self.assertIn("200", str(exc.exception))

    def test_Wijn200ShouldFit(self):
        wijnsoort = WijnSoort.objects.create(omschrijving="ab" * 100)
        wijnsoort.full_clean()
        self.assertEqual(len(wijnsoort.omschrijving), 200)
