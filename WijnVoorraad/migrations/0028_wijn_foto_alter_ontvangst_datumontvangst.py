# Generated by Django 4.1.7 on 2023-06-10 16:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0027_alter_wijn_wijndruivensoorten'),
    ]

    operations = [
        migrations.AddField(
            model_name='wijn',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='ontvangst',
            name='datumOntvangst',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]