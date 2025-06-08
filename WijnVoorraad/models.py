# pylint: disable=no-member

from datetime import date, datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Deferrable, F, Sum
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django_group_by import GroupByMixin


# Create your models here.


class WijnSoort(models.Model):
    css_choices = [
        ("wijnsoort_rood", "wijnsoort_rood"),
        ("wijnsoort_wit", "wijnsoort_wit"),
        ("wijnsoort_rose", "wijnsoort_rose"),
        ("wijnsoort_mousserend", "wijnsoort_mousserend"),
        ("wijnsoort_rodeport", "wijnsoort_rodeport"),
        ("wijnsoort_witteport", "wijnsoort_witteport"),
    ]
    omschrijving = models.CharField(max_length=200, unique=True)
    omschrijving_engels_ai = models.CharField(max_length=200, blank=True)
    style_css_class = models.CharField(max_length=100, blank=True, choices=css_choices)

    def __str__(self):
        return f"{self.omschrijving}"

    class Meta:
        ordering = ["omschrijving"]
        verbose_name = "wijnsoort"
        verbose_name_plural = "wijnsoorten"


class DruivenSoort(models.Model):
    omschrijving = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.omschrijving}"

    class Meta:
        ordering = ["omschrijving"]
        verbose_name = "druivensoort"
        verbose_name_plural = "druivensoorten"


class Locatie(models.Model):
    omschrijving = models.CharField(max_length=200, unique=True)
    aantal_kolommen = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.omschrijving}"

    class Meta:
        ordering = ["omschrijving"]


class Vak(models.Model):
    locatie = models.ForeignKey(Locatie, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    capaciteit = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.locatie.omschrijving} ({self.code})"

    class Meta:
        ordering = ["locatie", "code"]
        verbose_name_plural = "vakken"
        constraints = [
            models.UniqueConstraint(
                name="unique_code_binnen_locatie",
                fields=["locatie", "code"],
            )
        ]


class Deelnemer(models.Model):
    naam = models.CharField(max_length=200, unique=True)
    standaardLocatie = models.ForeignKey(
        Locatie, on_delete=models.SET_NULL, blank=True, null=True
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="deelnemers",
        related_query_name="deelnemer",
    )

    def __str__(self):
        return f"{self.naam}"

    class Meta:
        ordering = ["naam"]


