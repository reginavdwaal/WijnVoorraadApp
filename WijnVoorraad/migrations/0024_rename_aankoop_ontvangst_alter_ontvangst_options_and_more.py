# Generated by Django 4.1.7 on 2023-05-14 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0023_alter_voorraadmutatie_omschrijving'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Aankoop',
            new_name='Ontvangst',
        ),
        migrations.AlterModelOptions(
            name='ontvangst',
            options={'ordering': ['deelnemer', 'wijn', 'datumOntvangst'], 'verbose_name_plural': 'ontvangsten'},
        ),
        migrations.RenameField(
            model_name='ontvangst',
            old_name='datumAankoop',
            new_name='datumOntvangst',
        ),
        migrations.RenameField(
            model_name='voorraadmutatie',
            old_name='aankoop',
            new_name='ontvangst',
        ),
        migrations.AddField(
            model_name='wijnvoorraad',
            name='ontvangst',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='WijnVoorraad.ontvangst'),
        ),
        migrations.AlterField(
            model_name='voorraadmutatie',
            name='actie',
            field=models.CharField(choices=[('K', 'Koop'), ('O', 'Ontvangst'), ('V', 'Verplaatsing'), ('D', 'Drink')], max_length=1),
        ),
    ]
