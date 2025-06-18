"""Unit test for class VoorraadMutatie"""

from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone

from django.db import IntegrityError
from django.core.exceptions import ValidationError

from WijnVoorraad.models import VoorraadMutatie
from WijnVoorraad.tests.models.model_helper import SharedTestDataMixin


class TestVoorraadMutatie(SharedTestDataMixin, TestCase):
    """Unit tests for the VoorraadMutatie model."""

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

    def test_locatie_can_not_be_deleted_if_linked_to_voorraad_mutatie(self):
        """Test that a Locatie cannot be deleted if it has related VoorraadMutatie instances."""
        # Create a VoorraadMutatie linked to the Locatie
        VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        with self.assertRaises(IntegrityError):
            self.locatie.delete()

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

    def test_clean_should_call_wijnvoorraad_check_voorraad_wijziging(self):
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

    def test_save_should_call_wijnvoorraad_bijwerken(self):
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

    def test_save_should_call_wijnvoorraad_bijwerken_with_old_mutatie(self):
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

    def test_delete_should_call_wijnvoorraad_bijwerken(self):
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

    def test_drinken_should_copy_vak_from_call(self):
        """Test that drinken copies the vak from the call."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
            vak=self.vak_a1,
        )
        with patch("WijnVoorraad.models.WijnVoorraad.Bijwerken"):
            voorraad_mutatie.drinken(self.ontvangst, self.locatie, self.vak_a1)
            # Check that a new VoorraadMutatie was created
            new_mutatie = VoorraadMutatie.objects.last()
            self.assertEqual(new_mutatie.vak, self.vak_a1)

    def test_voorraad_plus_1_should_create_and_save_i_mutatie_with_action_k_now_aantal_1(
        self,
    ):
        """Test that voorraad_plus_1 creates an 'I' mutatie with action 'K',
        date now, and aantal 1."""
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

    def test_afboeken_should_copy_vak_from_call(self):
        """Test that afboeken copies the vak from the call."""

        with (
            patch("WijnVoorraad.models.WijnVoorraad.Bijwerken"),
            patch(
                "WijnVoorraad.models.WijnVoorraad.check_voorraad_wijziging",
                return_value=None,
            ),
        ):
            VoorraadMutatie.afboeken(
                self.ontvangst, self.locatie, aantal=1, vak=self.vak_a1
            )
            # Check that a new VoorraadMutatie was created
            new_mutatie = VoorraadMutatie.objects.last()
            self.assertEqual(new_mutatie.vak, self.vak_a1)

    def test_check_fuzzy_selectie_should_return_true_if_fuzzy_selectie_matches_omschrijving(
        self,
    ):
        # Test that check_fuzzy_selectie returns True
        # if fuzzy_selectie matches omschrijving or ontvangst.
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
            omschrijving="Test omschrijving",
        )
        self.assertTrue(voorraad_mutatie.check_fuzzy_selectie("Test"))
        self.assertTrue(voorraad_mutatie.check_fuzzy_selectie("omschrijving"))
        self.assertTrue(voorraad_mutatie.check_fuzzy_selectie("Test omschrijving"))

    def test_check_fuzzy_selectie_should_call_ontvangst_check_fuzzy_selectie(
        self,
    ):
        """Test that check_fuzzy_selectie calls ontvangst.check_fuzzy_selectie."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
        )
        with patch.object(
            voorraad_mutatie.ontvangst, "check_fuzzy_selectie", return_value=True
        ) as mock_check:
            voorraad_mutatie.check_fuzzy_selectie("Test")
            mock_check.assert_called_once_with("Test")

    def test_check_fuzzy_selectie_should_not_call_ontvangst_check_if_match_on_mutatie(
        self,
    ):
        # Test that check_fuzzy_selectie does not call ontvangst.check_fuzzy_selectie
        # if match on mutatie."""
        voorraad_mutatie = VoorraadMutatie.objects.create(
            ontvangst=self.ontvangst,
            aantal=10,
            actie="toevoegen",
            datum=timezone.now().date(),
            locatie=self.locatie,
            omschrijving="Test omschrijving",
        )
        with patch.object(
            voorraad_mutatie.ontvangst, "check_fuzzy_selectie"
        ) as mock_check:
            voorraad_mutatie.check_fuzzy_selectie("Test omschrijving")
            mock_check.assert_not_called()