class Wijn(models.Model):

    def validate_jaartal(jaartal):  # pylint: disable=no-self-argument
        # Validator to ensure the year is between 1901 and 2499.
        if not (1900 < jaartal < 2500):
            raise ValidationError(
                (
                    "%(jaartal)s is geen geldig jaartal. Het jaartal moet liggen tussen 1901 en 2499"
                ),
                params={"jaartal": jaartal},
            )

    domein = models.CharField(max_length=200)
    naam = models.CharField(max_length=200)
    wijnsoort = models.ForeignKey(WijnSoort, on_delete=models.PROTECT)

    jaar = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_jaartal]
    )
    land = models.CharField(max_length=200, blank=True)
    streek = models.CharField(max_length=200, blank=True)
    classificatie = models.CharField(max_length=200, blank=True)
    website = models.URLField(max_length=200, blank=True)
    opmerking = models.CharField(max_length=4000, blank=True)
    foto = models.ImageField(upload_to="images/", null=True, blank=True)
    datumAangemaakt = models.DateTimeField(auto_now_add=True)
    datumAfgesloten = models.DateTimeField(null=True, blank=True)

    wijnDruivensoorten = models.ManyToManyField(
        DruivenSoort,
        through="WijnDruivensoort",
        through_fields=("wijn", "druivensoort"),
        null=True,
        blank=True,
    )

    @property
    def volle_naam(self):
        if self.jaar:
            return f"{self.jaar} {self.domein} - {self.naam}"
        else:
            return f"{self.domein} - {self.naam}"

    def __str__(self):
        return self.volle_naam

    def check_afsluiten(self):
        vrd_aantal = WijnVoorraad.objects.filter(wijn=self).aggregate(
            aantal=Sum("aantal")
        )
        if vrd_aantal["aantal"] is None:
            self.datumAfgesloten = datetime.now()
            self.save()
        elif self.datumAfgesloten:
            self.datumAfgesloten = None
            self.save()

    def check_unique(self):
        o = Wijn.objects.filter(naam=self.naam, domein=self.domein, jaar=self.jaar)
        if o:
            return False
        else:
            return True

    def create_copy(self):
        orig_wijn_id = self.id
        nieuwe_wijn = self
        nieuwe_wijn.pk = None
        nieuwe_wijn.datumAangemaakt = datetime.now()
        nieuwe_wijn.datumAfgesloten = None
        nieuwe_wijn.foto = None
        orig_naam = nieuwe_wijn.naam
        nieuwe_wijn.naam = orig_naam + " - Copy"
        copy_number = 0

        save_success = False
        while not save_success and copy_number < 15:
            if nieuwe_wijn.check_unique():
                nieuwe_wijn.save()
                save_success = True
            else:
                copy_number += 1
                nieuwe_wijn.naam = orig_naam + " - Copy" + str(copy_number)

        if save_success:
            orig_wijn = Wijn.objects.get(pk=orig_wijn_id)
            for i in orig_wijn.wijnDruivensoorten.all():
                s = WijnDruivensoort()
                s.wijn = nieuwe_wijn
                s.druivensoort = i
                s.save()
            return nieuwe_wijn.id
        else:
            raise ValidationError("Teveel kopieën reeds aanwezig")

    def check_fuzzy_selectie(self, fuzzy_selectie):
        voldoet = False
        if fuzzy_selectie:
            if fuzzy_selectie.lower() in self.naam.lower():
                voldoet = True
            elif fuzzy_selectie.lower() in self.domein.lower():
                voldoet = True
            elif fuzzy_selectie.lower() in self.wijnsoort.omschrijving.lower():
                voldoet = True
            elif fuzzy_selectie.lower() in str(self.jaar):
                voldoet = True
            elif fuzzy_selectie.lower() in self.land.lower():
                voldoet = True
            elif fuzzy_selectie.lower() in self.streek.lower():
                voldoet = True
            elif fuzzy_selectie.lower() in self.classificatie.lower():
                voldoet = True
            elif fuzzy_selectie.lower() in self.opmerking.lower():
                voldoet = True
            elif self.wijnDruivensoorten.filter(
                omschrijving__icontains=fuzzy_selectie
            ).exists():
                voldoet = True
        else:
            voldoet = True
        return voldoet

    class Meta:
        ordering = [F("jaar").asc(nulls_last=True), Lower("domein"), Lower("naam")]
        verbose_name_plural = "wijnen"
        constraints = [
            models.UniqueConstraint(
                name="unique_wijn",
                fields=["naam", "domein", "jaar"],
            )
        ]


class WijnDruivensoort(models.Model):
    """
    Model that links a Wijn (wine) to a DruivenSoort (grape variety).

    This through model enables a many-to-many relationship between wines and grape varieties,
    enforcing uniqueness for each (wijn, druivensoort) combination.
    """

    wijn = models.ForeignKey(Wijn, on_delete=models.CASCADE)
    druivensoort = models.ForeignKey(DruivenSoort, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.wijn.volle_naam} - {self.druivensoort.omschrijving}"

    class Meta:
        ordering = ["wijn", "druivensoort"]
        verbose_name_plural = "Wijn druivensoorten"
        constraints = [
            models.UniqueConstraint(
                name="unique_wijn_druivensoort",
                fields=["wijn", "druivensoort"],
            )
        ]


class Ontvangst(models.Model):
    deelnemer = models.ForeignKey(Deelnemer, on_delete=models.PROTECT)
    wijn = models.ForeignKey(Wijn, on_delete=models.PROTECT)
    datumOntvangst = models.DateField(default=date.today)
    leverancier = models.CharField(max_length=200, blank=True)
    website = models.URLField(max_length=200, blank=True)
    prijs = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    opmerking = models.CharField(max_length=4000, blank=True)

    def __str__(self):
        return f"{self.deelnemer.naam} - {self.wijn.volle_naam} - {self.datumOntvangst.strftime('%d-%m-%Y')}"

    def create_copy(self):
        # orig_ontvangst_id = self.id
        nieuwe_ontvangst = self
        nieuwe_ontvangst.pk = None
        nieuwe_ontvangst.datumOntvangst = datetime.now()
        nieuwe_ontvangst.save()
        return nieuwe_ontvangst.id

    def check_fuzzy_selectie(self, fuzzy_selectie):
        voldoet = False
        if fuzzy_selectie:
            if fuzzy_selectie.lower() in self.leverancier.lower():
                voldoet = True
            elif fuzzy_selectie.lower() in self.opmerking.lower():
                voldoet = True
            elif self.wijn.check_fuzzy_selectie(fuzzy_selectie):
                voldoet = True
        else:
            voldoet = True
        return voldoet

    class Meta:
        ordering = ["-datumOntvangst", "deelnemer", "wijn"]
        verbose_name_plural = "ontvangsten"


