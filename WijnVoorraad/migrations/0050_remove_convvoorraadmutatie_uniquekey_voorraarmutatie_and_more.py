# Generated by Django 4.1.7 on 2024-06-23 12:44

from django.db import migrations, models
import django.db.models.constraints


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0049_remove_convvoorraadmutatie_uniquekey_voorraarmutatie_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='convvoorraadmutatie',
            name='uniquekey_voorraarmutatie',
        ),
        migrations.AddConstraint(
            model_name='convvoorraadmutatie',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('id_wijn_oud', 'id_deelnemer_oud', 'id_locatie_oud', 'indicatie_in_uit_oud', 'datum_oud'), name='uniquekey_voorraadmutatie'),
        ),
    ]
