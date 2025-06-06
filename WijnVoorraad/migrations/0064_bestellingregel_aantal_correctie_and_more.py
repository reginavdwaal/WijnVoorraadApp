# Generated by Django 4.1.7 on 2025-04-29 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0063_wijnvoorraad_aantal_rsv'),
    ]

    operations = [
        migrations.AddField(
            model_name='bestellingregel',
            name='aantal_correctie',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='bestellingregel',
            name='isVerzameld',
            field=models.BooleanField(default=False),
        ),
    ]
