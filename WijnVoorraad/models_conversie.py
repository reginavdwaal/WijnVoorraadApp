# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models import Deferrable

from WijnVoorraad.models import Deelnemer
from WijnVoorraad.models_oudwijn import OudDeelnemer


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
    aantal_gekoppeld = 0
    aantal_aangemaakt = 0
    for d_oud in te_conv_deelnemers():
        try:
            d_nieuw = Deelnemer.objects.get(naam=d_oud.naam)
            aantal_gekoppeld += 1
            if DoCommit:
                koppel_deelnemer_oud_nieuw(d_oud.id, d_nieuw.id)
        except:
            if InclAanmaken:
                d_nieuw = Deelnemer()
                d_nieuw.naam = d_oud.naam
                aantal_aangemaakt += 1
                if DoCommit:
                    d_nieuw.save()
    return (aantal_gekoppeld, aantal_aangemaakt)


# class ConvDruivensoort(models.Model):
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


# class ConvLocatie(models.Model):
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


# class ConvWijn(models.Model):
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
