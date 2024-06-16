# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class OudDeelnemer(models.Model):
    naam = models.CharField(unique=True, max_length=35)

    class Meta:
        managed = False
        db_table = "deelnemer"
        app_label = "ouddb"


class OudDruivensoort(models.Model):
    omschrijving = models.CharField(unique=True, max_length=20)

    class Meta:
        managed = False
        db_table = "druivensoort"
        app_label = "ouddb"


class OudFoto(models.Model):
    datum_gemaakt = models.DateField(blank=True, null=True)
    filenaam = models.CharField(max_length=100)
    omschrijving = models.CharField(max_length=255, blank=True, null=True)
    rotated_jn = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "foto"
        app_label = "ouddb"


class OudKeynumber(models.Model):
    keyname = models.CharField(primary_key=True, max_length=20)
    value = models.DecimalField(max_digits=8, decimal_places=0)

    class Meta:
        managed = False
        db_table = "keynumber"
        app_label = "ouddb"


class OudLocatie(models.Model):
    omschrijving = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "locatie"
        app_label = "ouddb"


class OudProefnotitie(models.Model):
    id_wijn = models.IntegerField()
    datum = models.DateField()
    id_deelnemer = models.IntegerField()
    proefnotitie = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "proefnotitie"
        app_label = "ouddb"


class OudVoorraadmutatie(models.Model):
    id_wijn = models.IntegerField()
    id_deelnemer = models.IntegerField()
    id_locatie = models.IntegerField()
    indicatie_in_uit = models.CharField(max_length=1)
    datum = models.DateField()
    aantal = models.IntegerField()
    omschrijving = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "voorraadmutatie"
        unique_together = (
            ("id_wijn", "id_deelnemer", "id_locatie", "indicatie_in_uit", "datum"),
        )
        app_label = "ouddb"


class OudWijn(models.Model):
    naam = models.CharField(unique=True, max_length=100)
    kleur = models.CharField(max_length=20)
    jaar = models.IntegerField()
    land = models.CharField(max_length=20, blank=True, null=True)
    streek = models.CharField(max_length=50, blank=True, null=True)
    domein = models.CharField(max_length=50, blank=True, null=True)
    classificatie = models.CharField(max_length=50, blank=True, null=True)
    leverancier = models.CharField(max_length=50, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    opmerkingen = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "wijn"
        app_label = "ouddb"


class OudWijnDruivensoort(models.Model):
    id_wijn = models.IntegerField(primary_key=True)
    id_druivensoort = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = "wijn_druivensoort"
        unique_together = (("id_wijn", "id_druivensoort"),)
        app_label = "ouddb"
