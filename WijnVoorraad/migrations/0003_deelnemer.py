# Generated by Django 4.1.7 on 2023-04-07 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WijnVoorraad', '0002_druivensoort_alter_wijnsoort_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deelnemer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naam', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['naam'],
            },
        ),
    ]