class VoorraadMutatie(models.Model):
    ontvangst = models.ForeignKey(Ontvangst, on_delete=models.PROTECT)
    locatie = models.ForeignKey(Locatie, on_delete=models.PROTECT)
    vak = models.ForeignKey(Vak, on_delete=models.PROTECT, null=True, blank=True)

    IN = "I"
    UIT = "U"
    in_uit_choices = [
        (IN, "In"),
        (UIT, "Uit"),
    ]
    in_uit = models.CharField(max_length=1, choices=in_uit_choices)

    KOOP = "K"
    ONTVANGST = "O"
    VERPLAATSING = "V"
    DRINK = "D"
    AFBOEKING = "A"
    actie_choices = [
        (KOOP, "Koop"),
        (ONTVANGST, "Ontvangst"),
        (VERPLAATSING, "Verplaatsing"),
        (DRINK, "Drink"),
        (AFBOEKING, "Afboeking"),
    ]
    actie = models.CharField(max_length=1, choices=actie_choices)

    datum = models.DateField()
    aantal = models.IntegerField()
    omschrijving = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return (
            f"{self.ontvangst.wijn.volle_naam} - "
            f"{self.ontvangst.deelnemer.naam} - "
            f"{self.in_uit} - "
            f"{self.datum.strftime('%d-%m-%Y')} - "
            f"{self.pk}"
        )

    def clean(self, *args, **kwargs):
        try:
            old_mutatie = VoorraadMutatie.objects.get(pk=self.pk)
        except VoorraadMutatie.DoesNotExist:
            old_mutatie = None
        WijnVoorraad.check_voorraad_wijziging(self, old_mutatie)
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        try:
            old_mutatie = VoorraadMutatie.objects.get(pk=self.pk)
        except VoorraadMutatie.DoesNotExist:
            old_mutatie = None
        super().save(*args, **kwargs)  # Call the "real" save() method.
        WijnVoorraad.Bijwerken(self, old_mutatie)

    def delete(self, *args, **kwargs):
        try:
            old_mutatie = VoorraadMutatie.objects.get(pk=self.pk)
        except VoorraadMutatie.DoesNotExist:
            old_mutatie = None
        WijnVoorraad.check_voorraad_wijziging(None, old_mutatie)
        WijnVoorraad.Bijwerken(None, old_mutatie)
        super().delete(*args, **kwargs)  # Call the "real" delete() method.

    def check_fuzzy_selectie(self, fuzzy_selectie):
        voldoet = False
        if fuzzy_selectie:
            if fuzzy_selectie.lower() in self.omschrijving.lower():
                voldoet = True
            elif self.ontvangst.check_fuzzy_selectie(fuzzy_selectie):
                voldoet = True
        else:
            voldoet = True
        return voldoet

    @staticmethod
    def drinken(ontvangst, locatie, vak=None):
        mutatie = VoorraadMutatie()
        mutatie.ontvangst = ontvangst
        mutatie.locatie = locatie
        if vak is not None:
            mutatie.vak = vak
        mutatie.in_uit = "U"
        mutatie.actie = "D"
        mutatie.datum = datetime.now()
        mutatie.aantal = 1
        mutatie.save()

    @staticmethod
    def voorraad_plus_1(ontvangst, locatie):
        mutatie = VoorraadMutatie()
        mutatie.ontvangst = ontvangst
        mutatie.locatie = locatie
        mutatie.in_uit = "I"
        mutatie.actie = "K"
        mutatie.datum = datetime.now()
        mutatie.aantal = 1
        mutatie.save()

    @staticmethod
    def verplaatsen(ontvangst, locatie_oud, vak_oud, locatie_nieuw, vak_nieuw, aantal):
        mutatie = VoorraadMutatie()
        mutatie.ontvangst = ontvangst
        mutatie.locatie = locatie_oud
        if vak_oud is not None:
            mutatie.vak = vak_oud
        mutatie.in_uit = "U"
        mutatie.actie = "V"
        mutatie.datum = datetime.now()
        mutatie.aantal = aantal
        mutatie.save()

        mutatie = VoorraadMutatie()
        mutatie.ontvangst = ontvangst
        mutatie.locatie = locatie_nieuw
        if vak_nieuw is not None:
            mutatie.vak = vak_nieuw
        mutatie.in_uit = "I"
        mutatie.actie = "V"
        mutatie.datum = datetime.now()
        mutatie.aantal = aantal
        mutatie.save()

    @staticmethod
    def afboeken(ontvangst, locatie, vak, aantal):
        mutatie = VoorraadMutatie()
        mutatie.ontvangst = ontvangst
        mutatie.locatie = locatie
        if vak is not None:
            mutatie.vak = vak
        mutatie.in_uit = "U"
        mutatie.actie = "A"
        mutatie.datum = datetime.now()
        mutatie.aantal = aantal
        mutatie.clean()
        mutatie.save()

    class Meta:
        verbose_name = "voorraadmutatie"
        verbose_name_plural = "voorraadmutaties"


