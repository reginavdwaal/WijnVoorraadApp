# Generated by Django 4.1.7 on 2024-04-23 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0036_alter_deelnemer_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='locatie',
            name='aantal_kolommen',
            field=models.IntegerField(default=1),
        ),
    ]
