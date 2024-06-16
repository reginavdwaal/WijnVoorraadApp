# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models import Deferrable

from WijnVoorraad.models import Deelnemer, DruivenSoort, Locatie, Wijn, WijnSoort
from WijnVoorraad.models_oudwijn import (
    OudDeelnemer,
    OudDruivensoort,
    OudLocatie,
    OudWijn,
)


class ConvDeelnemer(models.Model):
    id_oud = models.BigIntegerField(unique=True)
    id_nieuw = models.BigIntegerField()

    def __str__(self):
        return "Oud %s - Nieuw %s" % (self.id_oud, self.id_nieuw)

    class Meta:
        ordering = ["id_oud"]


def te_conv_deelnemers():
    conv_ids = list(ConvDeelnemer.objects.all().values_list("id_oud", flat=True))
    ouddeelnemers = OudDeelnemer.objects.exclude(id__in=conv_ids)
    return ouddeelnemers


def koppel_deelnemer_oud_nieuw(id_oud, id_nieuw):
    koppel = ConvDeelnemer()
    koppel.id_oud = id_oud
    koppel.id_nieuw = id_nieuw
    koppel.save()


def converteer_deelnemers(InclAanmaken, DoCommit):
    convdata = init_conv(DoCommit)

    for d_oud in te_conv_deelnemers():
        try:
            d_nieuw = Deelnemer.objects.get(naam__iexact=d_oud.naam)
            convdata.aantal_gekoppeld += 1
            if DoCommit:
                koppel_deelnemer_oud_nieuw(d_oud.id, d_nieuw.id)
        except Deelnemer.DoesNotExist:
            if InclAanmaken:
                d_nieuw = Deelnemer()
                d_nieuw.naam = d_oud.naam
                convdata.aantal_aangemaakt += 1
                if DoCommit:
                    d_nieuw.save()
                    koppel_deelnemer_oud_nieuw(d_oud.id, d_nieuw.id)
    add_messages(DoCommit, convdata)
    return convdata


class ConvDruivenSoort(models.Model):
    id_oud = models.BigIntegerField(unique=True)
    id_nieuw = models.BigIntegerField()

    def __str__(self):
        return "Oud %s - Nieuw %s" % (self.id_oud, self.id_nieuw)

    class Meta:
        ordering = ["id_oud"]
        verbose_name = "Conv druivensoort"
        verbose_name_plural = "Conv druivensoorten"


def te_conv_druivensoorten():
    conv_ids = list(ConvDruivenSoort.objects.all().values_list("id_oud", flat=True))
    ouddruivensoorten = OudDruivensoort.objects.exclude(id__in=conv_ids)
    return ouddruivensoorten


def koppel_druivensoort_oud_nieuw(id_oud, id_nieuw):
    koppel = ConvDruivenSoort()
    koppel.id_oud = id_oud
    koppel.id_nieuw = id_nieuw
    koppel.save()


def converteer_druivensoorten(InclAanmaken, DoCommit):
    convdata = init_conv(DoCommit)

    for d_oud in te_conv_druivensoorten():
        try:
            d_nieuw = DruivenSoort.objects.get(omschrijving__iexact=d_oud.omschrijving)
            convdata.aantal_gekoppeld += 1
            if DoCommit:
                koppel_druivensoort_oud_nieuw(d_oud.id, d_nieuw.id)
        except DruivenSoort.DoesNotExist:
            if InclAanmaken:
                d_nieuw = DruivenSoort()
                d_nieuw.omschrijving = d_oud.omschrijving
                convdata.aantal_aangemaakt += 1
                if DoCommit:
                    d_nieuw.save()
                    koppel_druivensoort_oud_nieuw(d_oud.id, d_nieuw.id)
    add_messages(DoCommit, convdata)
    return convdata


class ConvLocatie(models.Model):
    id_oud = models.BigIntegerField(unique=True)
    id_nieuw = models.BigIntegerField()

    def __str__(self):
        return "Oud %s - Nieuw %s" % (self.id_oud, self.id_nieuw)

    class Meta:
        ordering = ["id_oud"]


def te_conv_locaties():
    conv_ids = list(ConvLocatie.objects.all().values_list("id_oud", flat=True))
    oudlocaties = OudLocatie.objects.exclude(id__in=conv_ids)
    return oudlocaties


def koppel_locatie_oud_nieuw(id_oud, id_nieuw):
    koppel = ConvLocatie()
    koppel.id_oud = id_oud
    koppel.id_nieuw = id_nieuw
    koppel.save()


def converteer_locaties(InclAanmaken, DoCommit):
    convdata = init_conv(DoCommit)

    for d_oud in te_conv_locaties():
        try:
            d_nieuw = Locatie.objects.get(omschrijving__iexact=d_oud.omschrijving)
            convdata.aantal_gekoppeld += 1
            if DoCommit:
                koppel_locatie_oud_nieuw(d_oud.id, d_nieuw.id)
        except Locatie.DoesNotExist:
            if InclAanmaken:
                d_nieuw = Locatie()
                d_nieuw.omschrijving = d_oud.omschrijving
                convdata.aantal_aangemaakt += 1
                if DoCommit:
                    d_nieuw.save()
                    koppel_locatie_oud_nieuw(d_oud.id, d_nieuw.id)
    add_messages(DoCommit, convdata)
    return convdata