class WijnVoorraadQuerySet(QuerySet, GroupByMixin):
    pass


# AIUsage model tostore the AI usage
class AIUsage(models.Model):
    """
    AIUsage model to track the usage of AI by users.
    Attributes:
        user (ForeignKey): Reference to the User model, with a PROTECT delete behavior.
        model (CharField): Name of the AI model used, with a maximum length of 200 characters.
        response_time (DateTimeField): Timestamp of when the AI response was generated.
        response_content (TextField): Content of the AI response.
        response_tokens_used (IntegerField): Number of tokens used in the AI response.
    Methods:
        __str__(): Returns a string representation of the AIUsage instance, combining the username and response time.
    """

    # pylint: disable=no-member

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    model = models.CharField(max_length=200)
    response_time = models.DateTimeField()
    response_content = models.TextField()
    response_tokens_used = models.IntegerField()

    def __str__(self):
        return (
            self.user.username
            + " - "
            + self.response_time.strftime("%d-%m-%Y %H:%M:%S")
        )


class Bestelling(models.Model):
    deelnemer = models.ForeignKey(Deelnemer, on_delete=models.PROTECT)
    datumAangemaakt = models.DateField(default=date.today)
    vanLocatie = models.ForeignKey(Locatie, on_delete=models.PROTECT)
    opmerking = models.CharField(max_length=4000, blank=True)
    datumAfgesloten = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s - %s - %s " % (
            self.deelnemer,
            self.datumAangemaakt.strftime("%d-%m-%Y"),
            self.vanLocatie,
        )

    def afboeken(self):
        br = BestellingRegel.objects.filter(
            bestelling=self, isVerzameld=True, verwerkt="N"
        )
        for regel in br:
            regel.afboeken()

    def check_afsluiten(self):
        br1 = BestellingRegel.objects.filter(bestelling=self, isVerzameld=False)
        br2 = BestellingRegel.objects.filter(bestelling=self, verwerkt="N")
        if br1.count() == 0 and br2.count() == 0:
            self.datumAfgesloten = datetime.now()
            self.save()
        elif self.datumAfgesloten:
            self.datumAfgesloten = None
            self.save()

    class Meta:
        ordering = ["-datumAangemaakt", "deelnemer", "vanLocatie"]
        verbose_name_plural = "bestellingen"


