# Generated by Django 4.1.7 on 2024-06-25 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0054_alter_convvoorraadmutatie_datum_oud'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='convvoorraadmutatie',
            options={'ordering': ['id_oud'], 'verbose_name_plural': 'Conv wijnen'},
        ),
        migrations.RemoveConstraint(
            model_name='convvoorraadmutatie',
            name='uniquekey_convvoorraadmutatie',
        ),
        migrations.RemoveField(
            model_name='convvoorraadmutatie',
            name='datum_oud',
        ),
        migrations.RemoveField(
            model_name='convvoorraadmutatie',
            name='id_deelnemer_oud',
        ),
        migrations.RemoveField(
            model_name='convvoorraadmutatie',
            name='id_locatie_oud',
        ),
        migrations.RemoveField(
            model_name='convvoorraadmutatie',
            name='id_wijn_oud',
        ),
        migrations.RemoveField(
            model_name='convvoorraadmutatie',
            name='indicatie_in_uit_oud',
        ),
        migrations.AddField(
            model_name='convvoorraadmutatie',
            name='id_oud',
            field=models.BigIntegerField(default=1, unique=True),
            preserve_default=False,
        ),
    ]
