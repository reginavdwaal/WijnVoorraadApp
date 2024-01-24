# Generated by Django 4.1.7 on 2023-07-25 20:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('WijnVoorraad', '0035_deelnemer_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deelnemer',
            name='users',
            field=models.ManyToManyField(related_name='deelnemers', related_query_name='deelnemer', to=settings.AUTH_USER_MODEL),
        ),
    ]