class BestellingRegel(models.Model):
    bestelling = models.ForeignKey(Bestelling, on_delete=models.PROTECT)
    ontvangst = models.ForeignKey(Ontvangst, on_delete=models.PROTECT)
    vak = models.ForeignKey(Vak, on_delete=models.PROTECT, null=True, blank=True)
    aantal = models.IntegerField(default=0)
    opmerking = models.CharField(max_length=4000, blank=True)
    isVerzameld = models.BooleanField(default=False)
    aantal_correctie = models.IntegerField(null=True, blank=True)

    NIET = "N"
    AFGEBOEKT = "A"
    VERPLAATST = "V"
    verwerkt_choices = [
        (NIET, ""),
        (AFGEBOEKT, "Afgeboekt"),
        (VERPLAATST, "Verplaatst"),
    ]
    verwerkt = models.CharField(max_length=1, default="N", choices=verwerkt_choices)

    def __str__(self):
        return "%s - %s " % (
            self.bestelling,
            self.ontvangst.wijn,
        )

    def clean(self, *args, **kwargs):
        try:
            old_regel = BestellingRegel.objects.get(pk=self.pk)
        except BestellingRegel.DoesNotExist:
            old_regel = None
        WijnVoorraad.check_voorraad_rsv(self, old_regel)
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        try:
            old_regel = BestellingRegel.objects.get(pk=self.pk)
        except BestellingRegel.DoesNotExist:
            old_regel = None
        super().save(*args, **kwargs)  # Call the "real" save() method.
        WijnVoorraad.Bijwerken_rsv(self, old_regel)
        self.bestelling.check_afsluiten()

    def delete(self, *args, **kwargs):
        bestelling = self.bestelling
        try:
            old_regel = BestellingRegel.objects.get(pk=self.pk)
        except BestellingRegel.DoesNotExist:
            old_regel = None

        WijnVoorraad.check_voorraad_rsv(None, old_regel)
        WijnVoorraad.Bijwerken_rsv(None, old_regel)
        super().delete(*args, **kwargs)  # Call the "real" delete() method.
        bestelling.check_afsluiten()

    def afboeken(self):
        if self.verwerkt == "N":
            if self.aantal_correctie is not None:
                aantal = self.aantal_correctie
            else:
                aantal = self.aantal
            if aantal > 0:
                VoorraadMutatie.afboeken(
                    self.ontvangst, self.bestelling.vanLocatie, self.vak, aantal
                )
            self.verwerkt = "A"
            self.save()

    def verplaatsen(self, locatie_nieuw, vak_nieuw, aantal, bijwerken=True):
        if self.verwerkt == "N":
            VoorraadMutatie.verplaatsen(
                self.ontvangst,
                self.bestelling.vanLocatie,
                self.vak,
                locatie_nieuw,
                vak_nieuw,
                aantal,
            )
            if bijwerken:
                self.verwerkt = "V"
                self.save()

    class Meta:
        ordering = ["bestelling", "ontvangst"]
        verbose_name_plural = "bestellingregels"
        constraints = [
            models.UniqueConstraint(
                name="unique_bestellingregel",
                fields=["bestelling", "ontvangst", "vak"],
                deferrable=Deferrable.DEFERRED,
            )
        ]


