# Generated by Django 2.0.5 on 2018-08-20 16:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yearsum', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yearsum',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
    ]
