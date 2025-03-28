# Generated by Django 4.1.7 on 2025-03-09 20:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('WijnVoorraad', '0058_alter_convvoorraadmutatie_id_oud'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(max_length=200)),
                ('response_time', models.DateTimeField()),
                ('response_content', models.TextField()),
                ('response_tokens_used', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
