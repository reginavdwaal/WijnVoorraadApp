# Generated by Django 4.1.7 on 2024-06-23 20:20

from django.db import migrations, models
import django.db.models.constraints


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0052_convvoorraadmutatie_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='convwijndruivensoort',
            options={'ordering': ['id_wijn_oud', 'id_druivensoort_oud'], 'verbose_name': 'Conv wijn druivensoort', 'verbose_name_plural': 'Conv wijn druivensoorten'},
        ),
        migrations.RemoveConstraint(
            model_name='convvoorraadmutatie',
            name='uniquekey_voorraadmutatie',
        ),
        migrations.RemoveConstraint(
            model_name='convwijndruivensoort',
            name='uniquekey',
        ),
        migrations.AddConstraint(
            model_name='convvoorraadmutatie',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('id_wijn_oud', 'id_deelnemer_oud', 'id_locatie_oud', 'indicatie_in_uit_oud', 'datum_oud'), name='uniquekey_convvoorraadmutatie'),
        ),
        migrations.AddConstraint(
            model_name='convwijndruivensoort',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('id_wijn_oud', 'id_druivensoort_oud'), name='uniquekey_convwijndruivensoort'),
        ),
    ]
