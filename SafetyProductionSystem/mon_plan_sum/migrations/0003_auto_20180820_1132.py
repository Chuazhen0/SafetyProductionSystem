# Generated by Django 2.0.5 on 2018-08-20 11:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mon_plan_sum', '0002_auto_20180806_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monplansum',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
    ]
