# Generated by Django 4.1.7 on 2024-06-23 19:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0050_remove_convvoorraadmutatie_uniquekey_voorraarmutatie_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ConvVoorraadmutatie',
        ),
    ]
