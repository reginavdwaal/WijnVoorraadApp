# Generated by Django 4.1.7 on 2024-06-18 18:58

from django.db import migrations, models
import django.db.models.constraints


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0046_convwijn_alter_convdruivensoort_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConvWijnDruivensoort',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_wijn_oud', models.BigIntegerField()),
                ('id_druivensoort_oud', models.BigIntegerField()),
                ('id_nieuw', models.BigIntegerField()),
            ],
            options={
                'ordering': ['id_wijn_oud', 'id_druivensoort_oud'],
            },
        ),
        migrations.AlterModelOptions(
            name='convwijn',
            options={'ordering': ['id_oud'], 'verbose_name_plural': 'Conv wijnen'},
        ),
        migrations.AddConstraint(
            model_name='convwijndruivensoort',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('id_wijn_oud', 'id_druivensoort_oud'), name='uniquekey'),
        ),
    ]
