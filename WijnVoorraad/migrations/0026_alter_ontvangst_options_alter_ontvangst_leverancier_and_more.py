# Generated by Django 4.1.7 on 2023-06-09 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0025_ontvangst_prijs_alter_wijnvoorraad_ontvangst'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ontvangst',
            options={'ordering': ['-datumOntvangst', 'deelnemer', 'wijn'], 'verbose_name_plural': 'ontvangsten'},
        ),
        migrations.AlterField(
            model_name='ontvangst',
            name='leverancier',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ontvangst',
            name='opmerking',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ontvangst',
            name='website',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='voorraadmutatie',
            name='omschrijving',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wijn',
            name='classificatie',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wijn',
            name='land',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wijn',
            name='leverancier',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wijn',
            name='opmerking',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wijn',
            name='streek',
            field=models.CharField(blank=True, default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='wijn',
            name='website',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
    ]