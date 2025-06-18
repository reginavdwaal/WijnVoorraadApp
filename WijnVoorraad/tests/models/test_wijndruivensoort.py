"""
Unit tests for the WijnDruivensoort model.
"""

from django.db.utils import IntegrityError
from django.test import TestCase

from WijnVoorraad.models import WijnDruivensoort
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


class TestWijnDruivensoort(SharedTestDataMixin, TestCase):
    """Unit tests for the WijnDruivensoort model.
    This class tests the creation, string representation, unique constraints,
    and ordering of WijnDruivensoort instances.
    """

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
