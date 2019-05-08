# Generated by Django 2.0.5 on 2018-08-27 16:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warningre', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warningreceipt',
            name='last_updated_by',
        ),
        migrations.AlterField(
            model_name='warningreceipt',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
    ]
