# Generated by Django 2.0.5 on 2018-08-08 10:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myform', '0006_auto_20180806_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myform',
            name='created_at',
            field=models.DateField(default=datetime.datetime(2018, 8, 8, 10, 12, 37, 1920), verbose_name='创建时间'),
        ),
    ]
