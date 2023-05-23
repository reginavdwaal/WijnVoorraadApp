from django.db import models
from django.db.models import Deferrable, UniqueConstraint
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import F

# Create your models here.


class WijnSoort(models.Model):
    omschrijving = models.CharField(max_length=200)

    def __str__(self):
        return self.omschrijving

    class Meta:
        ordering = ["omschrijving"]
        verbose_name = "wijnsoort"
        verbose_name_plural = "wijnsoorten"


class DruivenSoort(models.Model):
    omschrijving = models.CharField(max_length=200)

    def __str__(self):
        return self.omschrijving

    class Meta:
        ordering = ["omschrijving"]
        verbose_name = "druivensoort"
        verbose_name_plural = "druivensoorten"


class Locatie(models.Model):
    omschrijving = models.CharField(max_length=200)

    def __str__(self):
        return self.omschrijving

    class Meta:
        ordering = ["omschrijving"]


class Vak(models.Model):
    locatie = models.ForeignKey(Locatie, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    capaciteit = models.IntegerField(default=1)

    def __str__(self):
        return "%s (%s)" % (self.locatie.omschrijving, self.code)

    class Meta:
        ordering = ["locatie", "code"]
        verbose_name_plural = "vakken"
        constraints = [
            models.UniqueConstraint(
                name="unique_code_binnen_locatie",
                fields=["locatie", "code"],
                deferrable=Deferrable.DEFERRED,
            )
        ]


class Deelnemer(models.Model):
    naam = models.CharField(max_length=200)
    standaardLocatie = models.ForeignKey(
        Locatie, on_delete=models.SET_NULL, blank=True, null=True
    )
    users = models.ManyToManyField(
        User,
        through="DeelnemerUser",
        through_fields=("deelnemer", "user"),
    )

    def __str__(self):
        return self.naam

    class Meta:
        ordering = ["naam"]


class DeelnemerUser(models.Model):
    deelnemer = models.ForeignKey(Deelnemer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.deelnemer.naam, self.user.username)

    class Meta:
        ordering = ["deelnemer", "user"]
        verbose_name_plural = "Deelnemer users"
        constraints = [
            models.UniqueConstraint(
                name="unique_deelnemer_user",
                fields=["deelnemer", "user"],
                deferrable=Deferrable.DEFERRED,
            )
        ]

class Wijn(models.Model):
    naam = models.CharField(max_length=200)
    domein = models.CharField(max_length=200)
    wijnsoort = models.ForeignKey(WijnSoort, on_delete=models.PROTECT)

    def validate_jaartal(jaartal):
        if not (1900 < jaartal < 2500):
            raise ValidationError(
                (
                    "%(jaartal)s is geen geldig jaartal. Het jaartal moet liggen tussen 1901 en 2499"
                ),
                params={"jaartal": jaartal},
            )

    jaar = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_jaartal]
    )
    land = models.CharField(max_length=200, null=True, blank=True)
    streek = models.CharField(max_length=200, null=True, blank=True)
    classificatie = models.CharField(max_length=200, null=True, blank=True)
    leverancier = models.CharField(max_length=200, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    opmerking = models.CharField(max_length=200, null=True, blank=True)
    #    foto = models.ImageField(null=True, blank=True)
    datumAangemaakt = models.DateTimeField(auto_now_add=True)
    datumAfgesloten = models.DateTimeField(null=True, blank=True)

    wijnDruivensoorten = models.ManyToManyField(
        DruivenSoort,
        through="WijnDruivensoort",
        through_fields=("wijn", "druivensoort"),
    )

    def __str__(self):
        return "%s - %s" % (self.naam, self.domein)

    class Meta:
        ordering = ["naam"]
        verbose_name_plural = "wijnen"
        constraints = [
            models.UniqueConstraint(
                name="unique_wijn",
                fields=["naam", "domein"],
                deferrable=Deferrable.DEFERRED,
            )
        ]

class WijnDruivensoort(models.Model):
    wijn = models.ForeignKey(Wijn, on_delete=models.PROTECT)
    druivensoort = models.ForeignKey(DruivenSoort, on_delete=models.PROTECT)

    def __str__(self):
        return "%s - %s" % (self.wijn.naam, self.druivensoort.omschrijving)

    class Meta:
        ordering = ["wijn", "druivensoort"]
        verbose_name_plural = "Wijn druivensoorten"
        constraints = [
            models.UniqueConstraint(
                name="unique_wijn_druivensoort",
                fields=["wijn", "druivensoort"],
                deferrable=Deferrable.DEFERRED,
            )
        ]

class Ontvangst(models.Model):
    deelnemer = models.ForeignKey(Deelnemer, on_delete=models.PROTECT)
    wijn = models.ForeignKey(Wijn, on_delete=models.PROTECT)
    datumOntvangst = models.DateField()
    leverancier = models.CharField(max_length=200, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    prijs = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    opmerking = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "%s - %s - %s " % (self.deelnemer.naam, self.wijn.naam, self.datumOntvangst.strftime("%d-%m-%Y"))

    class Meta:
        ordering = ["deelnemer", "wijn", "datumOntvangst"]
        verbose_name_plural = "ontvangsten"

class WijnVoorraad(models.Model):
    wijn = models.ForeignKey(Wijn, on_delete=models.PROTECT)
    deelnemer = models.ForeignKey(Deelnemer, on_delete=models.PROTECT)
    ontvangst = models.ForeignKey(Ontvangst, on_delete=models.PROTECT)
    locatie = models.ForeignKey(Locatie, on_delete=models.PROTECT)
    vak = models.ForeignKey(Vak, on_delete=models.PROTECT, null=True, blank=True)
    aantal = models.IntegerField(default=0)

    def __str__(self):
        if self.vak:
            return "%s - %s - %s (%s)" % (
                self.wijn.naam,
                self.deelnemer.naam,
                self.locatie.omschrijving,
                self.vak.code,
            )
        else:
            return "%s - %s - %s" % (
                self.wijn.naam,
                self.deelnemer.naam,
                self.locatie.omschrijving,
            )
        
    def Bijwerken (VoorraadMutatie, old_mutatie):
        if old_mutatie is not None:
            if old_mutatie.in_uit == VoorraadMutatie.IN:
                # de oude IN-boeking draaien we terug door deze te verwerken als UIT boeking
                WijnVoorraad.Bijwerken_mutatie_UIT(old_mutatie)
            else:
                # de oude UIT-boeking draaien we terug door deze te verwerken als IN boeking
                WijnVoorraad.Bijwerken_mutatie_IN(old_mutatie)

        # En dan nu de nieuwe mutatie gewoon verwerken
        if VoorraadMutatie.in_uit == VoorraadMutatie.IN:
            WijnVoorraad.Bijwerken_mutatie_IN(VoorraadMutatie)
        else:
            WijnVoorraad.Bijwerken_mutatie_UIT(VoorraadMutatie)

    def Bijwerken_mutatie_IN (VoorraadMutatie):
        try:
            vrd = WijnVoorraad.objects.get ( ontvangst=VoorraadMutatie.ontvangst
                                            , locatie=VoorraadMutatie.locatie
                                            , vak=VoorraadMutatie.vak)
            vrd.aantal=F('aantal') + VoorraadMutatie.aantal
            vrd.save()
        except WijnVoorraad.DoesNotExist:
            vrd = WijnVoorraad(wijn=VoorraadMutatie.ontvangst.wijn
                               , deelnemer=VoorraadMutatie.ontvangst.deelnemer
                               , ontvangst=VoorraadMutatie.ontvangst
                               , locatie = VoorraadMutatie.locatie
                               , vak=VoorraadMutatie.vak
                               , aantal=VoorraadMutatie.aantal)
            vrd.save()

    def Bijwerken_mutatie_UIT (VoorraadMutatie):
        vrd = WijnVoorraad.objects.get ( ontvangst=VoorraadMutatie.ontvangst
                                       , locatie=VoorraadMutatie.locatie
                                       , vak=VoorraadMutatie.vak)
        vrd.aantal=F('aantal') - VoorraadMutatie.aantal
        vrd.save()

    class Meta:
        ordering = ["wijn", "deelnemer", "locatie", "vak"]
        verbose_name = "Wijnvoorraad"
        verbose_name_plural = "wijnvoorraad"
        constraints = [
            models.UniqueConstraint(
                name="unique_wijnvoorraad",
                fields=["wijn", "deelnemer", "locatie", "vak"],
                deferrable=Deferrable.DEFERRED,
            )
        ]

class VoorraadMutatie(models.Model):
    ontvangst = models.ForeignKey(Ontvangst, on_delete=models.CASCADE)
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
    actie_choices = [
        (KOOP, "Koop"),
        (ONTVANGST, "Ontvangst"),
        (VERPLAATSING, "Verplaatsing"),
        (DRINK, "Drink")
    ]
    actie = models.CharField(max_length=1, choices=actie_choices)
    
    datum = models.DateField()
    aantal = models.IntegerField()
    omschrijving = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "%s - %s - %s - %s" % (
            self.ontvangst.wijn.naam,
            self.ontvangst.deelnemer.naam,
            self.in_uit,
            self.datum.strftime("%d-%m-%Y"),
        )
    
    def save(self, *args, **kwargs):
        try:
            old_mutatie = VoorraadMutatie.objects.get(pk=self.pk)
        except:
            old_mutatie = None
    
        super().save(*args, **kwargs)  # Call the "real" save() method.
        WijnVoorraad.Bijwerken (self, old_mutatie)

    class Meta:
        verbose_name = "voorraadmutatie"
        verbose_name_plural = "voorraadmutaties"
