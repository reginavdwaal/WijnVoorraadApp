# Generated by Django 4.1.7 on 2025-04-23 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0062_bestellingregel_unique_bestellingregel'),
    ]

    operations = [
        migrations.AddField(
            model_name='wijnvoorraad',
            name='aantal_rsv',
            field=models.IntegerField(default=0),
        ),
    ]
