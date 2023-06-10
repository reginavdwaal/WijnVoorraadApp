# Generated by Django 4.1.7 on 2023-05-13 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0019_remove_voorraadmutatie_deelnemer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voorraadmutatie',
            name='aankoop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='WijnVoorraad.aankoop'),
        ),
        migrations.AlterField(
            model_name='voorraadmutatie',
            name='actie',
            field=models.CharField(choices=[('K', 'Koop'), ('V', 'Verplaatsing'), ('D', 'Drink')], max_length=1),
        ),
        migrations.AlterField(
            model_name='voorraadmutatie',
            name='voorraad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='WijnVoorraad.wijnvoorraad'),
        ),
    ]