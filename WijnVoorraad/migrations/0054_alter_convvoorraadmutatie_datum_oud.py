# Generated by Django 4.1.7 on 2024-06-23 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0053_alter_convwijndruivensoort_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convvoorraadmutatie',
            name='datum_oud',
            field=models.DateField(blank=True, null=True),
        ),
    ]