class WijnVoorraad(models.Model):
    objects = WijnVoorraadQuerySet.as_manager()
    wijn = models.ForeignKey(Wijn, on_delete=models.PROTECT)
    deelnemer = models.ForeignKey(Deelnemer, on_delete=models.PROTECT)
    ontvangst = models.ForeignKey(Ontvangst, on_delete=models.PROTECT)
    locatie = models.ForeignKey(Locatie, on_delete=models.PROTECT)
    vak = models.ForeignKey(Vak, on_delete=models.PROTECT, null=True, blank=True)
    aantal = models.IntegerField(default=0)
    aantal_rsv = models.IntegerField(default=0)

    def __str__(self):
        if self.vak:
            return "%s - %s - %s (%s)" % (
                self.wijn.volle_naam,
                self.deelnemer.naam,
                self.locatie.omschrijving,
                self.vak.code,
            )
        else:
            return "%s - %s - %s" % (
                self.wijn.volle_naam,
                self.deelnemer.naam,
                self.locatie.omschrijving,
            )

    def drinken(self):
        VoorraadMutatie.drinken(self.ontvangst, self.locatie, self.vak)

    def check_fuzzy_selectie(self, fuzzy_selectie):
        voldoet = False
        if fuzzy_selectie:
            if self.wijn.check_fuzzy_selectie(fuzzy_selectie):
                voldoet = True
            elif self.ontvangst.check_fuzzy_selectie(fuzzy_selectie):
                voldoet = True
        else:
            voldoet = True
        return voldoet

    @staticmethod
    def Bijwerken(new_mutatie, old_mutatie):
        if old_mutatie is not None:
            if old_mutatie.in_uit == "I":
                # de oude IN-boeking draaien we terug door deze te verwerken als UIT boeking
                WijnVoorraad.Bijwerken_mutatie_UIT(old_mutatie)
            else:
                # de oude UIT-boeking draaien we terug door deze te verwerken als IN boeking
                WijnVoorraad.Bijwerken_mutatie_IN(old_mutatie)

        if new_mutatie is not None:
            # Als er een nieuwe mutatie is: gewoon verwerken
            if new_mutatie.in_uit == "I":
                WijnVoorraad.Bijwerken_mutatie_IN(new_mutatie)
            else:
                WijnVoorraad.Bijwerken_mutatie_UIT(new_mutatie)

    @staticmethod
    def Bijwerken_mutatie_IN(mutatie: VoorraadMutatie):
        try:
            vrd = WijnVoorraad.objects.get(
                ontvangst=mutatie.ontvangst,
                locatie=mutatie.locatie,
                vak=mutatie.vak,
            )
            vrd.aantal = F("aantal") + mutatie.aantal
        except WijnVoorraad.DoesNotExist:
            vrd = WijnVoorraad(
                wijn=mutatie.ontvangst.wijn,
                deelnemer=mutatie.ontvangst.deelnemer,
                ontvangst=mutatie.ontvangst,
                locatie=mutatie.locatie,
                vak=mutatie.vak,
                aantal=mutatie.aantal,
            )
        vrd.save()
        vrd.refresh_from_db()
        wijn = vrd.wijn
        wijn.check_afsluiten()

    @staticmethod
    def Bijwerken_mutatie_UIT(mutatie: VoorraadMutatie):
        try:
            vrd = WijnVoorraad.objects.get(
                ontvangst=mutatie.ontvangst,
                locatie=mutatie.locatie,
                vak=mutatie.vak,
            )
            vrd.aantal = F("aantal") - mutatie.aantal
        except WijnVoorraad.DoesNotExist:
            vrd = WijnVoorraad(
                wijn=mutatie.ontvangst.wijn,
                deelnemer=mutatie.ontvangst.deelnemer,
                ontvangst=mutatie.ontvangst,
                locatie=mutatie.locatie,
                vak=mutatie.vak,
                aantal=-mutatie.aantal,
            )

        vrd.save()
        vrd.refresh_from_db()
        wijn = vrd.wijn
        if vrd.aantal == 0:
            vrd.delete()
        wijn.check_afsluiten()

    def verplaatsen(self, v_nieuwe_locatie, v_nieuwe_vak, v_aantal_verplaatsen):
        VoorraadMutatie.verplaatsen(
            self.ontvangst,
            self.locatie,
            self.vak,
            v_nieuwe_locatie,
            v_nieuwe_vak,
            v_aantal_verplaatsen,
        )

    @staticmethod
    def check_voorraad_wijziging(
        mutatie: VoorraadMutatie, old_mutatie: VoorraadMutatie
    ):
        if old_mutatie is not None:
            if old_mutatie.in_uit == "I":
                wijziging_aantal = old_mutatie.aantal * -1
            else:
                wijziging_aantal = old_mutatie.aantal
            try:
                vrd = WijnVoorraad.objects.get(
                    ontvangst=old_mutatie.ontvangst,
                    locatie=old_mutatie.locatie,
                    vak=old_mutatie.vak,
                )
                if vrd.aantal + wijziging_aantal < 0:
                    raise ValidationError(
                        ("Onjuiste mutatie. Hiermee wordt de voorraad negatief!")
                    )
            except WijnVoorraad.DoesNotExist as e:
                if wijziging_aantal < 0:
                    raise ValidationError(
                        ("Onjuiste mutatie. Hiermee wordt de voorraad negatief!")
                    ) from e

        if mutatie is not None:
            if mutatie.in_uit == "I":
                wijziging_aantal = mutatie.aantal
            else:
                wijziging_aantal = mutatie.aantal * -1
            try:
                vrd = WijnVoorraad.objects.get(
                    ontvangst=mutatie.ontvangst,
                    locatie=mutatie.locatie,
                    vak=mutatie.vak,
                )
                if vrd.aantal + wijziging_aantal < 0:
                    raise ValidationError(
                        ("Onjuiste mutatie. Hiermee wordt de voorraad negatief!")
                    )
            except WijnVoorraad.DoesNotExist as e:
                if wijziging_aantal < 0:
                    raise ValidationError(
                        ("Onjuiste mutatie. Hiermee wordt de voorraad negatief!")
                    ) from e

    @staticmethod
    def check_voorraad_rsv(bestelling_regel, old_regel):
        vrd_old = None
        vrd_new = None
        aantal_old = 0
        aantal_new = 0
        if old_regel is not None:
            if old_regel.aantal_correctie is not None:
                aantal_old = old_regel.aantal_correctie
            else:
                aantal_old = old_regel.aantal
            try:
                vrd_old = WijnVoorraad.objects.get(
                    ontvangst=old_regel.ontvangst,
                    locatie=old_regel.bestelling.vanLocatie,
                    vak=old_regel.vak,
                )
            except WijnVoorraad.DoesNotExist:
                aantal_old = 0
        if bestelling_regel is not None:
            if bestelling_regel.aantal_correctie is not None:
                aantal_new = bestelling_regel.aantal_correctie
            else:
                aantal_new = bestelling_regel.aantal
            try:
                vrd_new = WijnVoorraad.objects.get(
                    ontvangst=bestelling_regel.ontvangst,
                    locatie=bestelling_regel.bestelling.vanLocatie,
                    vak=bestelling_regel.vak,
                )
            except WijnVoorraad.DoesNotExist:
                aantal_new = 0

        if (
            old_regel is not None
            and bestelling_regel is not None
            and vrd_old is not None
            and vrd_new is not None
            and vrd_old == vrd_new
        ):
            if vrd_old.aantal_rsv - aantal_old + aantal_new > vrd_old.aantal:
                raise ValidationError(
                    ("Onjuiste bestelling. Er is niet voldoende voorraad!")
                )
        else:
            if old_regel is not None and vrd_old is not None:
                if vrd_old.aantal_rsv - aantal_old > vrd_old.aantal:
                    raise ValidationError(
                        ("Onjuiste bestelling. Er is niet voldoende voorraad!")
                    )
            if bestelling_regel is not None:
                if vrd_new is not None:
                    if vrd_new.aantal_rsv + aantal_new > vrd_new.aantal:
                        raise ValidationError(
                            ("Onjuiste bestelling. Er is niet voldoende voorraad!")
                        )
                else:
                    if aantal_new > 0:
                        raise ValidationError(
                            ("Onjuiste bestelling. Er is geen voorraad!")
                        )

    @staticmethod
    def Bijwerken_rsv(new_regel: BestellingRegel, old_regel: BestellingRegel):
        if old_regel is not None:
            if old_regel.verwerkt == "N":
                WijnVoorraad.Bijwerken_rsv_eraf(old_regel)

        if new_regel is not None:
            if new_regel.verwerkt == "N":
                WijnVoorraad.Bijwerken_rsv_erbij(new_regel)

    @staticmethod
    def Bijwerken_rsv_erbij(regel: BestellingRegel):
        try:
            vrd = WijnVoorraad.objects.get(
                ontvangst=regel.ontvangst,
                locatie=regel.bestelling.vanLocatie,
                vak=regel.vak,
            )
            if regel.aantal_correctie is not None:
                aantal = regel.aantal_correctie
            else:
                aantal = regel.aantal
            vrd.aantal_rsv = F("aantal_rsv") + aantal
            vrd.save()
        except WijnVoorraad.DoesNotExist as e:
            if regel.aantal_correctie is not None:
                aantal = regel.aantal_correctie
            else:
                aantal = regel.aantal
            if aantal > 0:
                raise ValidationError(
                    ("Onjuiste bestelling. Er is geen voorraad!")
                ) from e

    @staticmethod
    def Bijwerken_rsv_eraf(regel: BestellingRegel):
        try:
            vrd = WijnVoorraad.objects.get(
                ontvangst=regel.ontvangst,
                locatie=regel.bestelling.vanLocatie,
                vak=regel.vak,
            )
            if regel.aantal_correctie is not None:
                aantal = regel.aantal_correctie
            else:
                aantal = regel.aantal
            vrd.aantal_rsv = F("aantal_rsv") - aantal
            vrd.save()
        except WijnVoorraad.DoesNotExist:
            pass

    class Meta:
        ordering = ["wijn", "deelnemer", "locatie", "vak"]
        verbose_name = "Wijnvoorraad"
        verbose_name_plural = "wijnvoorraad"
        constraints = [
            models.UniqueConstraint(
                name="unique_wijnvoorraad",
                fields=["ontvangst", "locatie", "vak"],
            )
        ]