class ConvWijn(models.Model):
    id_oud = models.BigIntegerField(unique=True)
    id_nieuw = models.BigIntegerField()

    def __str__(self):
        return "Oud %s - Nieuw %s" % (self.id_oud, self.id_nieuw)

    class Meta:
        ordering = ["id_oud"]
        verbose_name_plural = "Conv wijnen"


def te_conv_wijnen():
    conv_ids = list(ConvWijn.objects.all().values_list("id_oud", flat=True))
    oudwijnen = OudWijn.objects.exclude(id__in=conv_ids)
    return oudwijnen


def koppel_wijn_oud_nieuw(id_oud, id_nieuw):
    koppel = ConvWijn()
    koppel.id_oud = id_oud
    koppel.id_nieuw = id_nieuw
    koppel.save()


def converteer_wijnen(InclAanmaken, DoCommit):
    convdata = init_conv(DoCommit)

    for w_oud in te_conv_wijnen():
        try:
            w_nieuw = Wijn.objects.get(
                domein__iexact=w_oud.domein, naam__iexact=w_oud.naam, jaar=w_oud.jaar
            )
            convdata.aantal_gekoppeld += 1
            if DoCommit:
                koppel_wijn_oud_nieuw(w_oud.id, w_nieuw.id)
        except Wijn.DoesNotExist:
            if InclAanmaken:
                try:
                    wijnsoort = WijnSoort.objects.get(omschrijving__iexact=w_oud.kleur)
                    naam_nieuw = w_oud.naam.replace(str(w_oud.jaar), "").strip()
                    w_nieuw = Wijn()
                    w_nieuw.domein = w_oud.domein
                    w_nieuw.naam = naam_nieuw
                    w_nieuw.wijnsoort = wijnsoort
                    w_nieuw.jaar = w_oud.jaar
                    w_nieuw.land = w_oud.land
                    w_nieuw.streek = w_oud.streek
                    w_nieuw.classificatie = w_oud.classificatie
                    w_nieuw.website = w_oud.url
                    w_nieuw.opmerking = w_oud.opmerkingen

                    convdata.aantal_aangemaakt += 1
                    if DoCommit:
                        w_nieuw.save()
                        koppel_wijn_oud_nieuw(w_oud.id, w_nieuw.id)
                except WijnSoort.DoesNotExist:
                    convdata.aantal_fouten += 1
                    convdata.message_list.append(
                        f"Wijnsoort (kleur) onbekend. Id oud {w_oud.id}"
                    )
    add_messages(DoCommit, convdata)
    return convdata


class ConvData:
    def __init__(self):
        self.aantal_gekoppeld = 0
        self.aantal_aangemaakt = 0
        self.aantal_fouten = 0
        self.message_list = []


def init_conv(DoCommit):
    convdata = ConvData()
    if DoCommit:
        convdata.message_list.append("CONVERSIE: ")
    else:
        convdata.message_list.append("PROEFCONVERSIE: ")
    return convdata


def add_messages(DoCommit, convdata):
    if DoCommit:
        convdata.message_list.append(f"Aantal gekoppeld {convdata.aantal_gekoppeld}.")
        if convdata.aantal_aangemaakt > 0:
            convdata.message_list.append(
                f"Aantal aangemaakt {convdata.aantal_aangemaakt}."
            )
        else:
            convdata.message_list.append("Geen aangemaakt.")
        if convdata.aantal_fouten > 0:
            convdata.message_list.append(f"Aantal fouten {convdata.aantal_fouten}.")
    else:
        convdata.message_list.append(f"Aantal te koppelen {convdata.aantal_gekoppeld}.")
        if convdata.aantal_aangemaakt > 0:
            convdata.message_list.append(
                f"Aantal aan te maken {convdata.aantal_aangemaakt}."
            )
        if convdata.aantal_fouten > 0:
            convdata.message_list.append(f"Aantal fouten {convdata.aantal_fouten}.")


# class ConvFoto(models.Model):
#     id_oud = models.BigIntegerField()
#     id_nieuw = models.BigIntegerField()

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 name="uniquekey",
#                 fields=["id_oud", "id_nieuw"],
#                 deferrable=Deferrable.DEFERRED,
#             )
#         ]


# class ConvKeynumber(models.Model):
#     keyname_oud = models.CharField(max_length=20)
#     id_nieuw = models.BigIntegerField()

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 name="uniquekey",
#                 fields=["keyname_oud", "id_nieuw"],
#                 deferrable=Deferrable.DEFERRED,
#             )
#         ]


# class ConvProefnotitie(models.Model):
#     id_oud = models.BigIntegerField()
#     id_nieuw = models.BigIntegerField()

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 name="uniquekey",
#                 fields=["id_oud", "id_nieuw"],
#                 deferrable=Deferrable.DEFERRED,
#             )
#         ]


# class ConvVoorraadmutatie(models.Model):
#     id_oud = models.BigIntegerField()
#     id_nieuw = models.BigIntegerField()

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 name="uniquekey",
#                 fields=["id_oud", "id_nieuw"],
#                 deferrable=Deferrable.DEFERRED,
#             )
#         ]


# class ConvWijnDruivensoort(models.Model):
#     id_wijn_oud = models.IntegerField()
#     id_druivensoort_oud = models.IntegerField()
#     id_nieuw = models.BigIntegerField()

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 name="uniquekey",
#                 fields=["id_wijn_oud", "id_druivensoort_oud", "id_nieuw"],
#                 deferrable=Deferrable.DEFERRED,
#             )
#         ]
